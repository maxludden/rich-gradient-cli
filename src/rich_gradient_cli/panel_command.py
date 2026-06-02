"""Panel command wiring for the CLI."""

from __future__ import annotations

import sys
from typing import Any, List, Literal, Optional, cast

import click
import typer
from rich.align import Align, AlignMethod

from rich_gradient.animated_panel import AnimatedPanel
from rich_gradient.panel import Panel

from .common import (
    console,
    export_svg,
    parse_colors,
    parse_mapping_options,
    parse_padding,
    parse_style,
)


def panel_command(
    renderable: str = typer.Argument(..., metavar="TEXT"),
    colors: Optional[str] = typer.Option(
        None,
        "-c",
        "--colors",
        metavar="COLORS",
        help=(
            "Comma-separated list of colors for the gradient. [dim](e.g., "
            "`[/][red]red[/][dim], [/][#ff9900]#ff9900[/][dim], [/][yellow]yellow[/][dim]`). "
            "If no colors are provided, the color stops are automatically generated."
        ),
    ),
    bgcolors: Optional[str] = typer.Option(
        None,
        "--bgcolors",
        metavar="BGCOLORS",
        help=(
            "Comma-separated list of background colors for the gradient. [dim](e.g., "
            "`[/][red]red[/][dim],[/][#ff9900]#ff9900[/][dim],[/][#ff0]#ff0[/][dim]`). "
            "Defaults to [/][bold #fff]transparent[/][dim].[/dim]"
        ),
    ),
    rainbow: bool = typer.Option(
        False,
        "-r",
        "--rainbow",
        help="[#ff0000]U[/][#ff3b00]s[/][#ff5100]e[/][#ff7400] [/]\
[#ff9000]r[/][#ffa900]a[/][#ffc000]i[/][#ffd700]n[/]\
[#ffee00]b[/][#f7ff00]o[/][#d3ff00]w[/][#a7ff00] [/] \
[#7dff00]c[/][#2eff00]o[/][#00ff64]l[/][#00ff8e]o[/][#00ffc0]r[/]\
[#00ffec]s[/][#00f4ff] [/][#00ddff]f[/][#00c5ff]o[/][#00afff]r[/]\
[#1596ff] [/][#3b81ff]t[/][#4e67ff]h[/][#675fff]e[/][#7b57ff] [/]\
[#924bff]g[/][#a73bff]r[/][#c72cff]a[/][#eb1cff]d[/][#ff00f2]i[/]\
[#ff00ce]e[/][#ff00a4]n[/][#ff0084]t[/][#ff0054].[/]",
    ),
    hues: int = typer.Option(
        5,
        "--hues",
        metavar="HUES",
        help="The number of hues to use for a random gradient.",
        show_default=True,
    ),
    title: Optional[str] = typer.Option(
        None,
        "-t",
        "--title",
        metavar="TITLE",
        help="Title of the panel.",
    ),
    title_style: str = typer.Option(
        "bold",
        "--title-style",
        metavar="TITLE_STYLE",
        help="Style of the panel title text (requires -t/--title).",
    ),
    title_align: Literal["left", "center", "right"] = typer.Option(
        "center",
        "--title-align",
        metavar="TITLE_ALIGN",
        help="Alignment of the panel title. [lime](left, center, right)[/]",
        show_default=True,
        case_sensitive=False,
    ),
    subtitle: Optional[str] = typer.Option(
        None,
        "-s",
        "--subtitle",
        metavar="SUBTITLE",
        help="Subtitle of the panel.",
    ),
    subtitle_style: Optional[str] = typer.Option(
        None,
        "--subtitle-style",
        metavar="SUBTITLE_STYLE",
        help="Style of the panel subtitle text (requires --subtitle).",
    ),
    subtitle_align: Literal["left", "center", "right"] = typer.Option(
        "right",
        "--subtitle-align",
        metavar="SUBTITLE_ALIGN",
        help="Alignment of the panel subtitle. [lime](left, center, right)[/]",
        show_default=True,
        case_sensitive=False,
    ),
    style: Optional[str] = typer.Option(
        None,
        "--style",
        metavar="STYLE",
        help="The style to apply to the panel.",
    ),
    border_style: Optional[str] = typer.Option(
        None,
        "--border-style",
        metavar="BORDER_STYLE",
        help=(
            "The style to apply to the panel border. [dim italic]*Only non-color styles "
            "will be applied as the gradient's colors override color styles.[/]"
        ),
    ),
    padding: Optional[str] = typer.Option(
        "0,1",
        "-p",
        "--padding",
        metavar="PADDING",
        help="Padding inside the panel (1, 2, or 4 comma-separated integers).",
    ),
    safe_box: bool = typer.Option(
        False,
        "--safe-box",
        help="Use box characters that are safe for legacy Windows terminals.",
    ),
    vertical_justify: Literal["top", "middle", "bottom"] = typer.Option(
        "top",
        "-V",
        "--vertical-justify",
        metavar="VERTICAL_JUSTIFY",
        help="Vertical justification of the panel inner text. [lime](top, middle, bottom)[/]",
        show_default=True,
        case_sensitive=False,
    ),
    text_justify: Literal["left", "center", "right"] = typer.Option(
        "left",
        "-J",
        "--text-justify",
        metavar="TEXT_JUSTIFY",
        help="Justification of the text inside the panel. [lime](left, center, right)[/]",
        show_default=True,
        case_sensitive=False,
    ),
    justify: Literal["left", "center", "right"] = typer.Option(
        "left",
        "-j",
        "--justify",
        metavar="JUSTIFY",
        help="Justification of the panel itself. [lime](left, center, right)[/]",
        show_default=True,
        case_sensitive=False,
    ),
    expand: bool = typer.Option(
        True,
        "--expand/--no-expand",
        help="Whether to expand the panel to fill the width.",
    ),
    width: Optional[int] = typer.Option(
        None,
        "--width",
        metavar="WIDTH",
        help="Width of the panel (requires --no-expand if set).",
    ),
    height: Optional[int] = typer.Option(
        None,
        "--height",
        metavar="HEIGHT",
        help="Height of the panel; content determines by default.",
    ),
    highlight_words: Optional[List[str]] = typer.Option(
        None,
        "--highlight-word",
        metavar="WORD=STYLE",
        help="Highlight a word or phrase with a Rich style. May be repeated.",
    ),
    highlight_regex: Optional[List[str]] = typer.Option(
        None,
        "--highlight-regex",
        metavar="PATTERN=STYLE",
        help="Highlight a regex pattern with a Rich style. May be repeated.",
    ),
    end: str = typer.Option(
        "\n",
        "--end",
        metavar="END",
        help=(
            "String appended after the text is printed. [dim]\\[default: '\\n'][/dim]"
        ),
    ),
    box: Literal["SQUARE", "ROUNDED", "HEAVY", "DOUBLE", "ASCII"] = typer.Option(
        "ROUNDED",
        "--box",
        metavar="BOX",
        help=(
            "Box style for the panel border. [dim](e.g., SQUARE, ROUNDED, HEAVY, "
            "DOUBLE, ASCII).[/dim]"
        ),
        case_sensitive=False,
    ),
    animate: bool = typer.Option(
        False,
        "-a",
        "--animate",
        help="Animate the panel gradient.",
    ),
    duration: float = typer.Option(
        5.0,
        "-d",
        "--duration",
        metavar="DURATION",
        help="Duration of the panel animation in seconds (only used if --animate).",
    ),
    repeat_scale: float = typer.Option(
        4.0,
        "--repeat-scale",
        metavar="REPEAT_SCALE",
        help="Scale factor controlling the animated gradient repeat span.",
        show_default=True,
    ),
    svg: Optional[str] = typer.Option(
        None,
        "--svg",
        metavar="SVG",
        help="Save output as an SVG file.",
    ),
) -> None:
    """Display a renderable inside a gradient panel."""
    if renderable == "-":
        renderable = typer.get_text_stream("stdin").read().rstrip("\n")
        if not renderable:
            raise click.UsageError("Missing text argument.")

    fg_list = parse_colors(colors)
    bg_list = parse_colors(bgcolors)
    style_obj = parse_style(style)
    _text_justify = cast(AlignMethod, text_justify)
    try:
        padding_value = parse_padding(padding)
        highlight_word_map = parse_mapping_options(highlight_words)
        highlight_regex_map = parse_mapping_options(highlight_regex)
    except ValueError as error:
        raise typer.BadParameter(str(error)) from error

    from rich import box as rich_box

    box_map: dict[str, Any] = {
        "SQUARE": rich_box.SQUARE,
        "ROUNDED": rich_box.ROUNDED,
        "HEAVY": rich_box.HEAVY,
        "DOUBLE": rich_box.DOUBLE,
        "ASCII": rich_box.ASCII,
    }
    box_style = box_map.get(box.upper(), rich_box.ROUNDED)

    if animate and svg:
        raise click.UsageError("--svg is not supported with --animate.")
    if animate and console.is_terminal is True:
        animated_panel: AnimatedPanel = AnimatedPanel(
            Align(renderable, align=_text_justify),
            colors=cast(Any, fg_list),
            rainbow=rainbow,
            hues=hues,
            bg_colors=cast(Any, bg_list),
            title=title,
            title_style=parse_style(title_style),
            title_align=cast(AlignMethod, title_align),
            subtitle=subtitle,
            subtitle_style=parse_style(subtitle_style),
            subtitle_align=cast(AlignMethod, subtitle_align),
            style=style_obj,
            border_style=parse_style(border_style),
            padding=cast(Any, padding_value),
            vertical_justify=cast(Any, vertical_justify),
            justify=cast(AlignMethod, justify),
            expand=expand,
            width=width,
            height=height,
            box=box_style,
            safe_box=safe_box,
            highlight_words=highlight_word_map,
            highlight_regex=highlight_regex_map,
            repeat_scale=repeat_scale,
            animate=True,
            duration=duration,
        )
        animated_panel.run()
        sys.exit(0)

    panel = Panel(
        Align(renderable, align=_text_justify),
        colors=cast(Any, fg_list),
        rainbow=rainbow,
        hues=hues,
        bg_colors=cast(Any, bg_list),
        title=title,
        title_style=parse_style(title_style),
        title_align=cast(AlignMethod, title_align),
        subtitle=subtitle,
        subtitle_style=parse_style(subtitle_style),
        subtitle_align=cast(AlignMethod, subtitle_align),
        style=style_obj,
        border_style=parse_style(border_style),
        padding=cast(Any, padding_value),
        vertical_justify=cast(Any, vertical_justify),
        justify=cast(AlignMethod, justify),
        expand=expand,
        width=width,
        height=height,
        box=box_style,
        safe_box=safe_box,
        highlight_words=highlight_word_map,
        highlight_regex=highlight_regex_map,
    )
    if svg:
        export_svg(panel, svg, end=end)
        return
    console.print(panel, end=end)


__all__ = ["panel_command"]
