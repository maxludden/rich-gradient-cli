"""Shared helpers and configuration for the rich-gradient CLI."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, List, Mapping, Optional, Sequence, cast

from rich.console import Console, RenderableType
from rich.padding import Padding
from rich.style import Style
from rich_gradient.animated_gradient import AnimatedGradient
from rich_gradient.gradient import Gradient
from rich_gradient.theme import GRADIENT_TERMINAL_THEME

console = Console()
try:
    VERSION = version("rich-gradient-cli")
except PackageNotFoundError:
    VERSION = "0.0.0"

HEADER_TEXT = (
    "[#ff5500]r[/][#ff6f00]i[/][#ff8300]c[/]"
    "[#ff9500]h[/][#ffa600]-[/][#ffb600]g[/][#ffc500]r[/]"
    "[#ffd400]a[/][#ffe500]d[/][#fff400]i[/][#f9ff00]e[/]"
    "[#e2ff00]n[/][#c8ff00]t[/][#a9ff00] [/][bold #fff]CLI[/]"
)

FOOTER_TEXT = (
    "[#ff5500]\U0001f308[/][#ff7400] [/][#ff8c00]h[/]"
    "[#ffa100]t[/][#ffb500]t[/][#ffc700]p[/][#ffdc00]s[/]"
    "[#ffef00]:[/][#fbff00]/[/][#dfff00]/[/][#bdff00]m[/]"
    "[#9aff00]a[/][#73ff00]x[/][#2aff00]l[/][#00ff5c]u[/]"
    "[#00ff83]d[/][#00ffa6]d[/][#00ffd1]e[/][#00fff3]n[/]"
    "[#00f4ff].[/][#00e1ff]g[/][#00ccff]i[/][#00baff]t[/]"
    "[#00a6ff]h[/][#2192ff]u[/][#3b81ff]b[/][#4c6cff].[/]"
    "[#6061ff]i[/][#725bff]o[/][#8253ff]/[/][#9648ff]r[/]"
    "[#a83bff]i[/][#c22eff]c[/][#e122ff]h[/][#fb0cff]-[/]"
    "[#ff00e6]g[/][#ff00c6]r[/][#ff00a4]a[/][#ff0089]d[/]"
    "[#ff0066]i[/][#ff004b]e[/][#ff0036]n[/][#ff0000]t[/]"
)


USAGE_PREFIX = "[bold #00ff00]Usage:[/]"
USAGE_PROG_STYLE = "#af00ff"
USAGE_CMD_STYLE = "#0099ff"
USAGE_BRACKET_STYLE = "#ffffff"


def parse_colors(colors: Optional[str]) -> Optional[List[str]]:
    """Parse comma-separated color tokens into a list."""
    if colors is None:
        return None
    return [c.strip() for c in colors.split(",") if c.strip()]


def parse_style(style: Optional[str]) -> Style:
    """Parse a Rich style string or return a null style."""
    if style is None:
        return Style.null()
    return Style.parse(style)


def parse_mapping_options(values: Optional[Sequence[str]]) -> Optional[Mapping[str, str]]:
    """Parse repeated KEY=VALUE CLI options into a mapping."""
    if not values:
        return None

    parsed: dict[str, str] = {}
    for value in values:
        key, separator, item_value = value.partition("=")
        key = key.strip()
        item_value = item_value.strip()
        if not separator or not key or not item_value:
            raise ValueError(f"Expected KEY=VALUE, got {value!r}.")
        parsed[key] = item_value
    return parsed


def parse_padding(padding: Optional[str]) -> int | tuple[int, ...] | None:
    """Parse Rich padding shorthand from a CLI string."""
    if padding is None:
        return None

    parts = tuple(int(part) for part in padding.split(",") if part.strip())
    if len(parts) not in {1, 2, 4}:
        raise ValueError("Padding must contain 1, 2, or 4 comma-separated integers.")
    if len(parts) == 1:
        return parts[0]
    return parts


def export_svg(
    renderable: RenderableType, svg_path: str, *, end: str = "\n", no_wrap: bool = False
) -> None:
    """Render a Rich renderable to an SVG file."""
    svg_console = Console(record=True, force_terminal=True, color_system="truecolor")
    padded = Padding(renderable, (1, 4))
    svg_console.print(padded, end=end, no_wrap=no_wrap)

    Path(svg_path).write_text(
        svg_console.export_svg(
            title="rich-gradient",
            theme=GRADIENT_TERMINAL_THEME,
        ),
        encoding="utf-8",
    )


def render_gradient_output(
    renderable: RenderableType,
    *,
    colors: Optional[str] = None,
    bgcolors: Optional[str] = None,
    rainbow: bool = False,
    hues: int = 5,
    expand: bool = True,
    justify: str = "left",
    vertical_justify: str = "middle",
    repeat_scale: float = 2.0,
    highlight_words: Optional[Sequence[str]] = None,
    highlight_regex: Optional[Sequence[str]] = None,
    end: str = "\n",
    animate: bool = False,
    duration: Optional[float] = None,
    svg: Optional[str] = None,
) -> None:
    """Render any Rich renderable through rich-gradient's Gradient wrapper."""
    fg_list = parse_colors(colors)
    bg_list = parse_colors(bgcolors)
    highlight_word_map = parse_mapping_options(highlight_words)
    highlight_regex_map = parse_mapping_options(highlight_regex)

    if animate and svg:
        raise ValueError("--svg is not supported with --animate.")
    if animate and console.is_terminal is True:
        animated = AnimatedGradient(
            cast(Any, renderable),
            colors=cast(Any, fg_list),
            bg_colors=cast(Any, bg_list),
            hues=hues,
            rainbow=rainbow,
            expand=expand,
            justify=cast(Any, justify),
            vertical_justify=cast(Any, vertical_justify),
            repeat_scale=repeat_scale,
            highlight_words=highlight_word_map,
            highlight_regex=highlight_regex_map,
            animate=True,
            duration=duration,
        )
        animated.run()
        return

    gradient = Gradient(
        cast(Any, renderable),
        colors=cast(Any, fg_list),
        bg_colors=cast(Any, bg_list),
        hues=hues,
        rainbow=rainbow,
        expand=expand,
        justify=cast(Any, justify),
        vertical_justify=cast(Any, vertical_justify),
        repeat_scale=repeat_scale,
        highlight_words=highlight_word_map,
        highlight_regex=highlight_regex_map,
    )
    if svg:
        export_svg(gradient, svg, end=end)
        return
    console.print(gradient, end=end)


__all__ = [
    "VERSION",
    "console",
    "parse_colors",
    "parse_mapping_options",
    "parse_padding",
    "parse_style",
    "render_gradient_output",
    "HEADER_TEXT",
    "FOOTER_TEXT",
    "USAGE_PREFIX",
    "USAGE_PROG_STYLE",
    "USAGE_CMD_STYLE",
    "USAGE_BRACKET_STYLE",
    "export_svg",
]
