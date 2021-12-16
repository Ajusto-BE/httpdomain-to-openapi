from dataclasses import dataclass
import sys

from .utils import (
    prepare_docstring,
    remove_start_and_end_empty_strings
)


FORM_KINDS       = ['formparameter', 'formparam', 'fparam', 'form']
JSON_KINDS       = ['jsonparameter', 'jsonparam', 'json']
PARAM_KINDS      = ['param', 'parameter', 'arg', 'argument']
QUERY_KINDS      = ['queryparameter', 'queryparam', 'qparam', 'query']
REQJSON_KINDS    = ['reqjsonobj', 'reqjson', '<jsonobj', '<json']
RESJSON_KINDS    = ['resjsonobj', 'resjson', '>jsonobj', '>json']
REQJSONARR_KINDS = ['reqjsonarr', '<jsonarr']
RESJSONARR_KINDS = ['resjsonarr', '>jsonarr']
REQHEADER_KINDS  = ['requestheader', 'reqheader', '>header']
RESHEADER_KINDS  = ['responseheader', 'resheader', '<header']
STATUS_KINDS     = ['statuscode', 'status', 'code']


@dataclass
class Directive:
    kind: str
    type: str
    name: str
    body: str
    properties: list


def _split_list_by_function(l, func):
    """For each item in l, if func(l) is truthy, func(l) will be added to l1.
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


def _parse_directive(directive_line):
    first_colon = directive_line.find(':')
    second_colon = directive_line.find(':', first_colon + 1)

    if first_colon != 0 or second_colon is None:
        return None

    # If we don't have a type, just default it to string
    _type = 'string'

    head = directive_line[first_colon + 1:second_colon]
    head_parts = head.split(' ')

    if len(head_parts) == 2:
        kind, name = head_parts
    elif len(head_parts) == 3:
        kind, _type, name = head_parts
    else:
        return None

    body = directive_line[second_colon + 1:].strip()

    directive = Directive(
        kind=kind,
        type=_type,
        name=name,
        body=body,
        properties=[],
    )

    return directive


def _add_directive_to_openapi_operation(operation, directive):
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

    elif (
    	directive.kind in REQJSONARR_KINDS
    	or directive.kind in RESJSONARR_KINDS
    ):
        print(
            """
            Warning: reqjsonarr and resjsonarr are not supported, ignoring.
                Please use reqjson and resjson.
            """,
            file=sys.stderr
        )
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
        print(
            f'Warning: Unknown directive kind {directive.kind}',
            file=sys.stderr
        )
        return operation


def make_openapi_route_object(view_docstring):
    """Creates the route's openapi object.

    Parameters
    ----------
    view_docstring : str

    Returns
    -------
    dict
        summary : str
        description : str
        **paths : dict

    """
    from cli import OPTS

    lines = prepare_docstring(view_docstring)

    directive_lines, non_directive_lines = _split_list_by_function(
        lines, _parse_directive
    )

    non_directive_lines = remove_start_and_end_empty_strings(
        non_directive_lines
    )

    summary_line = non_directive_lines[0]

    description_lines = remove_start_and_end_empty_strings(
        non_directive_lines[1:]
    )

    openapi_operation = {
        'summary': summary_line,
        'description': '\n'.join(description_lines),
    }

    if OPTS.debug:
        print('Debug for httpdomain:', file=sys.stderr)
        print('>>> Not directive lines', file=sys.stderr)
        print(
            '\n'.join([str(d) for d in non_directive_lines]), file=sys.stderr
        )
        print('---', file=sys.stderr)
        print('>>> Directive lines', file=sys.stderr)
        print('\n'.join([str(d) for d in directive_lines]), file=sys.stderr)
        print('', file=sys.stderr)

    for directive in directive_lines:
        openapi_operation = _add_directive_to_openapi_operation(
            openapi_operation, directive
        )

    return openapi_operation
