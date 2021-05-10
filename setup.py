from setuptools import setup


with open('README.md', 'r') as fh:
    long_description = fh.read()


setup(
    name='httpdomain-to-openapi',
    version='0.0.1',
    description='Generate OpenAPI format out of docstrings',
    url='https://github.com/Phyramid/httpdomain-to-openapi.git',
    author='Phyramid Connections SRL',
    author_email="",
    long_description=long_description,
    long_description_content_type='text/markdown'
)
