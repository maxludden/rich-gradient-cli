"""Locate and read the RESOURCE argument (file, URL, stdin, or literal text)."""

from __future__ import annotations

import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from urllib.parse import urlparse

USER_AGENT = "rich-gradient-cli"
URL_TIMEOUT = 10.0
#: Largest response body (bytes) that will be downloaded from a URL.
MAX_DOWNLOAD_BYTES = 10 * 1024 * 1024


class ResourceError(Exception):
    """Raised when a resource cannot be read or rendered (exit code 1)."""


class Mode(str, Enum):
    """The renderable used to display a resource."""

    TEXT = "text"
    MARKDOWN = "markdown"
    SYNTAX = "syntax"
    JSON = "json"
    CSV = "csv"
    RULE = "rule"
    TREE = "tree"
    COLUMNS = "columns"
    SPECTRUM = "spectrum"
    RST = "rst"
    IPYNB = "ipynb"
    INSPECT = "inspect"


@dataclass(frozen=True)
class Resource:
    """Content read from a RESOURCE argument.

    Attributes:
        text: The decoded content (or literal text).
        name: A file name, URL path, or ``""`` for stdin and literal text.
        is_literal: ``True`` when the argument itself was the content.
        path: The local path when the resource is an existing file or directory.
    """

    text: str
    name: str = ""
    is_literal: bool = False
    path: Path | None = None

    @property
    def suffix(self) -> str:
        """Lower-cased file extension of :attr:`name`, including the dot."""
        return Path(self.name).suffix.lower()


#: File extensions that select a mode when no mode flag is given.
EXTENSION_MODES: dict[str, Mode] = {
    ".md": Mode.MARKDOWN,
    ".markdown": Mode.MARKDOWN,
    ".json": Mode.JSON,
    ".csv": Mode.CSV,
    ".tsv": Mode.CSV,
    ".rst": Mode.RST,
    ".ipynb": Mode.IPYNB,
}


def is_url(value: str) -> bool:
    """Return whether ``value`` is an ``http://`` or ``https://`` URL."""
    return urlparse(value).scheme in {"http", "https"}


def _decode(data: bytes, name: str) -> str:
    """Decode UTF-8 bytes, rejecting binary or non-UTF-8 content clearly."""
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ResourceError(f"{name or 'input'} is not valid UTF-8 text.") from exc


def _fetch(url: str) -> str:
    """Download ``url`` with a timeout, failing on HTTP errors."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=URL_TIMEOUT) as response:  # noqa: S310
            data = response.read(MAX_DOWNLOAD_BYTES + 1)
            if len(data) > MAX_DOWNLOAD_BYTES:
                raise ResourceError(
                    f"{url} is larger than {MAX_DOWNLOAD_BYTES // (1024 * 1024)} MB."
                )
            return _decode(data, url)
    except urllib.error.HTTPError as exc:
        raise ResourceError(f"Unable to fetch {url}: HTTP {exc.code} {exc.reason}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise ResourceError(f"Unable to fetch {url}: {exc}") from exc


def read_resource(resource: str | None, *, allow_directory: bool = False) -> Resource:
    """Resolve a RESOURCE argument into content.

    ``-`` (or ``None`` with piped stdin) reads stdin, ``http(s)://`` URLs are
    downloaded, existing files are read as UTF-8, and anything else is treated
    as literal text.

    Args:
        resource: The positional argument, or ``None`` if omitted.
        allow_directory: Return an empty :class:`Resource` for directories
            instead of raising (used by ``--tree``).

    Raises:
        ResourceError: On unreadable files, directories, bad UTF-8, or HTTP failures.
    """
    if resource is None or resource == "-":
        return Resource(text=_decode(sys.stdin.buffer.read(), "stdin"))
    if is_url(resource):
        return Resource(text=_fetch(resource), name=urlparse(resource).path)
    path = Path(resource).expanduser()
    try:
        is_dir, is_file = path.is_dir(), path.is_file()
    except (OSError, RuntimeError):
        # Too long or otherwise invalid as a path (e.g. a paragraph): literal text.
        is_dir = is_file = False
    if is_dir:
        if allow_directory:
            return Resource(text="", name=str(path), path=path)
        raise ResourceError(f"{resource} is a directory; pass a file, or use --tree.")
    if is_file:
        try:
            return Resource(text=_decode(path.read_bytes(), resource), name=path.name, path=path)
        except OSError as exc:
            raise ResourceError(f"Unable to read {resource}: {exc.strerror or exc}") from exc
    return Resource(text=resource, is_literal=True)


def detect_mode(resource: Resource) -> Mode:
    """Choose a mode from the resource's extension, defaulting to plain text."""
    if resource.is_literal or not resource.name:
        return Mode.TEXT
    if resource.suffix in EXTENSION_MODES:
        return EXTENSION_MODES[resource.suffix]
    if resource.suffix in {".txt", ""}:
        return Mode.TEXT
    return Mode.SYNTAX


__all__ = [
    "EXTENSION_MODES",
    "Mode",
    "Resource",
    "ResourceError",
    "detect_mode",
    "is_url",
    "read_resource",
]
