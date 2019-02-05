from os import path


def load_schema():
    schema_path = path.join(path.dirname(__file__), 'schema.json')
    with open(schema_path) as f:
        schema = f.read()
    return schema
