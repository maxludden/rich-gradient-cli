"""Export renderables to SVG or HTML files."""

from __future__ import annotations

import io
from pathlib import Path

from rich.console import Console, RenderableType
from rich_gradient.theme import GRADIENT_TERMINAL_THEME


def export_renderable(
    renderable: RenderableType,
    *,
    svg: str | None = None,
    html: str | None = None,
    width: int | None = None,
) -> None:
    """Render ``renderable`` to a recording console and save SVG and/or HTML.

    Args:
        renderable: What to render.
        svg: Destination SVG path, if any.
        html: Destination HTML path, if any.
        width: Console width in cells; defaults to Rich's detected width.

    Raises:
        OSError: If a destination cannot be written.
    """
    recorder = Console(
        record=True,
        force_terminal=True,
        color_system="truecolor",
        width=width,
        file=io.StringIO(),
    )
    recorder.print(renderable)
    if svg:
        Path(svg).write_text(
            recorder.export_svg(
                title="rich-gradient", theme=GRADIENT_TERMINAL_THEME, clear=False
            ),
            encoding="utf-8",
        )
    if html:
        Path(html).write_text(
            recorder.export_html(theme=GRADIENT_TERMINAL_THEME), encoding="utf-8"
        )


__all__ = ["export_renderable"]
