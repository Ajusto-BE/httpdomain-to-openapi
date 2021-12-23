import sys

import yaml
from yaml import Loader


def get_openapi_components():
    """Get the components file from the app
    """
    from .cli import OPTS

    try:
        with open(OPTS.components_file, 'r') as component_file:
            return yaml.load(component_file, Loader=Loader)
    except FileNotFoundError as e:
        print('! There was an error trying to open the components file:')
        print(e, file=sys.stderr)
        sys.exit(2)
