import builtins
import functools
import io
import os
import sys


def import_object(import_name):
    module_name, expr = import_name.split(':', 1)
    mod = __import__(module_name)
    mod = functools.reduce(getattr, module_name.split('.')[1:], mod)
    globals = builtins
    if not isinstance(globals, dict):
        globals = globals.__dict__
    return eval(expr, globals, mod.__dict__)


def cleanup_methods(methods):
    autoadded_methods = frozenset(['OPTIONS', 'HEAD'])
    if methods <= autoadded_methods:
        return methods
    return methods.difference(autoadded_methods)


def translate_werkzeug_rule(rule):
    from werkzeug.routing import parse_rule
    buf = io.StringIO()
    for conv, arg, var in parse_rule(rule):
        if conv:
            buf.write('(')
            if conv != 'default':
                buf.write(conv)
                buf.write(':')
            buf.write(var)
            buf.write(')')
        else:
            buf.write(var)
    return buf.getvalue()


def get_routes(app, endpoint=None, order=None):
    endpoints = []
    for rule in app.url_map.iter_rules(endpoint):
        url_with_endpoint = (
            str(next(app.url_map.iter_rules(rule.endpoint))),
            rule.endpoint
        )
        if url_with_endpoint not in endpoints:
            endpoints.append(url_with_endpoint)
    if order == 'path':
        endpoints.sort()
    endpoints = [e for _, e in endpoints]
    for endpoint in endpoints:
        methodrules = {}
        for rule in app.url_map.iter_rules(endpoint):
            methods = cleanup_methods(rule.methods)
            path = translate_werkzeug_rule(rule.rule)
            for method in methods:
                if method in methodrules:
                    methodrules[method].append(path)
                else:
                    methodrules[method] = [path]
        for method, paths in methodrules.items():
            yield method, paths, endpoint


def main():
    if len(sys.argv) < 2:
        print('''
            Usage: python __init__.py <flask_app_import_name>
            .e.g python __init__.py my_app:app
        ''')

    import_name = sys.argv[1]
    app = import_object(import_name)
    for route in get_routes(app):
        print(route)


if __name__ == '__main__':
    APP_DIR = '../50five-nl-backend/'
    sys.path.insert(0, os.path.abspath(APP_DIR))
    os.chdir(APP_DIR)
    main()
