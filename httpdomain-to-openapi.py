from collections import defaultdict
import builtins
import functools
import io
import os
import sys
import yaml


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


def make_openapi_operation_object(view_docstring):
    return {
        'da': 'da!',
    }


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
