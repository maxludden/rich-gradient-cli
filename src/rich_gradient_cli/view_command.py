"""Rich-CLI-style file viewing command."""

from __future__ import annotations

import csv
import importlib
import io
import json
import sys
from enum import Enum
from operator import itemgetter
from pathlib import Path
from typing import Any, Literal, Optional, Tuple, cast
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import click
import typer
from rich import box
from rich.align import Align
from rich._inspect import Inspect
from rich.console import (
    Console,
    ConsoleOptions,
    Group,
    RenderResult,
    RenderableType,
)
from rich.json import JSON
from rich.markdown import Markdown
from rich.padding import Padding
from rich.panel import Panel
from rich.rule import Rule
from rich.style import Style
from rich.styled import Styled
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text


class ResourceFormat(Enum):
    """Supported rich-cli-style render modes."""

    AUTO = "auto"
    SYNTAX = "syntax"
    PRINT = "print"
    MARKDOWN = "markdown"
    JSON = "json"
    CSV = "csv"
    RULE = "rule"
    RST = "rst"
    IPYNB = "ipynb"
    INSPECT = "inspect"


COMMON_LEXERS = {
    ".html": "html",
    ".htm": "html",
    ".py": "python",
    ".md": "markdown",
    ".js": "javascript",
    ".xml": "xml",
    ".json": "json",
    ".toml": "toml",
    ".yaml": "yaml",
    ".yml": "yaml",
}

CSV_EXTENSIONS = {".csv", ".tsv"}
MARKDOWN_EXTENSIONS = {".md", ".markdown"}
RST_EXTENSIONS = {".rst"}


class ForceWidth:
    """Force a renderable to a given terminal width."""

    def __init__(self, renderable: RenderableType, width: int) -> None:
        self.renderable = renderable
        self.width = width

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        yield from console.render(self.renderable, options.update_width(self.width))


def _read_resource(resource: str) -> str:
    """Read content from stdin, a local file, or a URL."""
    if not resource:
        raise click.UsageError("Missing path, URL, or '-'.")
    if resource == "-":
        return sys.stdin.read()
    if resource.startswith(("http://", "https://")):
        try:
            request = Request(resource, headers={"User-Agent": "rich-gradient-cli"})
            with urlopen(request, timeout=10) as response:
                return response.read().decode("utf-8", errors="replace")
        except (OSError, URLError) as error:
            raise typer.BadParameter(f"Unable to read URL: {error}") from error
    try:
        return Path(resource).read_text(encoding="utf-8", errors="replace")
    except OSError as error:
        raise typer.BadParameter(f"Unable to read file: {error}") from error


def _resource_suffix(resource: str) -> str:
    """Return the lower-case suffix for local and URL resources."""
    if resource.startswith(("http://", "https://")):
        return Path(urlparse(resource).path).suffix.lower()
    return Path(resource).suffix.lower()


def _detect_format(resource: str, explicit: ResourceFormat) -> ResourceFormat:
    """Detect a render mode from a resource name unless one was requested."""
    if explicit is not ResourceFormat.AUTO:
        return explicit
    suffix = _resource_suffix(resource)
    if suffix in MARKDOWN_EXTENSIONS:
        return ResourceFormat.MARKDOWN
    if suffix == ".json":
        return ResourceFormat.JSON
    if suffix in CSV_EXTENSIONS:
        return ResourceFormat.CSV
    if suffix in RST_EXTENSIONS:
        return ResourceFormat.RST
    if suffix == ".ipynb":
        return ResourceFormat.IPYNB
    return ResourceFormat.SYNTAX


def _detect_lexer(resource: str, lexer: Optional[str]) -> str:
    """Detect a Pygments lexer from a resource suffix."""
    if lexer:
        return lexer
    return COMMON_LEXERS.get(_resource_suffix(resource), "text")


def _parse_padding(padding: Optional[str]) -> Optional[Tuple[int, ...]]:
    """Parse Rich padding shorthand."""
    if not padding:
        return None
    try:
        values = tuple(int(value.strip()) for value in padding.split(","))
    except ValueError as error:
        raise typer.BadParameter(
            "Padding must be 1, 2, or 4 comma-separated integers."
        ) from error
    if len(values) not in {1, 2, 4}:
        raise typer.BadParameter("Padding must be 1, 2, or 4 comma-separated integers.")
    return values


def _line_range(
    head: Optional[int], tail: Optional[int], total_lines: int
) -> Optional[Tuple[int, int]]:
    """Return a Rich Syntax line range from head/tail options."""
    if head and tail:
        raise typer.BadParameter("Use --head or --tail, not both.")
    if head:
        return (1, head)
    if tail:
        return (max(total_lines - tail + 1, 1), total_lines)
    return None


