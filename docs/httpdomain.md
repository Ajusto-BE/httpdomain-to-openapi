# Using httpdomain

If you're not familiar with httpdomain, visit this page to see more details [httpdomain syntax](https://sphinxcontrib-httpdomain.readthedocs.io/en/stable/).


## Limitations

The httpdomain syntax is fairly simple and compact, so the syntax it self can only include so much until it complicates what you can read, as well write for the route definition.

Here are some points that are not possible at this time to translate for openapi:
* Nested object structure
* Define array/list request/responses schemas
* Placeholder
* Type format, regex rules

Currently only OpenAPI spec 3.0.0 is generated with httpdomain.


## Example

Here's a following example using Flask as the route:

```python
@app.route('/api/neat/<int:_id>', methods=['PUT'])
def update_neat_thing(_id):
    """Summary example of the route, Update a neat thing for an ID

    This part is an example description of the route. Any text will be
    displayed in the `description` property for the `path` in the OpenAPI doc
    and supports **markdown** syntax.

    :param number _id: The ID for the neat thing

    :reqjson string neat:

    :statuscode 200:
    :resjson number _id:
    :resjson string neat:

    """
    data = {
        '_id': _id,
        'neat': request.json.get('neat')
    }
 
    return Response(
        mimetype='application/json; charset=utf-8',
        response=json.dumps(data),
        status=200,
    )
```

This will result in the following OpenAPI doc:

```yaml
info:
  title: MyNeatApp
  version: 1.1.1
openapi: 3.0.0
paths:
  /api/neat/{_id}:
    put:
      description: "This part is an example description of the route. Any text will be
    displayed in the `description` property for the `path` in the OpenAPI doc
    and supports **markdown** syntax."
      parameters:
        - description: ''
          in: path
          name: _id
          required: true
          schema:
            type: number
      requestBody:
        content:
          application/json:
            schema:
              properties:
                neat:
                  type: string
      responses:
        '200':
          content:
            application/json:
              schema:
                properties:
                  _id:
                    type: number
                  neat:
                    type: string
          description: ''
      summary: Summary example of the route, Update a neat thing for an ID
```
