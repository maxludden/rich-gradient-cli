"""Spectrum command wiring for the CLI."""

from __future__ import annotations

from typing import Literal, Optional

import click
import typer

from rich_gradient.spectrum import Spectrum

from .common import console, export_svg


def spectrum_command(
    hues: int = typer.Option(
        17,
        "--hues",
        "-h",
        metavar="HUES",
        help="Number of spectrum colors to generate.",
        show_default=True,
    ),
    invert: bool = typer.Option(
        False,
        "--invert",
        help="Reverse the generated spectrum colors.",
    ),
    seed: Optional[int] = typer.Option(
        None,
        "--seed",
        metavar="SEED",
        help="Seed used for deterministic color selection.",
    ),
    output: Literal["table", "names", "hex", "csv"] = typer.Option(
        "table",
        "--output",
        "-o",
        metavar="OUTPUT",
        help="Output format for the spectrum. Choices: table, names, hex, csv.",
        show_default=True,
        case_sensitive=False,
    ),
    end: str = typer.Option(
        "\n",
        "--end",
        metavar="END",
        help="String appended after the spectrum is printed.",
    ),
    svg: Optional[str] = typer.Option(
        None,
        "--svg",
        metavar="SVG",
        help="Save table output as an SVG file.",
    ),
) -> None:
    """Render rich-gradient's Spectrum color set."""
    try:
        spectrum = Spectrum(hues=hues, invert=invert, seed=seed)
    except ValueError as error:
        raise typer.BadParameter(str(error)) from error

    if svg and output != "table":
        raise click.UsageError("--svg is only supported with --output table.")
    if output == "names":
        console.print(",".join(spectrum.names), end=end)
        return
    if output == "hex":
        console.print(",".join(spectrum.hex), end=end)
        return
    if output == "csv":
        console.print("name,hex", end="\n")
        for name, hex_code in zip(spectrum.names, spectrum.hex):
            console.print(f"{name},{hex_code}", end="\n")
        return
    if svg:
        export_svg(spectrum.rich, svg, end=end)
        return
    console.print(spectrum.rich, end=end)


__all__ = ["spectrum_command"]
