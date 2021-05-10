from collections import defaultdict
from dataclasses import dataclass
import builtins
import functools
import io
import os
import sys
import yaml
import getopt
import traceback


@dataclass
class Directive:
    kind: str
    type: str
    name: str
    body: str


PARAM_KINDS = ['param', 'parameter', 'arg', 'argument']
QUERY_KINDS = ['queryparameter', 'queryparam', 'qparam', 'query']
FORM_KINDS = ['formparameter', 'formparam', 'fparam', 'form']
JSON_KINDS = ['jsonparameter', 'jsonparam', 'json']
REQJSON_KINDS = ['reqjsonobj', 'reqjson', '<jsonobj', '<json']
RESJSON_KINDS = ['resjsonobj', 'resjson', '>jsonobj', '>json']
REQJSONARR_KINDS = ['reqjsonarr', '<jsonarr']
RESJSONARR_KINDS = ['resjsonarr', '>jsonarr']
REQHEADER_KINDS = ['requestheader', 'reqheader', '>header']
RESHEADER_KINDS = ['responseheader', 'resheader', '<header']
STATUS_KINDS = ['statuscode', 'status', 'code']


def prepare_docstring(s, tabsize=4):
    """
    Convert a docstring into lines of parseable reST.  Remove common leading
    indentation, where the indentation of a given number of lines (usually just
    one) is ignored.

    Return the docstring as a list of lines usable for inserting into a docutils
    ViewList (used as argument of nested_parse().)  An empty line is added to
    act as a separator between this docstring and following content.

    NOTE: This function is from Sphinx.
    """
    # NOTE: Do we really want to ignore indentation of the first line?
    ignore = 1
    lines = s.expandtabs(tabsize).splitlines()
    # Find minimum indentation of any non-blank lines after ignored lines.
    margin = sys.maxsize
    for line in lines[ignore:]:
        content = len(line.lstrip())
        if content:
            indent = len(line) - content
            margin = min(margin, indent)
    # Remove indentation from ignored lines.
    for i in range(ignore):
        if i < len(lines):
            lines[i] = lines[i].lstrip()
    if margin < sys.maxsize:
        for i in range(ignore, len(lines)):
            lines[i] = lines[i][margin:]
    # Remove any leading blank lines.
    while lines and not lines[0]:
        lines.pop(0)
    # make sure there is an empty line at the end
    if lines and lines[-1]:
        lines.append('')
    return lines


def import_object(import_name):
    module_name, expr = import_name.split(':', 1)
    mod = __import__(module_name)
    mod = functools.reduce(getattr, module_name.split('.')[1:], mod)
    globals = builtins
    if not isinstance(globals, dict):
        globals = globals.__dict__
    return eval(expr, globals, mod.__dict__)


def clean_up_methods(methods):
    autoadded_methods = frozenset(['OPTIONS', 'HEAD'])
    if methods <= autoadded_methods:
        return methods
    return methods.difference(autoadded_methods)


def get_routes(app):
    endpoints = []

    for rule in app.url_map.iter_rules():
        url = str(next(app.url_map.iter_rules(rule.endpoint)))

        # Exclude static endpoint
        static_url_path = app.static_url_path
        if rule.endpoint == 'static' and url.startswith(static_url_path):
            continue

        url_with_endpoint = (url, rule.endpoint)
        if url_with_endpoint not in endpoints:
            endpoints.append(url_with_endpoint)

    endpoints.sort()

    unique_view_fn_names = [e for _, e in endpoints]

    for view_fn_name in unique_view_fn_names:
        methodrules = defaultdict(list)
        for rule in app.url_map.iter_rules(view_fn_name):
            path = rule.rule
            for method in clean_up_methods(rule.methods):
                methodrules[method].append(path)
        for method, paths in methodrules.items():
            view_fn = app.view_functions[view_fn_name]
            view_docstring = view_fn.__doc__
            yield method, paths, view_fn_name, view_docstring


def print_usage_and_exit():
    print('''
        Usage: python httpdomain-to-openapi.py --app <flask_app_import_name> --title <title_for_documentation> --version <version_for_documentation>
            e.g python httpdomain-to-openapi.py --app my_app:app --title '50 Five' --version v5.25.0
    ''')
    sys.exit(1)


def remove_start_and_end_empty_strings(lines):
    if len(lines) == 0:
        return lines
    while len(lines[0]) == 0:
        lines.pop(0)
    while len(lines[-1]) == 0:
        lines.pop(-1)
    return lines


def split_list_by_function(l, func):
    """
    For each item in l, if func(l) is truthy, func(l) will be added to l1.
    Otherwise, l will be added to l2.
    """
    l1 = []
    l2 = []
    for item in l:
        res = func(item)
        if res:
            l1.append(res)
        else:
            l2.append(item)
    return l1, l2


def parse_directive(directive_line):
    first_colon = directive_line.find(':')
    second_colon = directive_line.find(':', first_colon + 1)

    if first_colon != 0 or second_colon is None:
        return None

    # If we don't have a type, just default it to string
    type = 'string'

    head = directive_line[first_colon + 1:second_colon]
    head_parts = head.split(' ')

    if len(head_parts) == 2:
        kind, name = head_parts
    elif len(head_parts) == 3:
        kind, type, name = head_parts
    else:
        return None

    body = directive_line[second_colon + 1:].strip()

    directive = Directive(
        kind=kind,
        type=type,
        name=name,
        body=body
    )

    return directive