def _box_for_name(name: str) -> box.Box:
    """Map rich-cli-style panel names to Rich box constants."""
    box_map = {
        "ascii": box.ASCII,
        "ascii2": box.ASCII2,
        "square": box.SQUARE,
        "rounded": box.ROUNDED,
        "heavy": box.HEAVY,
        "double": box.DOUBLE,
    }
    return box_map.get(name.lower(), box.ROUNDED)


def _render_csv(
    resource: str,
    data: str,
    *,
    head: Optional[int],
    tail: Optional[int],
    title: Optional[str],
    caption: Optional[str],
) -> Table:
    """Render CSV or TSV data as a Rich table."""
    sniffer = csv.Sniffer()
    dialect: Any
    try:
        dialect = sniffer.sniff(data[:1024], delimiters=",\t|;")
        has_header = sniffer.has_header(data[:1024])
    except csv.Error:
        if _resource_suffix(resource) == ".tsv":
            dialect = csv.get_dialect("excel-tab")
        else:
            dialect = csv.get_dialect("excel")
        has_header = True

    rows_iter = csv.reader(io.StringIO(data), dialect=dialect)
    rows = [row for row in rows_iter if row]
    header: Optional[list[str]] = None
    if has_header and rows:
        header = rows.pop(0)

    if head is not None:
        rows = rows[:head]
    elif tail is not None:
        rows = rows[-tail:]

    table = Table(
        show_header=header is not None,
        box=box.HEAVY_HEAD if header else box.SQUARE,
        border_style="blue",
        title=title,
        caption=caption,
        caption_justify="right",
    )
    columns = header or [f"Column {index + 1}" for index in range(max(map(len, rows), default=0))]
    for column in columns:
        table.add_column(column)
    for row in rows:
        table.add_row(*row)

    for index, table_column in enumerate(table.columns):
        for row in rows:
            try:
                value = itemgetter(index)(row)
            except IndexError:
                break
            if value and not _is_number(value):
                break
        else:
            table_column.justify = "right"
            table_column.style = "bold green"
            table_column.header_style = "bold green"
    return table


def _is_number(value: str) -> bool:
    """Return whether a CSV field looks numeric."""
    try:
        float(value)
    except ValueError:
        return False
    return True


def _resolve_object(expression: str) -> Any:
    """Resolve a dotted ``module.attr`` path, falling back to ``eval``.

    Mirrors ``rich --inspect``: the argument is a Python expression such as
    ``str`` or ``rich.console.Console``. Dotted paths are imported without
    ``eval``; anything else is evaluated with ``rich`` and the standard
    library importable by name.
    """
    expression = expression.strip()
    parts = expression.split(".")
    if all(part.isidentifier() for part in parts):
        for split in range(len(parts), 0, -1):
            try:
                obj: Any = importlib.import_module(".".join(parts[:split]))
            except ImportError:
                continue
            try:
                for attr in parts[split:]:
                    obj = getattr(obj, attr)
            except AttributeError:
                break
            return obj
        import builtins

        if hasattr(builtins, parts[0]):
            obj = getattr(builtins, parts[0])
            for attr in parts[1:]:
                obj = getattr(obj, attr)
            return obj
    try:
        return eval(expression, {})  # noqa: S307 - user-supplied CLI expression
    except Exception as error:
        raise typer.BadParameter(f"Unable to evaluate {expression!r}: {error}") from error


