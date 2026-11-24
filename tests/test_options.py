"""Tests for the option parsers."""

import pytest

from rich_gradient_cli.options import (
    BOXES,
    parse_colors,
    parse_mapping,
    parse_padding,
    parse_style,
    validate_colors,
    validate_highlights,
)


def test_parse_colors() -> None:
    """Colors are split, stripped, and empties dropped."""
    assert parse_colors("red, #0ff ,,tomato") == ["red", "#0ff", "tomato"]
    assert parse_colors("") is None
    assert parse_colors(None) is None


def test_parse_style() -> None:
    """Valid styles parse; invalid ones raise ValueError."""
    assert parse_style("bold red").bold
    assert not parse_style(None)
    with pytest.raises(ValueError):
        parse_style("not-a-style-$$")


def test_parse_mapping() -> None:
    """KEY=VALUE pairs become a mapping."""
    assert parse_mapping(["a=bold", "b = red"]) == {"a": "bold", "b": "red"}
    assert parse_mapping(None) is None
    with pytest.raises(ValueError):
        parse_mapping(["nope"])


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("1", 1), ("1,2", (1, 2)), ("1,2,3,4", (1, 2, 3, 4)), (None, None)],
)
def test_parse_padding(raw: str | None, expected: object) -> None:
    """Padding accepts 1, 2, or 4 integers."""
    assert parse_padding(raw) == expected


@pytest.mark.parametrize("raw", ["1,2,3", "a", "-1"])
def test_parse_padding_invalid(raw: str) -> None:
    """Bad padding raises ValueError."""
    with pytest.raises(ValueError):
        parse_padding(raw)


def test_boxes() -> None:
    """Every documented box name is available."""
    assert set(BOXES) == {"ascii", "ascii2", "square", "rounded", "heavy", "double"}


def test_validate_colors() -> None:
    """Rich names, hex, #abc and CSS names pass; unknown names raise ValueError."""
    assert validate_colors("red,#abc,tomato") == ["red", "#abc", "tomato"]
    assert validate_colors(None) is None
    with pytest.raises(ValueError, match="notacolor"):
        validate_colors("red,notacolor")


@pytest.mark.parametrize(
    ("values", "regex"),
    [(["w=notastyle"], False), (["[=red"], True), (["x=boldd"], True)],
)
def test_validate_highlights_invalid(values: list[str], regex: bool) -> None:
    """Bad styles and bad patterns raise ValueError."""
    with pytest.raises(ValueError):
        validate_highlights(values, regex=regex)


def test_validate_highlights_valid() -> None:
    """Valid highlights return the parsed mapping."""
    assert validate_highlights([r"\d+=bold red"], regex=True) == {r"\d+": "bold red"}
