"""Tests for resource reading and mode detection."""

import io
import urllib.error
from pathlib import Path

import pytest

from rich_gradient_cli import resource
from rich_gradient_cli.resource import Mode, ResourceError, detect_mode, read_resource


def test_literal_text() -> None:
    """Text that is not a path is treated literally."""
    res = read_resource("hello world")
    assert res.is_literal and res.text == "hello world"
    assert detect_mode(res) is Mode.TEXT


def test_file_and_detection(tmp_path: Path) -> None:
    """Files are read and the mode follows the extension."""
    for name, mode in [("a.md", Mode.MARKDOWN), ("a.json", Mode.JSON),
                       ("a.csv", Mode.CSV), ("a.py", Mode.SYNTAX), ("a.txt", Mode.TEXT)]:
        path = tmp_path / name
        path.write_text("x", encoding="utf-8")
        assert detect_mode(read_resource(str(path))) is mode


def test_directory_rejected(tmp_path: Path) -> None:
    """Directories need --tree."""
    with pytest.raises(ResourceError, match="directory"):
        read_resource(str(tmp_path))
    assert read_resource(str(tmp_path), allow_directory=True).path == tmp_path


def test_binary_rejected(tmp_path: Path) -> None:
    """Non-UTF-8 files raise a clear error."""
    path = tmp_path / "x.bin"
    path.write_bytes(b"\xff\xfe\x00")
    with pytest.raises(ResourceError, match="UTF-8"):
        read_resource(str(path))


def test_stdin(monkeypatch: pytest.MonkeyPatch) -> None:
    """'-' reads stdin."""
    monkeypatch.setattr("sys.stdin", io.TextIOWrapper(io.BytesIO(b"piped")))
    assert read_resource("-").text == "piped"


def test_stdin_binary_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    """Non-UTF-8 stdin raises ResourceError rather than a traceback."""
    monkeypatch.setattr("sys.stdin", io.TextIOWrapper(io.BytesIO(b"\xff\xfe\x00")))
    with pytest.raises(ResourceError, match="UTF-8"):
        read_resource("-")


def test_long_literal_is_text() -> None:
    """A literal longer than the OS path limit is still literal text."""
    text = "word " * 200
    res = read_resource(text)
    assert res.is_literal and res.text == text


def test_url_too_large(monkeypatch: pytest.MonkeyPatch) -> None:
    """Oversized responses are rejected."""
    class Response(io.BytesIO):
        def __enter__(self) -> "Response":
            return self

        def __exit__(self, *args: object) -> None:
            self.close()

    monkeypatch.setattr(resource, "MAX_DOWNLOAD_BYTES", 4)
    monkeypatch.setattr(resource.urllib.request, "urlopen", lambda *a, **k: Response(b"12345"))
    with pytest.raises(ResourceError, match="larger than"):
        read_resource("https://example.com/big")


def test_url_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    """URLs are downloaded and named by path."""
    class Response(io.BytesIO):
        def __enter__(self) -> "Response":
            return self

        def __exit__(self, *args: object) -> None:
            self.close()

    monkeypatch.setattr(resource.urllib.request, "urlopen", lambda *a, **k: Response(b"# hi"))
    res = read_resource("https://example.com/doc.md")
    assert res.text == "# hi" and detect_mode(res) is Mode.MARKDOWN


def test_url_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """HTTP errors are reported, not rendered."""
    def boom(*args: object, **kwargs: object) -> None:
        raise urllib.error.HTTPError("https://x", 404, "Not Found", None, None)  # type: ignore[arg-type]

    monkeypatch.setattr(resource.urllib.request, "urlopen", boom)
    with pytest.raises(ResourceError, match="404"):
        read_resource("https://example.com/missing")
