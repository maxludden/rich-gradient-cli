"""Rich renderable command wiring for gradient wrappers."""

from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import Any, Iterable, List, Literal, Optional, cast

import click
import typer
from rich.columns import Columns
from rich.syntax import Syntax
from rich.table import Table
from rich.tree import Tree

from .common import parse_padding, render_gradient_output


def _read_text_argument(value: str, *, label: str) -> str:
    """Read a text CLI argument, supporting '-' for stdin."""
    if value == "-":
        content = typer.get_text_stream("stdin").read().rstrip("\n")
        if not content:
            raise click.UsageError(f"Missing {label} argument.")
        return content
    return value


def _render_with_gradient(
    renderable: object,
    *,
    colors: Optional[str],
    bgcolors: Optional[str],
    rainbow: bool,
    hues: int,
    expand: bool,
    justify: str,
    vertical_justify: str,
    repeat_scale: float,
    highlight_words: Optional[List[str]],
    highlight_regex: Optional[List[str]],
    end: str,
    animate: bool,
    duration: Optional[float],
    svg: Optional[str],
) -> None:
    """Render a Rich object with consistent gradient error handling."""
    try:
        render_gradient_output(
            renderable,  # type: ignore[arg-type]
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


def columns_command(
    items: Optional[List[str]] = typer.Argument(None, metavar="ITEM..."),
    colors: Optional[str] = typer.Option(
        None, "-c", "--colors", metavar="COLORS", help="Comma-separated gradient colors."
    ),
    bgcolors: Optional[str] = typer.Option(
        None,
        "--bgcolors",
        metavar="BGCOLORS",
        help="Comma-separated background colors.",
    ),
    rainbow: bool = typer.Option(False, "-r", "--rainbow", help="Use rainbow colors."),
    hues: int = typer.Option(
        5, "--hues", metavar="HUES", help="Number of generated hues.", show_default=True
    ),
    padding: Optional[str] = typer.Option(
        "0,1", "-p", "--padding", metavar="PADDING", help="Column padding."
    ),
    width: Optional[int] = typer.Option(
        None, "--width", metavar="WIDTH", help="Fixed column width."
    ),
    columns_expand: bool = typer.Option(
        False, "--columns-expand", help="Expand columns to the console width."
    ),
    equal: bool = typer.Option(False, "--equal", help="Use equal-width columns."),
    column_first: bool = typer.Option(
        False, "--column-first", help="Fill columns before rows."
    ),
    right_to_left: bool = typer.Option(
        False, "--right-to-left", help="Render columns from right to left."
    ),
    align: Optional[Literal["left", "center", "right"]] = typer.Option(
        None,
        "--align",
        metavar="ALIGN",
        help="Alignment inside each column.",
        case_sensitive=False,
    ),
    title: Optional[str] = typer.Option(None, "--title", metavar="TITLE", help="Title."),
    expand: bool = typer.Option(
        True, "--expand/--no-expand", help="Expand the gradient wrapper."
    ),
    justify: Literal["left", "center", "right"] = typer.Option(
        "left", "-j", "--justify", help="Gradient justification.", case_sensitive=False
    ),
    vertical_justify: Literal["top", "middle", "bottom"] = typer.Option(
        "middle",
        "--vertical-justify",
        help="Gradient vertical justification.",
        case_sensitive=False,
    ),
    repeat_scale: float = typer.Option(
        2.0, "--repeat-scale", help="Gradient repeat scale.", show_default=True
    ),
    highlight_words: Optional[List[str]] = typer.Option(
        None, "--highlight-word", metavar="WORD=STYLE", help="Highlight word style."
    ),
    highlight_regex: Optional[List[str]] = typer.Option(
        None, "--highlight-regex", metavar="PATTERN=STYLE", help="Highlight regex style."
    ),
    end: str = typer.Option("\n", "--end", metavar="END", help="String appended after output."),
    animate: bool = typer.Option(False, "-a", "--animate", help="Animate gradient."),
    duration: Optional[float] = typer.Option(
        None, "-d", "--duration", metavar="DURATION", help="Animation duration."
    ),
    svg: Optional[str] = typer.Option(None, "--svg", metavar="SVG", help="Save SVG."),
) -> None:
    """Render Rich Columns through a gradient wrapper."""
    if not items:
        items = typer.get_text_stream("stdin").read().splitlines()
    if not items:
        raise click.UsageError("Missing item arguments.")
    try:
        padding_value = parse_padding(padding)
    except ValueError as error:
        raise typer.BadParameter(str(error)) from error

    columns = Columns(
        items,
        padding=cast(Any, padding_value or 0),
        width=width,
        expand=columns_expand,
        equal=equal,
        column_first=column_first,
        right_to_left=right_to_left,
        align=align,
        title=title,
    )
    _render_with_gradient(
        columns,
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


def _add_tree_path(root: Tree, path: str) -> None:
    """Add a slash-delimited path to a Rich tree."""
    node = root
    for part in [item for item in path.split("/") if item]:
        match = next(
            (
                child
                for child in node.children
                if getattr(child.label, "plain", str(child.label)) == part
            ),
            None,
        )
        node = match if match is not None else node.add(part)


def _iter_directory_paths(path: Path, *, max_depth: int) -> Iterable[str]:
    """Yield relative directory entries up to a maximum depth."""
    base_depth = len(path.parts)
    for dirpath, dirnames, filenames in os.walk(path):
        current = Path(dirpath)
        depth = len(current.parts) - base_depth
        if depth >= max_depth:
            dirnames[:] = []
        for dirname in sorted(dirnames):
            yield str((current / dirname).relative_to(path))
        for filename in sorted(filenames):
            yield str((current / filename).relative_to(path))


def tree_command(
    root: str = typer.Argument(..., metavar="ROOT"),
    branches: Optional[List[str]] = typer.Argument(None, metavar="BRANCH..."),
    path: bool = typer.Option(False, "--path", help="Treat ROOT as a directory path."),
    max_depth: int = typer.Option(
        2, "--max-depth", metavar="DEPTH", help="Maximum directory depth.", show_default=True
    ),
    style: str = typer.Option("tree", "--style", metavar="STYLE", help="Tree style."),
    guide_style: str = typer.Option(
        "tree.line", "--guide-style", metavar="STYLE", help="Guide line style."
    ),
    expanded: bool = typer.Option(True, "--expanded/--collapsed", help="Expand tree."),
    highlight: bool = typer.Option(False, "--highlight", help="Highlight labels."),
    hide_root: bool = typer.Option(False, "--hide-root", help="Hide the root label."),
    colors: Optional[str] = typer.Option(
        None, "-c", "--colors", metavar="COLORS", help="Comma-separated gradient colors."
    ),
    bgcolors: Optional[str] = typer.Option(None, "--bgcolors", metavar="BGCOLORS"),
    rainbow: bool = typer.Option(False, "-r", "--rainbow", help="Use rainbow colors."),
    hues: int = typer.Option(5, "--hues", metavar="HUES", show_default=True),
    expand: bool = typer.Option(True, "--expand/--no-expand", help="Expand wrapper."),
    justify: Literal["left", "center", "right"] = typer.Option(
        "left", "-j", "--justify", case_sensitive=False
    ),
    vertical_justify: Literal["top", "middle", "bottom"] = typer.Option(
        "middle", "--vertical-justify", case_sensitive=False
    ),
    repeat_scale: float = typer.Option(2.0, "--repeat-scale", show_default=True),
    highlight_words: Optional[List[str]] = typer.Option(None, "--highlight-word"),
    highlight_regex: Optional[List[str]] = typer.Option(None, "--highlight-regex"),
    end: str = typer.Option("\n", "--end"),
    animate: bool = typer.Option(False, "-a", "--animate"),
    duration: Optional[float] = typer.Option(None, "-d", "--duration"),
    svg: Optional[str] = typer.Option(None, "--svg", metavar="SVG"),
) -> None:
    """Render a Rich Tree through a gradient wrapper."""
    root_path = Path(root)
    tree = Tree(
        root_path.name if path else root,
        style=style,
        guide_style=guide_style,
        expanded=expanded,
        highlight=highlight,
        hide_root=hide_root,
    )
    if path:
        if not root_path.exists():
            raise typer.BadParameter(f"Path does not exist: {root}")
        for branch in _iter_directory_paths(root_path, max_depth=max_depth):
            _add_tree_path(tree, branch)
    else:
        for branch in branches or []:
            _add_tree_path(tree, branch)
    _render_with_gradient(
        tree,
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


def syntax_command(
    source: str = typer.Argument(..., metavar="PATH_OR_CODE"),
    lexer: Optional[str] = typer.Option(None, "-x", "--lexer", metavar="LEXER"),
    theme: str = typer.Option("monokai", "--theme", metavar="THEME", help="Pygments theme."),
    line_numbers: bool = typer.Option(False, "-n", "--line-numbers", help="Show line numbers."),
    word_wrap: bool = typer.Option(False, "--word-wrap", help="Enable word wrapping."),
    indent_guides: bool = typer.Option(False, "-g", "--guides", help="Show indent guides."),
    dedent: bool = typer.Option(False, "--dedent", help="Dedent code before rendering."),
    start_line: int = typer.Option(1, "--start-line", metavar="LINE", show_default=True),
    code_width: Optional[int] = typer.Option(None, "--code-width", metavar="WIDTH"),
    tab_size: int = typer.Option(4, "--tab-size", metavar="TAB_SIZE", show_default=True),
    background_color: Optional[str] = typer.Option(None, "--background-color"),
    padding: Optional[str] = typer.Option("0", "-p", "--padding", metavar="PADDING"),
    from_code: bool = typer.Option(False, "--code", help="Treat source as code text."),
    colors: Optional[str] = typer.Option(None, "-c", "--colors", metavar="COLORS"),
    bgcolors: Optional[str] = typer.Option(None, "--bgcolors", metavar="BGCOLORS"),
    rainbow: bool = typer.Option(False, "-r", "--rainbow"),
    hues: int = typer.Option(5, "--hues", metavar="HUES", show_default=True),
    expand: bool = typer.Option(True, "--expand/--no-expand"),
    justify: Literal["left", "center", "right"] = typer.Option(
        "left", "-j", "--justify", case_sensitive=False
    ),
    vertical_justify: Literal["top", "middle", "bottom"] = typer.Option(
        "middle", "--vertical-justify", case_sensitive=False
    ),
    repeat_scale: float = typer.Option(2.0, "--repeat-scale", show_default=True),
    highlight_words: Optional[List[str]] = typer.Option(None, "--highlight-word"),
    highlight_regex: Optional[List[str]] = typer.Option(None, "--highlight-regex"),
    end: str = typer.Option("\n", "--end"),
    animate: bool = typer.Option(False, "-a", "--animate"),
    duration: Optional[float] = typer.Option(None, "-d", "--duration"),
    svg: Optional[str] = typer.Option(None, "--svg", metavar="SVG"),
) -> None:
    """Render Rich Syntax through a gradient wrapper."""
    try:
        padding_value = parse_padding(padding)
    except ValueError as error:
        raise typer.BadParameter(str(error)) from error

    if source == "-" or from_code:
        code = _read_text_argument(source, label="code")
        syntax = Syntax(
            code,
            lexer or "text",
            theme=theme,
            dedent=dedent,
            line_numbers=line_numbers,
            start_line=start_line,
            code_width=code_width,
            tab_size=tab_size,
            word_wrap=word_wrap,
            background_color=background_color,
            indent_guides=indent_guides,
            padding=cast(Any, padding_value or 0),
        )
    else:
        syntax = Syntax.from_path(
            source,
            lexer=lexer,
            theme=theme,
            dedent=dedent,
            line_numbers=line_numbers,
            start_line=start_line,
            code_width=code_width,
            tab_size=tab_size,
            word_wrap=word_wrap,
            background_color=background_color,
            indent_guides=indent_guides,
            padding=cast(Any, padding_value or 0),
        )
    _render_with_gradient(
        syntax,
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


def table_command(
    source: str = typer.Argument(..., metavar="CSV_OR_ROWS"),
    delimiter: str = typer.Option(",", "--delimiter", metavar="DELIMITER", help="CSV delimiter."),
    no_header: bool = typer.Option(False, "--no-header", help="Treat all rows as data."),
    title: Optional[str] = typer.Option(None, "--title", metavar="TITLE"),
    caption: Optional[str] = typer.Option(None, "--caption", metavar="CAPTION"),
    table_width: Optional[int] = typer.Option(None, "--table-width", metavar="WIDTH"),
    table_expand: bool = typer.Option(False, "--table-expand", help="Expand table width."),
    show_lines: bool = typer.Option(False, "--show-lines", help="Draw lines between rows."),
    safe_box: Optional[bool] = typer.Option(None, "--safe-box/--unsafe-box"),
    colors: Optional[str] = typer.Option(None, "-c", "--colors", metavar="COLORS"),
    bgcolors: Optional[str] = typer.Option(None, "--bgcolors", metavar="BGCOLORS"),
    rainbow: bool = typer.Option(False, "-r", "--rainbow"),
    hues: int = typer.Option(5, "--hues", metavar="HUES", show_default=True),
    expand: bool = typer.Option(True, "--expand/--no-expand"),
    justify: Literal["left", "center", "right"] = typer.Option(
        "left", "-j", "--justify", case_sensitive=False
    ),
    vertical_justify: Literal["top", "middle", "bottom"] = typer.Option(
        "middle", "--vertical-justify", case_sensitive=False
    ),
    repeat_scale: float = typer.Option(2.0, "--repeat-scale", show_default=True),
    highlight_words: Optional[List[str]] = typer.Option(None, "--highlight-word"),
    highlight_regex: Optional[List[str]] = typer.Option(None, "--highlight-regex"),
    end: str = typer.Option("\n", "--end"),
    animate: bool = typer.Option(False, "-a", "--animate"),
    duration: Optional[float] = typer.Option(None, "-d", "--duration"),
    svg: Optional[str] = typer.Option(None, "--svg", metavar="SVG"),
) -> None:
    """Render a CSV-backed Rich Table through a gradient wrapper."""
    csv_text = _read_text_argument(source, label="CSV") if source == "-" else source
    source_path = Path(csv_text)
    if source != "-" and source_path.exists():
        csv_text = source_path.read_text(encoding="utf-8")

    rows = list(csv.reader(csv_text.splitlines(), delimiter=delimiter))
    if not rows:
        raise click.UsageError("Missing CSV rows.")

    headers = rows[0] if not no_header else [f"Column {index}" for index in range(1, len(rows[0]) + 1)]
    data_rows = rows[1:] if not no_header else rows
    table = Table(
        *headers,
        title=title,
        caption=caption,
        width=table_width,
        expand=table_expand,
        show_lines=show_lines,
        safe_box=safe_box,
    )
    for row in data_rows:
        table.add_row(*row)

    _render_with_gradient(
        table,
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


__all__ = ["columns_command", "syntax_command", "table_command", "tree_command"]
