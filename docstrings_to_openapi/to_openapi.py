import json
import sys

import yaml

from .cli import OPTS


def main():
    """The main function to bulding the OpenAPI doc for the app's API.

    Here starts by mapping the supporting frameworks and docstring styles that
    can parse controller/view docs.

    Then with the incoming parameters when executing this tool, will call into
    the chosen modules to build the openapi doc.

    The output will be done on `stdout`.

    Any prints, e.g. with `-d` `--debug` enabled will be output on `stderr`.

    """
    from .flask_routes import generate_flask_paths
    from .httpdomain import make_openapi_route_object as httpdomain_parse
    from .openapi_block import make_openapi_route_object as openapi_block_parse

    frameworks = {
        'flask': generate_flask_paths,
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
        'paths': {},
    }

    docstyle = docstyles.get(OPTS.style)
    openapi_doc['paths'] = frameworks.get(OPTS.framework)(docstyle)

    if OPTS.format == 'yaml':
        yaml.dump(openapi_doc, sys.stdout)
    else:
        json.dump(openapi_doc, sys.stdout)


if __name__ == '__main__':
    main()