def add_directive_to_openapi_operation(operation, directive):
    if directive.kind in PARAM_KINDS:
        value = {
            'name': directive.name,
            'in': 'path',
            'description': directive.body,
            'required': True,
            'schema': {
                'type': directive.type,
            },
        }
        operation\
            .setdefault('parameters', [])\
            .append(value)
        return operation

    elif directive.kind in QUERY_KINDS:
        value = {
            'name': directive.name,
            'in': 'query',
            'description': directive.body,
            'schema': {
                'type': directive.type,
            },
        }
        operation\
            .setdefault('parameters', [])\
            .append(value)
        return operation

    elif directive.kind in FORM_KINDS:
        # NOTE: We are defaulting to a Content-Type of multipart/form-data.
        #
        # However, this could just as well be application/x-www-form-urlencoded!
        # We need to somehow handle this.
        #
        # The slight snag here is that the httpdomain syntax doesn't seem
        # to distinguish between the two. We could add it as a separate header,
        # true, but then it would be a bit annoying to parse, since we would
        # have to make a special case in the REQ_HEADER section, then parse
        # that first and so on…
        operation\
            .setdefault('requestBody', {})\
            .setdefault('content', {})\
            .setdefault('multipart/form-data', {})\
            .setdefault('schema', {'type': 'object'})\
            .setdefault('properties', {})\
            [directive.name] = {'type': directive.type}
        return operation

    elif directive.kind in JSON_KINDS or directive.kind in REQJSON_KINDS:
        operation\
            .setdefault('requestBody', {})\
            .setdefault('content', {})\
            .setdefault('application/json', {})\
            .setdefault('schema', {'type': 'object'})\
            .setdefault('properties', {})\
            [directive.name] = {'type': directive.type}
        return operation

    elif directive.kind in RESJSON_KINDS:
        field_info = {
            'description': directive.body,
            'type': directive.type,
        }
        operation\
            .setdefault('responses', {})\
            .setdefault('200', {})\
            .setdefault('content', {})\
            .setdefault('application/json', {})\
            .setdefault('schema', {'type': 'object'})\
            .setdefault('properties', {})\
            [directive.name] = field_info
        return operation

    elif directive.kind in REQJSONARR_KINDS or directive.kind in RESJSONARR_KINDS:
        print('Warning: reqjsonarr and resjsonarr are not supported, ignoring.')
        print('  Please use reqjson and resjson.')
        return operation

    elif directive.kind in REQHEADER_KINDS:
        value = {
            'name': directive.name,
            'in': 'header',
            'description': directive.body,
            'schema': {
                'type': 'string',
            },
        }
        operation\
            .setdefault('parameters', [])\
            .append(value)
        return operation

    elif directive.kind in RESHEADER_KINDS:
        header = {
            'description': directive.body,
            'schema': {
                'type': 'string',
            },
        }
        operation\
            .setdefault('responses', {})\
            .setdefault('200', {})\
            .setdefault('headers', {})\
            [directive.name] = header
        return operation

    elif directive.kind in STATUS_KINDS:
        operation\
            .setdefault('responses', {})\
            .setdefault(directive.name, {})\
            .update(description=directive.body)
        return operation

    else:
        print(f'Warning: Unknown directive kind {directive.kind}')
        return operation


def make_openapi_operation_object(view_docstring):
    lines = prepare_docstring(view_docstring)
    directive_lines, non_directive_lines = split_list_by_function(
        lines, parse_directive
    )
    directive_lines = directive_lines
    non_directive_lines = remove_start_and_end_empty_strings(non_directive_lines)
    summary_line = non_directive_lines[0]
    description_lines = remove_start_and_end_empty_strings(non_directive_lines[1:])

    openapi_operation = {
        'summary': summary_line,
        'description': '\n'.join(description_lines),
    }

    # NOTE: You can use this for debugging.
    if False:
        print('\n'.join([str(d) for d in non_directive_lines]))
        print('--')
        print('\n'.join([str(d) for d in directive_lines]))
        print('------------------------------------')

    for directive in directive_lines:
        openapi_operation = add_directive_to_openapi_operation(
            openapi_operation, directive
        )

    return openapi_operation


def build_openapi_dict(routes, title='', version=''):
    openapi_dict = {
        'openapi': '3.0.0',
        'info': {
            'title': title,
            'version': version,
        },
        'paths': {},
    }

    for method, paths, view_fn_name, view_docstring in routes:
        if view_docstring:
            for path in paths:
                if path not in openapi_dict['paths']:
                    openapi_dict['paths'][path] = {}
                openapi_dict['paths'][path][method.lower()] = \
                    make_openapi_operation_object(view_docstring)

    return openapi_dict


def print_openapi_dict(openapi_dict):
    yaml.dump(openapi_dict, sys.stdout)


def main():
    import_name = ''
    title = ''
    version = ''

    opts, _ = getopt.getopt(
        sys.argv[1:],
        'a:t:v:',
        ['app=', 'title=', 'version=']
    )

    for opt, arg in opts:
        if opt in ['-a', '--app']:
            import_name = arg
        elif opt in ['-t', '--title']:
            title = arg
        elif opt in ['-v', '--version']:
            version = arg

    if import_name == '' or title == '' or version == '':
        print_usage_and_exit()

    app = import_object(import_name)
    routes = get_routes(app)
    openapi_dict = build_openapi_dict(routes, title, version)
    print_openapi_dict(openapi_dict)


if __name__ == '__main__':
    APP_DIR = '../50five-nl-backend/'
    # APP_DIR = '../docs-demo-openapi/'
    sys.path.insert(0, os.path.abspath(APP_DIR))
    os.chdir(APP_DIR)
    main()