def _render_ipynb(
    data: str,
    *,
    lexer: Optional[str],
    theme: str,
    hyperlinks: bool,
    head: Optional[int],
    tail: Optional[int],
    line_numbers: bool,
    guides: bool,
    no_wrap: bool,
) -> RenderableType:
    """Render a Jupyter notebook's cells and outputs."""
    try:
        notebook = json.loads(data)
        cells_data = notebook["cells"]
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise typer.BadParameter(f"Unable to parse notebook: {error}") from error
    language = lexer or notebook.get("metadata", {}).get("kernelspec", {}).get(
        "language", "text"
    )

    cells: list[RenderableType] = []
    blank_before = True
    for cell in cells_data:
        if blank_before:
            cells.append("")
        if "execution_count" in cell:
            count = cell["execution_count"] or " "
            cells.append(f"[green]In [[#66ff00]{count}[/#66ff00]]:[/green]")
        source = "".join(cell.get("source", ""))
        renderable: RenderableType
        if cell.get("cell_type") == "code":
            renderable = Panel(
                Syntax(
                    source,
                    language,
                    theme=theme,
                    line_numbers=line_numbers,
                    indent_guides=guides,
                    word_wrap=not no_wrap,
                    line_range=_line_range(head, tail, len(source.splitlines())),
                ),
                border_style="dim",
            )
        elif cell.get("cell_type") == "markdown":
            renderable = Markdown(source, code_theme=theme, hyperlinks=hyperlinks)
        else:
            renderable = Text(source)
        blank_before = True
        cells.append(renderable)
        for output in cell.get("outputs", []):
            kind = output.get("output_type")
            if kind == "stream":
                renderable = Text.from_ansi("".join(output["text"]))
                blank_before = False
            elif kind == "error":
                renderable = Text.from_ansi("\n".join(output["traceback"]).rstrip())
                blank_before = True
            elif kind == "execute_result":
                count = output.get("execution_count") or " "
                plain = output.get("data", {}).get("text/plain", "")
                if isinstance(plain, list):
                    plain = "".join(plain)
                renderable = Text.from_markup(
                    f"[red]Out[[#ee4b2b]{count}[/#ee4b2b]]:[/red]\n"
                ) + Text.from_ansi(plain)
                blank_before = True
            else:
                continue
            cells.append(renderable)
    return Group(*cells)


def _render_resource(
    resource: str,
    *,
    mode: ResourceFormat,
    lexer: Optional[str],
    theme: str,
    line_numbers: bool,
    guides: bool,
    no_wrap: bool,
    hyperlinks: bool,
    head: Optional[int],
    tail: Optional[int],
    emoji: bool,
    text_justify: Literal["default", "left", "center", "right", "full"],
    rule_style: str,
    rule_char: str,
    title: Optional[str],
    caption: Optional[str],
) -> RenderableType:
    """Build the base renderable for a resource and mode."""
    if mode is ResourceFormat.PRINT:
        data = _read_resource(resource) if resource == "-" else resource
        text = Text.from_markup(data, justify=text_justify, emoji=emoji)
        text.no_wrap = no_wrap
        return text
    if mode is ResourceFormat.RULE:
        data = _read_resource(resource) if resource == "-" else resource
        return Rule(
            data,
            style=Style.parse(rule_style),
            characters=rule_char,
            align=cast(
                Literal["left", "center", "right"],
                "center" if text_justify in {"default", "full"} else text_justify,
            ),
        )
    if mode is ResourceFormat.INSPECT:
        return Inspect(
            _resolve_object(resource),
            help=False,
            dunder=False,
            all=False,
            methods=True,
        )
    data = _read_resource(resource)
    if mode is ResourceFormat.RST:
        from rich_rst import RestructuredText

        return RestructuredText(
            data,
            code_theme=theme,
            default_lexer=lexer or "python",
            show_errors=False,
        )
    if mode is ResourceFormat.IPYNB:
        return _render_ipynb(
            data,
            lexer=lexer,
            theme=theme,
            hyperlinks=hyperlinks,
            head=head,
            tail=tail,
            line_numbers=line_numbers,
            guides=guides,
            no_wrap=no_wrap,
        )
    if mode is ResourceFormat.MARKDOWN:
        return Markdown(data, code_theme=theme, hyperlinks=hyperlinks)
    if mode is ResourceFormat.JSON:
        try:
            json.loads(data)
        except json.JSONDecodeError as error:
            raise typer.BadParameter(f"Unable to parse JSON: {error}") from error
        return JSON(data)
    if mode is ResourceFormat.CSV:
        return _render_csv(
            resource,
            data,
            head=head,
            tail=tail,
            title=title,
            caption=caption,
        )

    resolved_lexer = _detect_lexer(resource, lexer)
    lines = data.splitlines()
    return Syntax(
        data,
        resolved_lexer,
        theme=theme,
        line_numbers=line_numbers,
        indent_guides=guides,
        word_wrap=not no_wrap,
        line_range=_line_range(head, tail, len(lines)),
    )


def _apply_wrappers(
    renderable: RenderableType,
    *,
    style: Optional[str],
    padding: Optional[str],
    panel: Optional[str],
    panel_style: Optional[str],
    title: Optional[str],
    caption: Optional[str],
    expand: bool,
    align: Literal["default", "left", "center", "right"],
    width: Optional[int],
) -> RenderableType:
    """Apply common rich-cli-style wrappers around a renderable."""
    padding_values = _parse_padding(padding)
    if padding_values is not None:
        renderable = Padding(renderable, cast(Any, padding_values), expand=expand)
    if panel and panel.lower() != "none":
        renderable = Panel(
            renderable,
            box=_box_for_name(panel),
            expand=expand,
            title=title,
            subtitle=caption,
            border_style=parse_optional_style(panel_style),
        )
    if style:
        renderable = Styled(renderable, Style.parse(style))
    if width:
        renderable = ForceWidth(renderable, width)
    if align != "default":
        renderable = Align(renderable, align=align)
    return renderable


