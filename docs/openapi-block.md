# Using openapi-block

Docstrings can include a block with a `yaml` text piece that will be directly added to the generated OpenAPI doc for the app.

To include the openapi details for the route, make sure the text is providing in the docstring starting with `` ```openapi `` and ending with `` ``` ``.

Since it supports directly defining the details for the path in `yaml`, everything should be supported with in the spec.

Only `yaml` syntax is supported in these blocks, and `yaml` indentation rules apply.


## Example

Here's a following example using Flask as the route:

```python
@app.route('/api/neat/<int:_id>', methods=['PUT'])
def update_neat_thing(_id):
    """Summary example of the route, Update a neat thing for an ID

    This part is an example description of the route. Any text will be
    displayed in the `description` property for the `path` in the OpenAPI doc
    and supports **markdown** syntax.

    ```openapi
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
    \`\`\`

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
