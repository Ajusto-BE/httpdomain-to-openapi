import argparse
from pprint import pprint
import sys

parser = argparse.ArgumentParser()

framework_parser = parser.add_subparsers(dest='framework')

flask_parser = framework_parser.add_parser('flask')
flask_parser.add_argument(
    '-a', '--app',
    help="The flask app import name in python",
    required=True,
)
flask_parser.add_argument(
    '-b', '--app-dir',
    help="The directory where the flask app source is",
    required=True,
)

parser.add_argument(
    '-d', '--debug', 
    action='store_true',
    help="Prints extra log messages to stderr"
)
parser.add_argument(
    '-f', '--format',
    choices=['json', 'yaml'],
    default='yaml',
    help="The output format for the OpenAPI doc (default: %(default)s)",
)
parser.add_argument(
    '--openapi-spec',
    default='3.0.0',
    help="The OpenAPI doc spec (default: %(default)s)",
)
parser.add_argument(
    '-s', '--style',
    choices=['httpdomain', 'openapi-block'],
    default='openapi-block',
    help="The docstring style for the OpenAPI details (default: %(default)s)",
)
parser.add_argument(
    '-t', '--title',
    help="The title to show on the app the OpenAPI doc",
    required=True,
)
parser.add_argument(
    '-v', '--version',
    help="The app API version to show on the OpenAPI doc",
    required=True,
)

OPTS = parser.parse_args()

if OPTS.debug:
    print('Debug provided command parameters:', file=sys.stderr)
    pprint(vars(OPTS), stream=sys.stderr)

if __name__ == '__main__':
    "For testing the cli arguments using only this file"
    print(OPTS)