def parse_optional_style(style: Optional[str]) -> Style:
    """Parse an optional style string for wrappers."""
    return Style.parse(style) if style else Style.null()


def _selected_mode(
    *,
    print_: bool,
    syntax: bool,
    markdown: bool,
    json_: bool,
    csv_: bool,
    rule: bool,
    rst: bool = False,
    ipynb: bool = False,
    inspect: bool = False,
) -> ResourceFormat:
    """Resolve mutually exclusive render mode flags."""
    selected = [
        mode
        for flag, mode in (
            (print_, ResourceFormat.PRINT),
            (syntax, ResourceFormat.SYNTAX),
            (markdown, ResourceFormat.MARKDOWN),
            (json_, ResourceFormat.JSON),
            (csv_, ResourceFormat.CSV),
            (rule, ResourceFormat.RULE),
            (rst, ResourceFormat.RST),
            (ipynb, ResourceFormat.IPYNB),
            (inspect, ResourceFormat.INSPECT),
        )
        if flag
    ]
    if len(selected) > 1:
        raise typer.BadParameter("Choose only one render mode.")
    return selected[0] if selected else ResourceFormat.AUTO


def _selected_align(
    left: bool, center: bool, right: bool
) -> Literal["default", "left", "center", "right"]:
    """Resolve mutually exclusive block alignment flags."""
    selected = [name for flag, name in ((left, "left"), (center, "center"), (right, "right")) if flag]
    if len(selected) > 1:
        raise typer.BadParameter("Choose only one alignment option.")
    return cast(Literal["default", "left", "center", "right"], selected[0] if selected else "default")


def _selected_text_justify(
    text_left: bool, text_center: bool, text_right: bool, text_full: bool
) -> Literal["default", "left", "center", "right", "full"]:
    """Resolve mutually exclusive text justification flags."""
    selected = [
        name
        for flag, name in (
            (text_left, "left"),
            (text_center, "center"),
            (text_right, "right"),
            (text_full, "full"),
        )
        if flag
    ]
    if len(selected) > 1:
        raise typer.BadParameter("Choose only one text justification option.")
    return cast(
        Literal["default", "left", "center", "right", "full"],
        selected[0] if selected else "default",
    )


