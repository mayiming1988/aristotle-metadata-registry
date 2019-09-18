from os import path
from functools import lru_cache


@lru_cache(maxsize=1)  # Cache the result (only need 1 since there are no args)
def load_schema() -> str:
    schema_path = path.join(path.dirname(__file__), 'schema.json')
    with open(schema_path) as f:
        schema = f.read()
    return schema
