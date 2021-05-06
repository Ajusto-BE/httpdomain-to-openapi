from collections import defaultdict
import builtins
import functools
import io
import os
import sys
import yaml


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
        Usage: python httpdomain-to-openapi.py <flask_app_import_name>
            e.g python httpdomain-to-openapi.py my_app:app
    ''')
    sys.exit(1)


def is_docstring_line_directive(docstring_line):
    return docstring_line.startswith(':')


def remove_start_and_end_empty_strings(lines):
    if len(lines) == 0:
        return lines
    while len(lines[0]) == 0:
        lines.pop(0)
    while len(lines[-1]) == 0:
        lines.pop(-1)
    return lines


def parse_directive(directive_line):
    return directive_line


def make_openapi_operation_parts_from_directive(directive):
    return {'lol': 'hi'}


def make_openapi_operation_object(view_docstring):
    lines = prepare_docstring(view_docstring)
    directive_lines = remove_start_and_end_empty_strings(
        [line for line in lines if is_docstring_line_directive(line)]
    )
    non_directive_lines = remove_start_and_end_empty_strings(
        [line for line in lines if not is_docstring_line_directive(line)]
    )
    summary_line = non_directive_lines[0]
    description_lines = remove_start_and_end_empty_strings(non_directive_lines[1:])

    openapi_operation = {
        'summary': summary_line,
        'description': '\n'.join(description_lines),
    }

    print('\n'.join(directive_lines))
    print('------------------------------------')

    for directive_line in directive_lines:
        directive = parse_directive(directive_line)
        new_operation_parts = make_openapi_operation_parts_from_directive(directive)
        openapi_operation = {**openapi_operation, **new_operation_parts}

    return openapi_operation


def build_openapi_dict(routes):
    # TODO: Add support for title as parameter
    # TODO: Add support for version as parameter
    openapi_dict = {
        'openapi': '3.0.0',
        'info': {
            'title': 'My cool API!',
            'version': '1',
        },
        'paths': {},
    }

    for method, paths, view_fn_name, view_docstring in routes:
        for path in paths:
            if path not in openapi_dict['paths']:
                openapi_dict['paths'][path] = {}
            openapi_dict['paths'][path][method.lower()] = \
                make_openapi_operation_object(view_docstring)

    return openapi_dict


def print_openapi_dict(openapi_dict):
    yaml.dump(openapi_dict, sys.stdout)


def main():
    if len(sys.argv) < 2:
        print_usage_and_exit()

    import_name = sys.argv[1]
    app = import_object(import_name)
    routes = get_routes(app)
    openapi_dict = build_openapi_dict(routes)
    print_openapi_dict(openapi_dict)


if __name__ == '__main__':
    # APP_DIR = '../50five-nl-backend/'
    APP_DIR = '../docs-demo-openapi/'
    sys.path.insert(0, os.path.abspath(APP_DIR))
    os.chdir(APP_DIR)
    main()