def view_command(
    resource: str = typer.Argument(..., metavar="PATH_OR_URL"),
    print_: bool = typer.Option(
        False,
        "--print",
        "-p",
        help="Treat the input as Rich console markup.",
    ),
    syntax: bool = typer.Option(False, "--syntax", help="Render as syntax-highlighted text."),
    markdown: bool = typer.Option(False, "--markdown", "-m", help="Render as Markdown."),
    json_: bool = typer.Option(False, "--json", "-J", help="Render as JSON."),
    csv_: bool = typer.Option(False, "--csv", help="Render CSV or TSV as a table."),
    rule: bool = typer.Option(False, "--rule", "-u", help="Render a horizontal rule."),
    rst: bool = typer.Option(False, "--rst", help="Render reStructuredText."),
    ipynb: bool = typer.Option(False, "--ipynb", help="Render a Jupyter notebook."),
    inspect: bool = typer.Option(
        False, "--inspect", help="Inspect a Python object (e.g. 'str')."
    ),
    head: Optional[int] = typer.Option(
        None,
        "--head",
        "-h",
        min=1,
        metavar="LINES",
        help="Display first LINES for syntax or CSV output.",
    ),
    tail: Optional[int] = typer.Option(
        None,
        "--tail",
        "-t",
        min=1,
        metavar="LINES",
        help="Display last LINES for syntax or CSV output.",
    ),
    theme: str = typer.Option(
        "ansi_dark",
        "--theme",
        envvar="RICH_THEME",
        metavar="THEME",
        help="Pygments syntax theme.",
    ),
    lexer: Optional[str] = typer.Option(
        None,
        "--lexer",
        "-x",
        metavar="LEXER",
        help="Pygments lexer override.",
    ),
    line_numbers: bool = typer.Option(
        False,
        "--line-numbers",
        "-n",
        help="Show line numbers in syntax output.",
    ),
    guides: bool = typer.Option(
        False,
        "--guides",
        "-g",
        help="Show indentation guides in syntax output.",
    ),
    no_wrap: bool = typer.Option(False, "--no-wrap", help="Disable syntax word wrap."),
    hyperlinks: bool = typer.Option(
        False,
        "--hyperlinks",
        "-y",
        help="Render Markdown links as terminal hyperlinks.",
    ),
    emoji: bool = typer.Option(False, "--emoji", "-j", help="Enable emoji markup."),
    left: bool = typer.Option(False, "--left", "-l", help="Align block left."),
    center: bool = typer.Option(False, "--center", "-c", help="Align block center."),
    right: bool = typer.Option(False, "--right", "-r", help="Align block right."),
    text_left: bool = typer.Option(False, "--text-left", "-L", help="Justify text left."),
    text_center: bool = typer.Option(False, "--text-center", "-C", help="Justify text center."),
    text_right: bool = typer.Option(False, "--text-right", "-R", help="Justify text right."),
    text_full: bool = typer.Option(False, "--text-full", "-F", help="Fully justify text."),
    width: Optional[int] = typer.Option(
        None,
        "--width",
        "-w",
        min=1,
        metavar="SIZE",
        help="Render output at SIZE columns.",
    ),
    max_width: Optional[int] = typer.Option(
        None,
        "--max-width",
        "-W",
        min=1,
        metavar="SIZE",
        help="Constrain console print width to SIZE columns.",
    ),
    style: Optional[str] = typer.Option(None, "--style", "-s", metavar="STYLE"),
    padding: Optional[str] = typer.Option(
        None,
        "--padding",
        "-d",
        metavar="TOP,RIGHT,BOTTOM,LEFT",
        help="Padding around output: 1, 2, or 4 comma-separated integers.",
    ),
    panel: Optional[str] = typer.Option(
        None,
        "--panel",
        "-a",
        metavar="BOX",
        help="Draw a panel around output: ascii, ascii2, square, rounded, heavy, double.",
    ),
    panel_style: Optional[str] = typer.Option(None, "--panel-style", "-S", metavar="STYLE"),
    title: Optional[str] = typer.Option(None, "--title", metavar="TEXT"),
    caption: Optional[str] = typer.Option(None, "--caption", metavar="TEXT"),
    expand: bool = typer.Option(False, "--expand", "-e", help="Expand panel or padding."),
    rule_style: str = typer.Option("bright_green", "--rule-style", metavar="STYLE"),
    rule_char: str = typer.Option("─", "--rule-char", metavar="CHARACTER"),
    force_terminal: bool = typer.Option(
        False,
        "--force-terminal",
        help="Keep terminal colors when output is captured or piped.",
    ),
    export_html: Optional[str] = typer.Option(
        None,
        "--export-html",
        "-o",
        metavar="PATH",
        help="Write rendered output as HTML.",
    ),
    export_svg: Optional[str] = typer.Option(
        None,
        "--export-svg",
        metavar="PATH",
        help="Write rendered output as SVG.",
    ),
    pager: bool = typer.Option(False, "--pager", help="Display output in a pager."),
) -> None:
    """View files, URLs, stdin, or markup with Rich-style rendering."""
    mode = _detect_format(
        resource,
        _selected_mode(
            print_=print_,
            syntax=syntax,
            markdown=markdown,
            json_=json_,
            csv_=csv_,
            rule=rule,
            rst=rst,
            ipynb=ipynb,
            inspect=inspect,
        ),
    )
    renderable = _render_resource(
        resource,
        mode=mode,
        lexer=lexer,
        theme=theme,
        line_numbers=line_numbers,
        guides=guides,
        no_wrap=no_wrap,
        hyperlinks=hyperlinks,
        head=head,
        tail=tail,
        emoji=emoji,
        text_justify=_selected_text_justify(text_left, text_center, text_right, text_full),
        rule_style=rule_style,
        rule_char=rule_char,
        title=title,
        caption=caption,
    )
    renderable = _apply_wrappers(
        renderable,
        style=style,
        padding=padding,
        panel=panel,
        panel_style=panel_style,
        title=title,
        caption=caption,
        expand=expand or width is not None,
        align=_selected_align(left, center, right),
        width=width,
    )

    console = Console(
        emoji=emoji,
        record=bool(export_html or export_svg),
        force_terminal=True if force_terminal else None,
        width=width,
    )
    if pager:
        with console.pager(styles=force_terminal):
            console.print(renderable, width=max_width)
    else:
        console.print(renderable, width=max_width)

    if export_html:
        console.save_html(export_html, clear=False)
    if export_svg:
        console.save_svg(export_svg, clear=False)


__all__ = ["view_command"]
