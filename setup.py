from setuptools import setup, find_packages


with open('README.md', 'r') as fh:
    long_description = fh.read()


setup(
    name='docstrings-to-openapi',
    version='0.1.0',
    description='Generate OpenAPI document from docstrings',
    url='https://github.com/SaffronSoftware/httpdomain-to-openapi.git',
    author='Phyramid Connections SRL',
    author_email="",
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['docstrings_to_openapi'],
    py_modules=find_packages('docstrings_to_openapi'),
    install_requires=[
        'PyYAML>=5.3.1',
    ],
    entry_points={
        'console_scripts': [
            'docstrings-to-openapi=docstrings_to_openapi.to_openapi:main'
        ],
    },
)
