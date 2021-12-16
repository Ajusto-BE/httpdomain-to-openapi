import json
import sys

import yaml

from cli import OPTS


def main():
    """
    """
    print(OPTS)

    from flask_routes import generate_flask_paths
    from httpdomain import make_openapi_operation_object as httpdomain_parse
    from openapi_block import make_openapi_route_object as openapi_block_parse

    frameworks = {
        'flask': generate_flask_paths,
    }

    docstyles = {
        'httpdomain': httpdomain_parse,
        'openapi-block': openapi_block_parse,
    }

    openapi_doc = {
        'openapi': '3.0.0',
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
