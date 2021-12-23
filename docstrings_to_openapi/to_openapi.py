import json
import sys

import yaml

from .cli import OPTS


def main():
    """The main function for building the OpenAPI doc.

    It starts by mapping out the supported frameworks and docstring styles.
    Then based on the parameters the tool was called with, it will then call
    into the chosen modules to build the openapi document.

    The output will be done on `stdout`.

    Any prints, e.g. with `-d` `--debug` enabled will be output on `stderr`.

    """
    from .flask_routes import generate_flask_paths
    from .httpdomain import make_openapi_route_object as httpdomain_parse
    from .openapi_block import make_openapi_route_object as openapi_block_parse
    from .openapi_components import get_openapi_components

    frameworks = {
        'flask': {
            'components': get_openapi_components,
            'paths': generate_flask_paths,
        }
    }

    docstyles = {
        'httpdomain': httpdomain_parse,
        'openapi-block': openapi_block_parse,
    }

    openapi_doc = {
        'openapi': OPTS.openapi_spec,
        'info': {
            'title': OPTS.title,
            'version': OPTS.version,
        },
    }

    docstyle = docstyles.get(OPTS.style)

    get_components = frameworks.get(OPTS.framework).get('components')
    get_paths = frameworks.get(OPTS.framework).get('paths')

    openapi_doc['components'] = get_components()
    openapi_doc['paths'] = get_paths(docstyle)

    if OPTS.format == 'yaml':
        yaml.dump(openapi_doc, sys.stdout)
    else:
        json.dump(openapi_doc, sys.stdout)


if __name__ == '__main__':
    main()
