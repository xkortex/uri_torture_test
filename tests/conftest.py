import json
from pathlib import Path
from typing import List

from uri_torture_test.models import URIExample, URIParts

tests_dir = Path("./tests").resolve()
fixtures_dir = tests_dir.joinpath('fixtures')
assert fixtures_dir.is_dir()


def load_uri_example(fn: Path) -> List[URIExample]:
    with open(fn) as fp:
        data = json.load(fp)

    out = []
    for item in data:
        item['parts'] = URIParts(**item['parts']) if 'parts' in item else None
        out.append(URIExample(**item))
    return out


gold_standard_uris_data = load_uri_example(fixtures_dir.joinpath('gold_standard_uris.json'))
silver_standard_uris_data = load_uri_example(fixtures_dir.joinpath('silver_standard_uris.json'))
invalid_uris_data = load_uri_example(fixtures_dir.joinpath('invalid_uris.json'))
corner_cases_data = load_uri_example(fixtures_dir.joinpath('corner_cases.json'))
