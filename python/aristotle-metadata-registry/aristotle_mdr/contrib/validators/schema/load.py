from os import path


def load_schema(self):
    schema_path = path.join(__file__, 'schema.json')
    with open(schema_path) as f:
        schema = f.read()
    return schema
