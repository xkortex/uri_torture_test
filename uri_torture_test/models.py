import re
from dataclasses import dataclass
from typing import Any, Dict, Optional, TypedDict, Union, no_type_check

re_rfc3986_basic = re.compile(
    r"((?P<scheme>[a-z][a-z0-9+\-.]+):)"
    r"(//(?P<authority>[^/?#\s]*))?"
    r"(?P<path>[^?#\s]*)"
    r"(\?(?P<query>[^#\s]*))?"
    r"(#(?P<fragment>[^#\s]))?"
)
re_rfc3986_full = re.compile(
    r'(?:(?P<scheme>[a-z][a-z0-9+\-.]+):)?'  # scheme https://tools.ietf.org/html/rfc3986#appendix-A
    r'(?://'
    r'(?P<authority>'
    r'(?:(?P<user>[^\s:/@#?]*)(?::(?P<password>[^\s/@#?]*))?@)?'  # user info
    r'(?:'
    r'(?P<ipv4>(?:\d{1,3}\.){3}\d{1,3})(?=$|[/:#?])|'  # ipv4
    r'(?P<ipv6>\[[A-F0-9]*:[A-F0-9:]+\])(?=$|[/:#?])|'  # ipv6
    r'(?P<domain>[^\s/:?#]+)'  # domain, validation occurs later
    r')?'
    r'(?::(?P<port>\d+))?'  # port
    r'))?'  # authority
    r'(?P<path>[^\s?#]*)?'  # path
    r'(?:\?(?P<query>[^\s#]*))?'  # query
    r'(?:#(?P<fragment>[^\s#]*))?',  # fragment
    re.IGNORECASE,
)

re_scheme = re.compile(r"^[a-z][a-z0-9+\-.]+$")
re_scheme_absolute = re.compile(r"^(?P<scheme_abs>[a-z][a-z0-9+\-.]+://)")
re_rfc3986_old = re.compile("^" + re_rfc3986_basic.pattern + "$", re.IGNORECASE)


class URIParts(TypedDict):
    scheme: str
    authority: Optional[str]
    path: Optional[str]
    query: Optional[str]
    fragment: Optional[str]


@dataclass
class URIExample:
    uri: str
    source: Optional[str] = None
    description: Optional[str] = None
    parts: Optional[URIParts] = None
    subparts: Optional[Dict[str, str]] = None
    is_locator: Optional[bool] = None

    def __str__(self):
        return f"{self.__class__.__name__}({self.uri!r})"


class URI(str):
    """
    Structured representation of an RFC 3986 URI
    URIs can be URLs or URNs
    URIs ALWAYS have a scheme and almost always a path.

    """

    __slots__ = ('_scheme', '_authority', '_path', '_query', '_fragment')

    @no_type_check
    def __new__(cls, uri: Union[str, 'URI']) -> 'URI':
        """"""
        if isinstance(uri, cls):
            return uri

        return cls.parse(uri)

    @classmethod
    def parse(cls, uri: Union[str, 'URI']) -> 'URI':
        if uri is None or len(uri) == 0:
            raise ValueError("URI could not be parsed. No uri value was provided")

        has_authority = re_scheme_absolute.match(uri)
        if has_authority:
            # todo: use alternate parser here for pydantic compatibility
            pass

        match = re_rfc3986_full.match(uri)

        if match is None:
            raise ValueError(f"Does not match valid RFC 3986 URI: {uri!r}")
        gd = match.groupdict()

        return cls._from_parsed(uri, **gd)

    @classmethod
    def _from_parsed(
        cls,
        uri: str,
        scheme: str,
        authority: Optional[str],
        path: Optional[str],
        query: Optional[str],
        fragment: Optional[str],
        **kw,
    ) -> 'URI':
        self = str.__new__(cls, uri)
        self._scheme = scheme
        self._authority = authority
        self._path = path
        self._query = query
        self._fragment = fragment
        return self

    @classmethod
    def build(
        cls,
        scheme: str,
        authority: Optional[str] = None,
        path: Optional[str] = None,
        query: Optional[str] = None,
        fragment: Optional[str] = None,
    ) -> 'URI':
        # todo: deal with degenerate slashes
        if not scheme:
            raise ValueError("Every URI must have a scheme")
        if not re_scheme.match(scheme):
            raise ValueError("Scheme contains invalid character ({}): scheme={!r}".format(r':/?\#\s', scheme))
        scheme_part = scheme + ':'
        if authority:
            authority_part = '//' + authority
        elif authority == '':
            authority_part = ''
        else:
            authority_part = ''
        if query:
            query_part = '?' + query
        else:
            query_part = ''

        if fragment:
            fragment_part = '#' + fragment
        else:
            fragment_part = ''

        path = path or ''

        uri = ''.join((scheme_part, authority_part, path, query_part, fragment_part))

        return cls._from_parsed(uri, scheme, authority, path, query, fragment)

    def __repr__(self):
        contents = ', '.join(f"{k}={v!r}" for k, v in self.dict().items() if v is not None)
        return f"{self.__class__.__name__}.build({contents})"

    def dict(self):
        return {
            "scheme": self.scheme,
            "authority": self.authority,
            "path": self.path,
            "query": self.query,
            "fragment": self.fragment,
        }

    @property
    def scheme(self) -> str:
        return self._scheme

    @property
    def authority(self) -> Optional[str]:
        return self._authority

    @property
    def path(self) -> Optional[str]:
        return self._path

    @property
    def query(self) -> Optional[str]:
        return self._query

    @property
    def fragment(self):
        return self._fragment

    @classmethod
    def __get_validators__(cls) -> 'CallableGenerator':
        """Allows this class to be validated with Pydantic"""
        yield cls.validate

    @classmethod
    def validate(cls, value: Any, field: 'ModelField', config: 'BaseConfig') -> 'AnyUrl':
        """Allows this class to be validated with Pydantic"""
        if value.__class__ == cls:
            return value
        self = cls(value)
        return self
