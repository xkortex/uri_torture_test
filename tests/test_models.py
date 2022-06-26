from typing import Any, Callable, Optional, Tuple

import httpx
import pytest
import rfc3986
from conftest import corner_cases_data, gold_standard_uris_data, invalid_uris_data, silver_standard_uris_data
from pydantic import AnyUrl, parse_obj_as

from uri_torture_test.models import URI, URIExample


@pytest.mark.parametrize("uri,example", [(el.uri, el) for el in gold_standard_uris_data])
def test_uri_cls_gold_standard_uris(uri: str, example: URIExample):
    got_uri = URI(uri)
    for name, value in example.parts.items():
        got_value = getattr(got_uri, name)
        assert got_value == value


@pytest.mark.parametrize("uri,example", [(el.uri, el) for el in silver_standard_uris_data])
def test_uri_cls_silver_standard_uris(uri: str, example: URIExample):
    got_uri = URI(uri)
    if example.parts:
        for name, value in example.parts.items():
            got_value = getattr(got_uri, name)
            assert got_value == value


@pytest.mark.xfail(reason="this validator currently is not strong enough to reject these")
@pytest.mark.parametrize("uri,example", [(el.uri, el) for el in invalid_uris_data])
def test_uri_cls_invalid_uris(uri: str, example: URIExample):
    with pytest.raises(ValueError) as exc_info:
        _ = URI(uri)


@pytest.mark.parametrize("uri,example", [(el.uri, el) for el in invalid_uris_data])
def test_any_url_invalid_uris(uri: str, example: URIExample):
    with pytest.raises(ValueError) as exc_info:
        _ = parse_obj_as(AnyUrl, uri)


@pytest.mark.xfail(reason="rfc3986 library is bad at validating")
@pytest.mark.parametrize("uri,example", [(el.uri, el) for el in invalid_uris_data])
def test_rfc3986_invalid_uris(uri: str, example: URIExample):
    assert not rfc3986.is_valid_uri(uri)


def try_parse(uri: str, func: Callable) -> Tuple:
    try:
        return func(uri), None
    except Exception as exc:
        return None, exc


@pytest.mark.parametrize("uri,example", [(el.uri, el) for el in corner_cases_data])
def test_debug_corner_cases(uri: str, example: URIExample):
    print(f"\n{example!r}")
    xkortex_uri = URI(uri).dict()
    pydantic_uri = parse_obj_as(AnyUrl, uri)
    rfc3986_uri = rfc3986.urlparse(uri)
    httpx_uri, httpx_exc = try_parse(uri, httpx.URL)
    print(f"{xkortex_uri=}")
    print(f"{pydantic_uri=}")
    print(f"{rfc3986_uri=}")
    print(f"{httpx_uri or httpx_exc=}")
