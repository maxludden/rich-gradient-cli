"""Generic gradient command wiring for the CLI."""

from __future__ import annotations

from typing import List, Literal, Optional

import click
import typer

from .common import render_gradient_output


def gradient_command(
    renderable: str = typer.Argument(..., metavar="TEXT"),
    colors: Optional[str] = typer.Option(
        None,
        "-c",
        "--colors",
        metavar="COLORS",
        help="Comma-separated list of foreground colors for the gradient.",
    ),
    bgcolors: Optional[str] = typer.Option(
        None,
        "--bgcolors",
        metavar="BGCOLORS",
        help="Comma-separated list of background colors for the gradient.",
    ),
    rainbow: bool = typer.Option(
        False,
        "-r",
        "--rainbow",
        help="Use rainbow colors for the gradient.",
    ),
    hues: int = typer.Option(
        5,
        "--hues",
        metavar="HUES",
        help="The number of hues to use when colors are generated.",
        show_default=True,
    ),
    expand: bool = typer.Option(
        True,
        "--expand/--no-expand",
        help="Whether to expand the renderable to fill the console width.",
    ),
    justify: Literal["left", "center", "right"] = typer.Option(
        "left",
        "-j",
        "--justify",
        metavar="JUSTIFY",
        help="Horizontal justification of the gradient renderable.",
        show_default=True,
        case_sensitive=False,
    ),
    vertical_justify: Literal["top", "middle", "bottom"] = typer.Option(
        "middle",
        "--vertical-justify",
        metavar="VERTICAL_JUSTIFY",
        help="Vertical justification of the gradient renderable.",
        show_default=True,
        case_sensitive=False,
    ),
    repeat_scale: float = typer.Option(
        2.0,
        "--repeat-scale",
        metavar="REPEAT_SCALE",
        help="Scale factor controlling the gradient repeat span.",
        show_default=True,
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
        help="String appended after the gradient is printed.",
    ),
    animate: bool = typer.Option(
        False,
        "-a",
        "--animate",
        help="Animate the generic gradient.",
    ),
    duration: Optional[float] = typer.Option(
        None,
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
    """Render text through rich-gradient's generic Gradient renderable."""
    if renderable == "-":
        renderable = typer.get_text_stream("stdin").read().rstrip("\n")
        if not renderable:
            raise click.UsageError("Missing text argument.")

    try:
        render_gradient_output(
            renderable,
            colors=colors,
            bgcolors=bgcolors,
            rainbow=rainbow,
            hues=hues,
            expand=expand,
            justify=justify,
            vertical_justify=vertical_justify,
            repeat_scale=repeat_scale,
            highlight_words=highlight_words,
            highlight_regex=highlight_regex,
            end=end,
            animate=animate,
            duration=duration,
            svg=svg,
        )
    except ValueError as error:
        message = str(error)
        if "--svg" in message:
            raise click.UsageError(message) from error
        raise typer.BadParameter(message) from error


__all__ = ["gradient_command"]
