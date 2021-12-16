import builtins
from collections import defaultdict
import functools
import os
from pprint import pprint
import sys


def _clean_up_methods(methods):
    autoadded_methods = frozenset(['OPTIONS', 'HEAD'])
    if methods <= autoadded_methods:
        return methods
    return methods.difference(autoadded_methods)


def _get_routes(app):
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
            for method in _clean_up_methods(rule.methods):
                methodrules[method].append(path)

        for method, paths in methodrules.items():
            view_fn = app.view_functions[view_fn_name]
            view_docstring = view_fn.__doc__
            if view_docstring:
                yield method, paths, view_fn_name, view_docstring


def _import_object(import_name):
    module_name, expr = import_name.split(':', 1)
    mod = __import__(module_name)
    mod = functools.reduce(getattr, module_name.split('.')[1:], mod)
    globals = builtins
    if not isinstance(globals, dict):
        globals = globals.__dict__
    return eval(expr, globals, mod.__dict__)


def generate_flask_paths(docstring_parse):
    """Creates the openapi structure for all the flask app's routes.

    This function will try to import the flask app itself to get the data
    for the defined routes.

    Parameters
    ----------
    doctring_parse : function

    Returns
    -------
    dict
        **path : dict
            The url route
            **method : dict
                Each method of the url route

    """
    from .cli import OPTS

    sys.path.insert(0, os.path.abspath(OPTS.app_dir))
    os.chdir(OPTS.app_dir)
    
    app = _import_object(OPTS.app)
    routes = _get_routes(app)

    collection = {}

    for method, paths, view_fn_name, view_docstring in routes:
        for path in paths:
            if path not in collection:
                collection[path] = {}

            route_doc = docstring_parse(view_docstring)

            if OPTS.debug:
                print('Debug for', method, path, file=sys.stderr)
                pprint(route_doc, stream=sys.stderr)

            collection[path][method.lower()] = route_doc

    return collection
