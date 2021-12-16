# docstrings-to-openapi

Generates an OpenAPI document from a python web framework's defined controllers/paths/view docstrings.


## Supported Frameworks

Currently only flask is provided, but any other python web framework can be added.


## Docstring Styles

* [httpdomain](docs/httpdomain.md)
* [openapi-block (yaml)](docs/openapi-block.md)


## Dependencies

* PyYAML


## Install

docstrings-to-openapi will most likely need to be installed in the app's virtualenv in order to run correctly.

Since this is not on pypi, for the time being, it can be installed by cloning the project to your machine or using the pip feature from installing from a url:

```
$ git clone https://github.com/saffronsoftware/httpdomain-to-openapi.git
# Remember to have your project's virtualenv activated
(my-project-venv) $ pip install -e ./httpdomain-to-openapi
```
or
```
(my-project-env) $ pip install -e git+ssh://git@github.com/saffronsoftware/httpdomain-to-openapi.git
```

And once successfully installed, it can be ran:
```
(my-project-env) $ docstrings-to-openapi
```


### Command Options

```
usage: docstrings-to-openapi [-h] [-d] [-f {json,yaml}] [--openapi-spec OPENAPI_SPEC] [-s {httpdomain,openapi-block}] -t TITLE -v VERSION {flask} ...

positional arguments:
  {flask}

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           Prints extra log messages to stderr
  -f {json,yaml}, --format {json,yaml}
                        The output format for the OpenAPI doc (default: yaml)
  --openapi-spec OPENAPI_SPEC
                        The OpenAPI doc spec (default: 3.0.0)
  -s {httpdomain,openapi-block}, --style {httpdomain,openapi-block}
                        The docstring style for the OpenAPI details (default: openapi-block)
  -t TITLE, --title TITLE
                        The title to show on the app the OpenAPI doc
  -v VERSION, --version VERSION
                        The app API version to show on the OpenAPI doc
```


#### Flask

```
usage: docstrings-to-openapi flask [-h] -a APP -b APP_DIR

optional arguments:
  -h, --help            show this help message and exit
  -a APP, --app APP     The flask app import name in python
  -b APP_DIR, --app-dir APP_DIR
                        The directory where the flask app source is
```


## Limitations

This program does not cover certain Flask functionality such as
[pluggable views](https://flask.palletsprojects.com/en/1.1.x/views/)
and most likely blueprints.

Support for this could be quite straightfoward by consulting the, `sphinxcontrib-httpdomain` source, in particular `flask_base.py`.
However, this functionality was not needed when writing `httpdomain-to-openapi` for its initial use case.

OpenAPI defined components are not supported at this time.


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
