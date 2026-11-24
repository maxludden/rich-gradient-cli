"""Parsers that turn raw command-line strings into typed values."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence

# Importing rich_gradient patches ``Color.parse`` (via rich-color-ext) so it also
# accepts CSS color names and ``#abc`` shorthand, matching what the gradients use.
import rich_gradient  # noqa: F401
from rich import box
from rich.box import Box
from rich.color import Color, ColorParseError
from rich.style import Style

#: Panel box names accepted by ``--box``, mapped to Rich boxes.
BOXES: dict[str, Box] = {
    "ascii": box.ASCII,
    "ascii2": box.ASCII2,
    "square": box.SQUARE,
    "rounded": box.ROUNDED,
    "heavy": box.HEAVY,
    "double": box.DOUBLE,
}


def parse_colors(colors: str | None) -> list[str] | None:
    """Split a comma-separated color list.

    Args:
        colors: Raw ``--colors`` value, e.g. ``"red,#0ff,tomato"``.

    Returns:
        The stripped, non-empty tokens, or ``None`` when ``colors`` is empty.
    """
    if not colors:
        return None
    parsed = [token.strip() for token in colors.split(",") if token.strip()]
    return parsed or None


def validate_colors(colors: str | None) -> list[str] | None:
    """Split a comma-separated color list and check every color parses.

    Raises:
        ValueError: If any token is not a Rich color, hex code, or CSS name.
    """
    parsed = parse_colors(colors)
    for token in parsed or []:
        try:
            Color.parse(token)
        except ColorParseError as exc:
            raise ValueError(f"Invalid color {token!r}.") from exc
    return parsed


def parse_style(style: str | None) -> Style:
    """Parse a Rich style string, returning a null style when empty.

    Raises:
        ValueError: If ``style`` is not a valid Rich style.
    """
    if not style:
        return Style.null()
    try:
        return Style.parse(style)
    except Exception as exc:  # rich raises StyleSyntaxError
        raise ValueError(f"Invalid style {style!r}: {exc}") from exc


def parse_mapping(values: Sequence[str] | None) -> Mapping[str, str] | None:
    """Parse repeated ``KEY=VALUE`` options into a mapping.

    Raises:
        ValueError: If an item is not of the form ``KEY=VALUE``.
    """
    if not values:
        return None
    parsed: dict[str, str] = {}
    for item in values:
        key, separator, value = item.partition("=")
        key, value = key.strip(), value.strip()
        if not separator or not key or not value:
            raise ValueError(f"Expected KEY=VALUE, got {item!r}.")
        parsed[key] = value
    return parsed


def validate_highlights(
    values: Sequence[str] | None, *, regex: bool = False
) -> Mapping[str, str] | None:
    """Parse ``KEY=STYLE`` highlights, checking each style (and pattern if ``regex``).

    Raises:
        ValueError: On a malformed item, an invalid style, or an invalid regex.
    """
    mapping = parse_mapping(values)
    for key, value in (mapping or {}).items():
        parse_style(value)
        if regex:
            try:
                re.compile(key)
            except re.error as exc:
                raise ValueError(f"Invalid regex {key!r}: {exc}") from exc
    return mapping


def parse_padding(padding: str | None) -> int | tuple[int, int] | tuple[int, int, int, int] | None:
    """Parse CSS-style padding such as ``"1"``, ``"1,2"`` or ``"1,2,3,4"``.

    Raises:
        ValueError: If the string is not 1, 2 or 4 comma-separated integers.
    """
    if not padding:
        return None
    try:
        parts = tuple(int(part) for part in padding.split(",") if part.strip())
    except ValueError as exc:
        raise ValueError("Padding must be integers, e.g. 1 or 1,2 or 1,2,3,4.") from exc
    if any(part < 0 for part in parts):
        raise ValueError("Padding cannot be negative.")
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return (parts[0], parts[1])
    if len(parts) == 4:
        return (parts[0], parts[1], parts[2], parts[3])
    raise ValueError("Padding must contain 1, 2, or 4 comma-separated integers.")


__all__ = [
    "BOXES",
    "parse_colors",
    "parse_mapping",
    "parse_padding",
    "parse_style",
    "validate_colors",
    "validate_highlights",
]
