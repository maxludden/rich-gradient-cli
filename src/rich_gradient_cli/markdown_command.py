"""Markdown command wiring for the CLI."""

from __future__ import annotations

from typing import Any, Literal, Optional, cast

import typer
from rich.align import AlignMethod, VerticalAlignMethod

from rich_gradient.animated_markdown import AnimatedMarkdown
from rich_gradient.markdown import Markdown

from .common import console, export_svg, parse_colors, parse_style


def markdown_command(
    markdown: str = typer.Argument(..., metavar="MARKDOWN"),
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
            "`[/][red]red[/][dim], [/][#ff9900]#ff9900[/][dim], [/][#ff0]#ff0[/][dim]`). "
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
        7,
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
            "The style to apply to the markdown text. [dim italic]*Only non-color styles "
            "will be applied as the gradient's colors override color styles.[/]"
        ),
    ),
    justify: Literal["left", "center", "right"] = typer.Option(
        "left",
        "-j",
        "--justify",
        metavar="JUSTIFY",
        help="Justification of the markdown text. [lime](left, center, right)[/]",
        show_default=True,
        case_sensitive=False,
    ),
    vertical_justify: Literal["top", "middle", "bottom"] = typer.Option(
        "top",
        "--vertical-justify",
        metavar="VERTICAL_JUSTIFY",
        help="Vertical justification of the markdown text. [lime](top, middle, bottom)[/]",
        show_default=True,
        case_sensitive=False,
    ),
    no_wrap: bool = typer.Option(
        False,
        "--no-wrap",
        help="Disable wrapping of markdown text.",
        show_default=True,
    ),
    end: str = typer.Option(
        "\n",
        "--end",
        metavar="END",
        help=(
            "String appended after the text is printed. [dim]\\[default: '\\n'][/dim]"
        ),
    ),
    animate: bool = typer.Option(
        False,
        "--animate",
        help="Animate the gradient markdown text.",
    ),
    duration: float = typer.Option(
        5.0,
        "-d",
        "--duration",
        metavar="DURATION",
        help="Duration of the animation in seconds (only used if --animate).",
    ),
    svg: Optional[str] = typer.Option(
        None,
        "--svg",
        metavar="SVG",
        help="Save output as an SVG file.",
    ),
) -> None:
    """Render markdown text with gradient colors in a rich console."""
    if markdown == "-":
        markdown = typer.get_text_stream("stdin").read().rstrip("\n")
        if not markdown:
            raise typer.UsageError("Missing markdown argument.")

    _colors = parse_colors(colors)
    _bgcolors = parse_colors(bgcolors)
    markdown_kwargs: dict[str, Any] = {}
    if style:
        markdown_kwargs["style"] = parse_style(style)

    justify_value = cast(AlignMethod, justify)
    vertical_value = cast(VerticalAlignMethod, vertical_justify)

    if animate and svg:
        raise typer.UsageError("--svg is not supported with --animate.")
    if animate and console.is_terminal is True:
        console.clear()
        animated = AnimatedMarkdown(
            markdown,
            colors=_colors,
            rainbow=rainbow,
            hues=hues,
            justify=justify_value,
            vertical_justify=vertical_value,
            bg_colors=_bgcolors,
            markdown_kwargs=markdown_kwargs or None,
            animate=True,
            duration=duration,
        )
        animated.run()
        return

    md = Markdown(
        markdown,
        colors=_colors,
        rainbow=rainbow,
        hues=hues,
        justify=justify_value,
        vertical_justify=vertical_value,
        bg_colors=_bgcolors,
        markdown_kwargs=markdown_kwargs or None,
    )
    if svg:
        export_svg(md, svg, end=end, no_wrap=no_wrap)
        return
    console.print(md, end=end, no_wrap=no_wrap)


__all__ = ["markdown_command"]
