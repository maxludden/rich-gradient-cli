"""Tests for the option parsers."""

import pytest

from rich_gradient_cli.options import (
    BOXES,
    parse_colors,
    parse_mapping,
    parse_padding,
    parse_style,
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
