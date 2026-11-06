"""Tests for SVG/HTML export."""

from pathlib import Path

import pytest
from rich.text import Text

from rich_gradient_cli.export import export_renderable


def test_export_both(tmp_path: Path) -> None:
    """Both formats are written."""
    svg, html = tmp_path / "a.svg", tmp_path / "a.html"
    export_renderable(Text("hello"), svg=str(svg), html=str(html), width=20)
    assert "<svg" in svg.read_text(encoding="utf-8")
    assert "hello" in html.read_text(encoding="utf-8")


def test_export_bad_destination(tmp_path: Path) -> None:
    """An unwritable destination raises OSError carrying the filename."""
    with pytest.raises(OSError) as info:
        export_renderable(Text("x"), svg=str(tmp_path / "missing" / "a.svg"))
    assert info.value.filename
