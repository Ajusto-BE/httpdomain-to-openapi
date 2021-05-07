# httpdomain-to-openapi

Generates OpenAPI documentation from code documented according to the
[httpdomain syntax](https://sphinxcontrib-httpdomain.readthedocs.io/en/stable/).

## Usage

- Modify the path mentioned in APP_DIR variable from *httpdomain-to-openapi.py* file to match the location of the Flask app directory from your local machine
- Run *httpdomain-to-openapi.py* file with Python
```
python3 httpdomain-to-openapi.py --app app_example:app --title '50 Five' --version v5.25.0
```

**Command options** detailed:
1. **-a, --app**
- *type*: mendatory
- *description*: indicates the Flask app for which to collect the endpoints that need to be documented in accordance with the OpenAPI Specification
2. **-t, --title**
- *type*: optional
- *description*: adds a given title to the generated OpenAPI documentation
3. **-v, --version**
- *type*: optional
- *description*: adds a given version to the generated OpenAPI documentation

## Limitations

This program does not cover certain Flask functionality such as
[pluggable views](https://flask.palletsprojects.com/en/1.1.x/views/)
and most likely blueprints.

Support for this could be quite straightfowardly by consulting the,
`sphinxcontrib-httpdomain` source, in particular `flask_base.py`.
However, this functionality was not needed when writing
`httpdomain-to-openapi` for its initial use case.

## Acknowledgements

Author: [Vlad-Stefan Harbuz](https://github.com/vladh)

Some code is adapted from
[sphinxcontrib-httpdomain](https://github.com/sphinx-contrib/httpdomain).

```
Copyright 2021 Vlad-Stefan Harbuz

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```
