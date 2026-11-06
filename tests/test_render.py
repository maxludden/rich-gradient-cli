"""Tests for rich-gradient renderable construction."""

import json

import pytest
from rich.console import Console

from rich_gradient_cli.render import (
    RenderConfig,
    build_inner,
    build_output,
    resolve_expand,
    resolve_object,
    slice_lines,
    spectrum_output,
)
from rich_gradient_cli.resource import Mode, Resource, ResourceError


def _res(text: str, name: str = "") -> Resource:
    """Build a literal-less resource for tests."""
    return Resource(text=text, name=name)


def _render(renderable: object) -> str:
    """Render to plain text at a fixed width."""
    console = Console(width=60, record=True, file=open("/dev/null", "w"))
    console.print(renderable)
    return console.export_text()


def test_slice_lines() -> None:
    """head/tail keep the right lines."""
    assert slice_lines("a\nb\nc", 2, None) == "a\nb"
    assert slice_lines("a\nb\nc", None, 1) == "c"
    assert slice_lines("a\nb", None, None) == "a\nb"


def test_csv_head_and_escape() -> None:
    """CSV rows are limited and cells are not parsed as markup."""
    cfg = RenderConfig(head=1)
    out = _render(build_inner(Mode.CSV, _res("h1,h2\n[b]x[/b],1\ny,2", "a.csv"), cfg))
    assert "[b]x[/b]" in out and "y" not in out


def test_csv_empty() -> None:
    """Empty CSV is a clear error."""
    with pytest.raises(ResourceError):
        build_inner(Mode.CSV, _res("", "a.csv"), RenderConfig())


def test_json_invalid() -> None:
    """Bad JSON raises ResourceError."""
    with pytest.raises(ResourceError, match="Invalid JSON"):
        build_inner(Mode.JSON, _res("{"), RenderConfig())


def test_ipynb() -> None:
    """Notebook cells and outputs render."""
    nb = {"cells": [
        {"cell_type": "code", "execution_count": 1, "source": ["print(1)"],
         "outputs": [{"output_type": "stream", "text": ["1\n"]}]},
        {"cell_type": "markdown", "source": ["# Title"]},
    ], "metadata": {"kernelspec": {"language": "python"}}}
    out = _render(build_inner(Mode.IPYNB, _res(json.dumps(nb)), RenderConfig()))
    assert "print(1)" in out and "Title" in out


def test_ipynb_invalid() -> None:
    """A notebook without cells is rejected."""
    with pytest.raises(ResourceError, match="Invalid notebook"):
        build_inner(Mode.IPYNB, _res("{}"), RenderConfig())


def test_tree_directory(tmp_path) -> None:
    """Directories are walked, hiding dotfiles."""
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "f.txt").write_text("x")
    (tmp_path / ".hidden").write_text("x")
    res = Resource(text="", name=str(tmp_path), path=tmp_path)
    out = _render(build_inner(Mode.TREE, res, RenderConfig()))
    assert "sub/" in out and "f.txt" in out and ".hidden" not in out


def test_resolve_object() -> None:
    """Dotted paths, builtins and expressions resolve; garbage errors."""
    assert resolve_object("str") is str
    assert resolve_object("os.path.join").__name__ == "join"
    assert resolve_object("1 + 1") == 2
    with pytest.raises(ResourceError):
        resolve_object("no_such_name_xyz")


def test_columns_empty() -> None:
    """--columns needs content."""
    with pytest.raises(ResourceError):
        build_inner(Mode.COLUMNS, _res("  \n"), RenderConfig())


def test_invalid_markup() -> None:
    """Bad markup suggests --no-markup."""
    with pytest.raises(ResourceError, match="no-markup"):
        build_inner(Mode.TEXT, _res("[/nope]"), RenderConfig())


def test_resolve_expand() -> None:
    """Explicit expand wins; panels and markdown expand by default."""
    assert resolve_expand(Mode.TEXT, RenderConfig(expand=True))
    assert resolve_expand(Mode.TEXT, RenderConfig(panel=True))
    assert resolve_expand(Mode.MARKDOWN, RenderConfig())
    assert not resolve_expand(Mode.TEXT, RenderConfig())


def test_build_output_panel_and_rule() -> None:
    """Panels and rules build without error."""
    console = Console(width=40, file=open("/dev/null", "w"))
    cfg = RenderConfig(colors="red,blue", panel=True, title="T")
    assert "hi" in _render(build_output(Mode.TEXT, _res("hi"), cfg, console, animated=False))
    rule = build_output(Mode.RULE, _res("title"), RenderConfig(colors="red,blue"), console, animated=False)
    assert "title" in _render(rule)


def test_spectrum_output_formats() -> None:
    """Names/hex/csv formats list one row per hue."""
    for fmt in ("names", "hex", "csv"):
        out = _render(spectrum_output(RenderConfig(hues=5, spectrum_output=fmt)))
        assert len([line for line in out.splitlines() if line.strip()]) == 5


def test_tree_dot_uses_real_directory_name(tmp_path, monkeypatch) -> None:
    """``--tree .`` labels the root with the real directory name, not ``.``."""
    (tmp_path / "f.txt").write_text("x")
    monkeypatch.chdir(tmp_path)
    from pathlib import Path

    res = Resource(text="", name=".", path=Path("."))
    out = _render(build_inner(Mode.TREE, res, RenderConfig()))
    assert out.splitlines()[0].strip() == tmp_path.name


def test_tree_max_depth_exact(tmp_path) -> None:
    """``max_depth`` stops at exactly that many levels."""
    (tmp_path / "a" / "b").mkdir(parents=True)
    (tmp_path / "a" / "b" / "deep.txt").write_text("x")
    res = Resource(text="", name=str(tmp_path), path=tmp_path)
    out = _render(build_inner(Mode.TREE, res, RenderConfig(max_depth=2)))
    assert "b/" in out and "deep.txt" not in out
