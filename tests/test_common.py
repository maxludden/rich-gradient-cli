from rich.style import Style

from rich_gradient_cli.common import parse_colors, parse_style


def test_parse_colors_splits_and_trims() -> None:
    assert parse_colors(" red, #ff9900 ,blue ") == ["red", "#ff9900", "blue"]


def test_parse_colors_none() -> None:
    assert parse_colors(None) is None


def test_parse_style_none_returns_null_style() -> None:
    assert parse_style(None) == Style.null()

