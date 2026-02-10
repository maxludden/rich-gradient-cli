"""Rule command wiring for the CLI."""

from __future__ import annotations

from typing import Literal, Optional, cast

import typer
from rich.align import AlignMethod

from rich_gradient.rule import Rule

from .common import console, export_svg, parse_colors, parse_style


def rule_command(
    title: Optional[str] = typer.Option(
        None,
        "-t",
        "--title",
        metavar="TITLE",
        help="Title of the rule.",
    ),
    title_style: Optional[str] = typer.Option(
        "bold",
        "-s",
        "--title-style",
        metavar="TITLE_STYLE",
        help=(
            "The style of the rule's title text. [dim italic]*Only non-color styles "
            "will be applied as the gradient's colors override color styles.[/]"
        ),
        show_default=True,
    ),
    colors: Optional[str] = typer.Option(
        "",
        "-c",
        "--colors",
        metavar="COLORS",
        help=(
            "Comma-separated list of colors for the gradient. [dim](e.g., "
            "`[/][red]red[/][dim], [/][#ff9900]#ff9900[/][dim], [/][yellow]yellow[/][dim]`)."
        ),
        show_default=True,
    ),
    bgcolors: Optional[str] = typer.Option(
        "",
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
        10,
        "--hues",
        metavar="HUES",
        help="The number of hues to use for a random gradient.",
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
    thickness: int = typer.Option(
        2,
        "-T",
        "--thickness",
        metavar="THICKNESS",
        help="Thickness of the rule line (choices 0-3).",
    ),
    align: Literal["left", "center", "right"] = typer.Option(
        "center",
        "-a",
        "--align",
        metavar="ALIGN",
        help="Alignment of the rule in the console. [lime](left, center, right)[/]",
        show_default=True,
        case_sensitive=False,
    ),
    svg: Optional[str] = typer.Option(
        None,
        "--svg",
        metavar="SVG",
        help="Save output as an SVG file.",
    ),
) -> None:
    """Display a gradient rule in the console."""
    _colors = parse_colors(colors)
    _bgcolors = parse_colors(bgcolors)
    _title_style = parse_style(title_style)

    rule = Rule(
        title=title or "",
        title_style=_title_style,
        colors=_colors,
        rainbow=rainbow,
        hues=hues,
        bg_colors=_bgcolors,
        thickness=thickness,
        end=end,
        align=cast(AlignMethod, align),
    )
    if svg:
        export_svg(rule, svg, end=end)
        return
    console.print(rule)


__all__ = ["rule_command"]
