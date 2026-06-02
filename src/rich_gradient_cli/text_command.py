"""Text/print command wiring for the CLI."""

from __future__ import annotations

import sys
from typing import Any, List, Literal, Optional, cast

import click
import typer
from rich.console import JustifyMethod, OverflowMethod

from rich_gradient.animated_text import AnimatedText
from rich_gradient.text import Text

from .common import console, export_svg, parse_colors, parse_style


def print_command(
    text: Optional[List[str]] = typer.Argument(None),
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
        7,
        "-h",
        "--hues",
        metavar="HUES",
        help="The number of hues to use for a random gradient.",
        show_default=True,
    ),
    style: Optional[str] = typer.Option(
        None,
        "--style",
        metavar="STYLE",
        help=(
            "The style to apply to the text. [dim italic]*Only non-color styles "
            "will be applied as the gradient's colors override color styles.[/]"
        ),
    ),
    justify: Literal["left", "center", "right"] = typer.Option(
        "left",
        "-j",
        "--justify",
        metavar="JUSTIFY",
        help="Justification of the text. [lime](left, center, right)[/]",
        show_default=True,
        case_sensitive=False,
    ),
    overflow: Literal["crop", "fold", "ellipsis"] = typer.Option(
        "fold",
        "--overflow",
        metavar="OVERFLOW",
        help="How to handle overflow of text. [lime](crop, fold, ellipsis)[/]",
        show_default=True,
        case_sensitive=False,
    ),
    no_wrap: bool = typer.Option(
        False,
        "--no-wrap",
        help="Disable wrapping of text.",
        show_default=True,
    ),
    tab_size: int = typer.Option(
        4,
        "--tab-size",
        metavar="TAB_SIZE",
        help="Number of spaces used to render tab characters.",
        show_default=True,
    ),
    markup: bool = typer.Option(
        True,
        "--markup/--no-markup",
        help="Parse Rich markup tags in input text.",
    ),
    end: str = typer.Option(
        "\n",
        "--end",
        metavar="END",
        help=(
            "String appended after the text is printed. [dim]\\[default: '\\n'][/dim]"
        ),
    ),
    bgcolors: Optional[str] = typer.Option(
        None,
        "--bgcolors",
        metavar="BGCOLORS",
        help="Optional comma separated string of background colors. [dim]If not provided, background is transparent.[/]",
    ),
    svg: Optional[str] = typer.Option(
        None,
        "--svg",
        metavar="SVG",
        help="Save output as an SVG file.",
    ),
    animate: bool = typer.Option(
        False,
        "-a",
        "--animate",
        help="Animate the gradient text.",
    ),
    duration: Optional[float] = typer.Option(
        None,
        "-d",
        "--duration",
        metavar="DURATION",
        help="Duration of the text animation in seconds (only used if --animate).",
    ),
    repeat_scale: float = typer.Option(
        4.0,
        "--repeat-scale",
        metavar="REPEAT_SCALE",
        help="Scale factor controlling the animated gradient repeat span.",
        show_default=True,
    ),
) -> None:
    """Print text in gradient color to the console."""
    if text:
        if len(text) == 1 and text[0] == "-":
            content = typer.get_text_stream("stdin").read().rstrip("\n")
            if not content:
                raise typer.BadParameter("Missing text argument.")
        else:
            content = " ".join(text)
    else:
        if sys.stdin.isatty():
            raise typer.BadParameter("Missing text argument.")
        content = typer.get_text_stream("stdin").read().rstrip("\n")
        if not content:
            raise typer.BadParameter("Missing text argument.")

    fg_list = parse_colors(colors)
    bg_list = parse_colors(bgcolors)
    style_obj = parse_style(style)
    if animate and svg:
        raise click.UsageError("--svg is not supported with --animate.")
    if animate and console.is_terminal is True:
        animated = AnimatedText(
            content,
            colors=fg_list,
            rainbow=rainbow,
            hues=hues,
            justify=cast(Any, justify),
            bg_colors=bg_list,
            text_kwargs={
                "style": style_obj,
                "overflow": overflow,
                "no_wrap": no_wrap,
                "end": end,
                "tab_size": tab_size,
            },
            markup=markup,
            repeat_scale=repeat_scale,
            animate=True,
            duration=duration,
        )
        animated.run()
        return

    gradient = Text(
        content,
        colors=fg_list,
        rainbow=rainbow,
        hues=hues,
        style=style_obj,
        justify=cast(JustifyMethod, justify),
        overflow=cast(OverflowMethod, overflow),
        end=end,
        no_wrap=no_wrap,
        tab_size=tab_size,
        bg_colors=bg_list,
        markup=markup,
    )
    if svg:
        export_svg(gradient, svg, end="")
        return
    console.print(gradient)


__all__ = ["print_command"]
