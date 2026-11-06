"""The ``gradient`` command: one command, modeled on Textualize/rich-cli."""

import sys
from pathlib import Path
from enum import Enum
from importlib.metadata import PackageNotFoundError, version
from typing import Annotated, Optional

import typer
from rich.console import Console, RenderableType

from .export import export_renderable
from .options import parse_mapping, parse_padding, parse_style
from .render import RenderConfig, Runnable, build_output, spectrum_output
from .resource import Mode, Resource, ResourceError, detect_mode, read_resource
from .telemetry import run_telemetry_action

try:
    VERSION = version("rich-gradient-cli")
except PackageNotFoundError:  # pragma: no cover - running from a bare checkout
    VERSION = "0.0.0"

EXIT_ERROR = 1

RENDERABLE = "Renderable"
GRADIENT = "Gradient"
ANIMATION = "Animation"
LAYOUT = "Layout"
CONTENT = "Content"
OUTPUT = "Output"


class VerticalAlign(str, Enum):
    """Vertical alignment."""

    TOP = "top"
    MIDDLE = "middle"
    BOTTOM = "bottom"


class SpectrumOutput(str, Enum):
    """Output format for ``--spectrum``."""

    TABLE = "table"
    NAMES = "names"
    HEX = "hex"
    CSV = "csv"


class TelemetryAction(str, Enum):
    """Actions accepted by ``--telemetry``."""

    ENABLE = "enable"
    DISABLE = "disable"
    STATUS = "status"


class Box(str, Enum):
    """Panel border styles (keys of :data:`rich_gradient_cli.options.BOXES`)."""

    NONE = "none"
    ASCII = "ascii"
    ASCII2 = "ascii2"
    SQUARE = "square"
    ROUNDED = "rounded"
    HEAVY = "heavy"
    DOUBLE = "double"

app = typer.Typer(
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=False,
    context_settings={"help_option_names": ["--help"]},
    help=(
        "Render text, files, URLs, or stdin with a [b]rich-gradient[/b] gradient.\n\n"
        "RESOURCE is a file path, an http(s) URL, [b]-[/b] for stdin, or literal text. "
        "The renderable is auto-detected from the file extension unless a mode "
        "flag such as [b]--markdown[/b] is given."
    ),
    epilog="https://maxludden.github.io/rich-gradient-cli",
)


def _version_callback(value: bool) -> None:
    """Print the version and exit when ``--version`` is passed."""
    if value:
        typer.echo(f"gradient {VERSION}")
        raise typer.Exit()


def _telemetry_callback(value: Optional[TelemetryAction]) -> None:
    """Handle ``--telemetry`` and exit, without rendering anything."""
    if value is not None:
        typer.echo(run_telemetry_action(value.value))
        raise typer.Exit()


#: Render mode of the current invocation, read by ``entrypoint`` for telemetry.
invoked_mode: str | None = None


def _fail(message: str) -> "typer.Exit":
    """Print ``message`` to stderr in red and return an error exit."""
    Console(stderr=True).print(f"[bold red]Error:[/] {message}", markup=True, highlight=False)
    return typer.Exit(EXIT_ERROR)


#: Modes that honor ``--head``/``--tail`` and ``--text-*`` respectively.
_HEAD_TAIL_MODES = {Mode.SYNTAX, Mode.CSV, Mode.IPYNB}
_TEXT_ALIGN_MODES = {Mode.TEXT, Mode.MARKDOWN}


def _warn_ignored(mode: Mode, *, head_tail: bool, text_align: bool, vertical: bool, panel: bool) -> None:
    """Warn on stderr about layout options that have no effect for ``mode``."""
    ignored: list[str] = []
    if head_tail and mode not in _HEAD_TAIL_MODES:
        ignored.append("--head/--tail")
    if text_align and mode not in _TEXT_ALIGN_MODES:
        ignored.append("--text-left/-center/-right/-full")
    if vertical and panel:
        ignored.append("--vertical-align (panels are top-aligned)")
    if ignored:
        Console(stderr=True).print(
            f"[yellow]Warning:[/] {', '.join(ignored)} ignored in {mode.value} mode.",
            highlight=False,
        )


@app.command()
def main(
    resource: Annotated[
        Optional[str],
        typer.Argument(
            metavar="[PATH,TEXT,URL, or '-']",
            show_default=False,
            help="File, URL, '-' for stdin, or literal text.",
        ),
    ] = None,
    # --- Renderable -----------------------------------------------------------
    print_: Annotated[bool, typer.Option("--print", "-p", help="Print console markup as gradient text.", rich_help_panel=RENDERABLE)] = False,
    rule: Annotated[bool, typer.Option("--rule", "-u", help="Display a horizontal rule titled RESOURCE.", rich_help_panel=RENDERABLE)] = False,
    json_: Annotated[bool, typer.Option("--json", "-J", help="Display as JSON.", rich_help_panel=RENDERABLE)] = False,
    markdown: Annotated[bool, typer.Option("--markdown", "-m", help="Display as Markdown.", rich_help_panel=RENDERABLE)] = False,
    rst: Annotated[bool, typer.Option("--rst", help="Display reStructuredText.", rich_help_panel=RENDERABLE)] = False,
    csv_: Annotated[bool, typer.Option("--csv", help="Display CSV/TSV as a table.", rich_help_panel=RENDERABLE)] = False,
    ipynb: Annotated[bool, typer.Option("--ipynb", help="Display a Jupyter notebook.", rich_help_panel=RENDERABLE)] = False,
    syntax: Annotated[bool, typer.Option("--syntax", help="Syntax highlighting.", rich_help_panel=RENDERABLE)] = False,
    inspect: Annotated[bool, typer.Option("--inspect", help="Inspect a Python object, e.g. 'str' or 'rich.console.Console'. Imports/evals RESOURCE: never pass untrusted text.", rich_help_panel=RENDERABLE)] = False,
    tree: Annotated[bool, typer.Option("--tree", help="Display a directory (or lines of text) as a tree.", rich_help_panel=RENDERABLE)] = False,
    columns: Annotated[bool, typer.Option("--columns", help="Lay out each line as a column cell.", rich_help_panel=RENDERABLE)] = False,
    spectrum: Annotated[bool, typer.Option("--spectrum", help="Show the rich-gradient color spectrum.", rich_help_panel=RENDERABLE)] = False,
    # --- Gradient -------------------------------------------------------------
    colors: Annotated[Optional[str], typer.Option("--colors", envvar="GRADIENT_COLORS", metavar="COLORS", help="Comma-separated gradient colors (names, hex, CSS names).", rich_help_panel=GRADIENT)] = None,
    bgcolors: Annotated[Optional[str], typer.Option("--bgcolors", metavar="COLORS", help="Comma-separated background colors.", rich_help_panel=GRADIENT)] = None,
    rainbow: Annotated[bool, typer.Option("--rainbow", help="Use the rainbow spectrum (ignores --colors).", rich_help_panel=GRADIENT)] = False,
    hues: Annotated[int, typer.Option("--hues", min=2, max=17, help="Number of spectrum hues for --rainbow / no colors.", rich_help_panel=GRADIENT)] = 5,
    repeat_scale: Annotated[Optional[float], typer.Option("--repeat-scale", min=0.01, help="How many times the gradient repeats across the output.", rich_help_panel=GRADIENT)] = None,
    highlight_word: Annotated[Optional[list[str]], typer.Option("--highlight-word", metavar="WORD=STYLE", help="Style a word (repeatable).", rich_help_panel=GRADIENT)] = None,
    highlight_regex: Annotated[Optional[list[str]], typer.Option("--highlight-regex", metavar="PATTERN=STYLE", help="Style regex matches (repeatable).", rich_help_panel=GRADIENT)] = None,
    animate: Annotated[bool, typer.Option("--animate", help="Animate the gradient (interactive terminals only).", rich_help_panel=GRADIENT)] = False,
    duration: Annotated[Optional[float], typer.Option("--duration", min=0.01, help="Stop animating after this many seconds.", rich_help_panel=GRADIENT)] = None,
    # --- Layout ---------------------------------------------------------------
    left: Annotated[bool, typer.Option("--left", "-l", help="Align block to the left.", rich_help_panel=LAYOUT)] = False,
    right: Annotated[bool, typer.Option("--right", "-r", help="Align block to the right.", rich_help_panel=LAYOUT)] = False,
    center: Annotated[bool, typer.Option("--center", "-c", help="Align block to the center.", rich_help_panel=LAYOUT)] = False,
    text_left: Annotated[bool, typer.Option("--text-left", "-L", help="Justify text to the left.", rich_help_panel=LAYOUT)] = False,
    text_right: Annotated[bool, typer.Option("--text-right", "-R", help="Justify text to the right.", rich_help_panel=LAYOUT)] = False,
    text_center: Annotated[bool, typer.Option("--text-center", "-C", help="Justify text to the center.", rich_help_panel=LAYOUT)] = False,
    text_full: Annotated[bool, typer.Option("--text-full", "-F", help="Justify text to both edges.", rich_help_panel=LAYOUT)] = False,
    vertical_align: Annotated[VerticalAlign, typer.Option("--vertical-align", help="Vertically align the block.", rich_help_panel=LAYOUT)] = VerticalAlign.MIDDLE,
    width: Annotated[Optional[int], typer.Option("--width", "-w", min=1, metavar="SIZE", help="Fit output to SIZE characters.", rich_help_panel=LAYOUT)] = None,
    max_width: Annotated[Optional[int], typer.Option("--max-width", "-W", min=1, metavar="SIZE", help="Set maximum width to SIZE characters.", rich_help_panel=LAYOUT)] = None,
    expand: Annotated[Optional[bool], typer.Option("--expand/--no-expand", "-e", help="Expand to full width (default: auto).", rich_help_panel=LAYOUT)] = None,
    padding: Annotated[Optional[str], typer.Option("--padding", "-d", metavar="TOP,RIGHT,BOTTOM,LEFT", help="Padding around output: 1, 2 or 4 comma-separated integers.", rich_help_panel=LAYOUT)] = None,
    panel: Annotated[Optional[Box], typer.Option("--panel", "-a", metavar="BOX", help="Wrap the output in a gradient panel: ascii, ascii2, square, rounded, heavy, double, none.", rich_help_panel=LAYOUT)] = None,
    panel_style: Annotated[str, typer.Option("--panel-style", "-S", metavar="STYLE", help="Panel border style.", rich_help_panel=LAYOUT)] = "",
    title: Annotated[Optional[str], typer.Option("--title", metavar="TEXT", help="Panel (or table) title.", rich_help_panel=LAYOUT)] = None,
    caption: Annotated[Optional[str], typer.Option("--caption", metavar="TEXT", help="Panel (or table) caption.", rich_help_panel=LAYOUT)] = None,
    # --- Content --------------------------------------------------------------
    style: Annotated[str, typer.Option("--style", "-s", metavar="STYLE", help="Rich style applied to the text.", rich_help_panel=CONTENT)] = "",
    markup: Annotated[bool, typer.Option("--markup/--no-markup", help="Parse Rich console markup in text.", rich_help_panel=CONTENT)] = True,
    emoji: Annotated[bool, typer.Option("--emoji", "-j", help="Enable emoji codes such as :sparkles:.", rich_help_panel=CONTENT)] = False,
    hyperlinks: Annotated[bool, typer.Option("--hyperlinks", "-y", help="Render hyperlinks in Markdown.", rich_help_panel=CONTENT)] = False,
    no_wrap: Annotated[bool, typer.Option("--no-wrap", help="Don't word wrap text or code.", rich_help_panel=CONTENT)] = False,
    tab_size: Annotated[int, typer.Option("--tab-size", min=1, help="Tab width.", rich_help_panel=CONTENT)] = 4,
    head: Annotated[Optional[int], typer.Option("--head", "-h", min=1, metavar="LINES", help="Display the first LINES (--syntax, --csv, --ipynb; ignored elsewhere).", rich_help_panel=CONTENT)] = None,
    tail: Annotated[Optional[int], typer.Option("--tail", "-t", min=1, metavar="LINES", help="Display the last LINES (--syntax, --csv, --ipynb; ignored elsewhere).", rich_help_panel=CONTENT)] = None,
    lexer: Annotated[Optional[str], typer.Option("--lexer", "-x", metavar="LEXER", help="Pygments lexer for --syntax.", rich_help_panel=CONTENT)] = None,
    theme: Annotated[str, typer.Option("--theme", envvar="RICH_THEME", metavar="THEME", help="Pygments theme for code.", rich_help_panel=CONTENT)] = "monokai",
    line_numbers: Annotated[bool, typer.Option("--line-numbers", "-n", help="Show line numbers.", rich_help_panel=CONTENT)] = False,
    guides: Annotated[bool, typer.Option("--guides", "-g", help="Show indentation guides.", rich_help_panel=CONTENT)] = False,
    rule_style: Annotated[str, typer.Option("--rule-style", metavar="STYLE", help="Style for --rule.", rich_help_panel=CONTENT)] = "",
    rule_char: Annotated[Optional[str], typer.Option("--rule-char", metavar="CHARACTER", help="Character(s) for --rule (overrides --thickness).", rich_help_panel=CONTENT)] = None,
    thickness: Annotated[int, typer.Option("--thickness", min=0, max=3, help="Rule thickness, 0-3.", rich_help_panel=CONTENT)] = 2,
    delimiter: Annotated[Optional[str], typer.Option("--delimiter", metavar="CHAR", help="CSV delimiter (default: auto-detect).", rich_help_panel=CONTENT)] = None,
    no_header: Annotated[bool, typer.Option("--no-header", help="Treat the first CSV row as data.", rich_help_panel=CONTENT)] = False,
    max_depth: Annotated[int, typer.Option("--max-depth", min=1, help="Directory depth for --tree.", rich_help_panel=CONTENT)] = 2,
    spectrum_output_: Annotated[SpectrumOutput, typer.Option("--spectrum-output", help="Format for --spectrum.", rich_help_panel=CONTENT)] = SpectrumOutput.TABLE,
    # --- Output ---------------------------------------------------------------
    export_html: Annotated[Optional[str], typer.Option("--export-html", "-o", metavar="PATH", help="Write HTML to PATH.", rich_help_panel=OUTPUT)] = None,
    export_svg: Annotated[Optional[str], typer.Option("--export-svg", metavar="PATH", help="Write SVG to PATH.", rich_help_panel=OUTPUT)] = None,
    pager: Annotated[bool, typer.Option("--pager", help="Display in an interactive pager.", rich_help_panel=OUTPUT)] = False,
    force_terminal: Annotated[bool, typer.Option("--force-terminal", help="Keep ANSI codes when not writing to a terminal.", rich_help_panel=OUTPUT)] = False,
    telemetry: Annotated[Optional[TelemetryAction], typer.Option("--telemetry", callback=_telemetry_callback, is_eager=True, metavar="[enable|disable|status]", help="Manage opt-in anonymous usage telemetry, then exit.", rich_help_panel=OUTPUT)] = None,
    version_: Annotated[bool, typer.Option("--version", "-v", callback=_version_callback, is_eager=True, help="Print version and exit.", rich_help_panel=OUTPUT)] = False,
) -> None:
    """Render text, files, URLs, or stdin with a [b]rich-gradient[/b] gradient.

    RESOURCE is a file path, an http(s) URL, [b]-[/b] for stdin, or literal text.
    The renderable is auto-detected from the file extension unless a flag such as
    [b]--markdown[/b] is given.
    """
    global invoked_mode
    aligns = [name for flag, name in ((left, "left"), (center, "center"), (right, "right")) if flag]
    if len(aligns) > 1:
        raise typer.BadParameter("Choose only one of --left, --center, --right.")
    justs = [
        name
        for flag, name in (
            (text_left, "left"), (text_center, "center"), (text_right, "right"), (text_full, "full"),
        )
        if flag
    ]
    if len(justs) > 1:
        raise typer.BadParameter("Choose only one text justification option.")
    align_value = aligns[0] if aligns else "left"
    text_align_value = justs[0] if justs else "default"
    panel_on = panel is not None and panel is not Box.NONE
    # Exactly zero or one renderable flag may be given.
    selected = {
        Mode.TEXT: print_, Mode.MARKDOWN: markdown, Mode.SYNTAX: syntax, Mode.JSON: json_,
        Mode.CSV: csv_, Mode.RULE: rule, Mode.TREE: tree, Mode.COLUMNS: columns,
        Mode.SPECTRUM: spectrum, Mode.RST: rst, Mode.IPYNB: ipynb, Mode.INSPECT: inspect,
    }
    chosen = [mode for mode, flag in selected.items() if flag]
    if len(chosen) > 1:
        flags = ", ".join(f"--{mode.value}" for mode in chosen)
        raise typer.BadParameter(f"Choose only one renderable flag, got: {flags}.")
    if animate and (export_svg or export_html):
        raise typer.BadParameter("--animate cannot be combined with --export-svg/--export-html.")
    if animate and pager:
        raise typer.BadParameter("--animate cannot be combined with --pager.")
    if head is not None and tail is not None:
        raise typer.BadParameter("--head and --tail cannot be combined.")
    try:
        parse_padding(padding)
        parse_style(style)
        parse_style(panel_style)
        parse_mapping(highlight_word)
        parse_mapping(highlight_regex)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    for dest in (export_svg, export_html):
        if dest and not Path(dest).expanduser().resolve().parent.is_dir():
            raise typer.BadParameter(f"Cannot write {dest}: directory does not exist.")

    cfg = RenderConfig(
        colors=colors, bgcolors=bgcolors, rainbow=rainbow, hues=hues, repeat_scale=repeat_scale,
        highlight_words=list(highlight_word or []), highlight_regex=list(highlight_regex or []),
        animate=animate, duration=duration,
        align=align_value, text_align=text_align_value, vertical_align=vertical_align.value,
        expand=expand, padding=padding, panel=panel_on,
        box=panel.value if panel_on and panel is not None else "rounded", panel_style=panel_style,
        rule_style=rule_style,
        title=title, caption=caption, style=style, markup=markup, emoji=emoji,
        hyperlinks=hyperlinks, no_wrap=no_wrap, tab_size=tab_size, head=head, tail=tail,
        lexer=lexer, theme=theme, line_numbers=line_numbers, guides=guides, rule_char=rule_char,
        thickness=thickness, delimiter=delimiter, no_header=no_header, max_depth=max_depth,
        spectrum_output=spectrum_output_.value,
    )

    console = Console(force_terminal=True if force_terminal else None)
    if width is not None:
        console.width = width
    if max_width is not None:
        console.width = min(console.width, max_width)

    try:
        renderable: RenderableType | None = None
        runner: Runnable | None = None
        if chosen == [Mode.SPECTRUM]:
            invoked_mode = Mode.SPECTRUM.value
            renderable = spectrum_output(cfg)
        else:
            if resource is None and sys.stdin.isatty():
                raise typer.BadParameter("Missing RESOURCE (text, path, URL, or '-').")
            if chosen == [Mode.INSPECT]:
                if resource is None:
                    raise typer.BadParameter("--inspect needs a Python expression.")
                data = Resource(text=resource, is_literal=True)
            else:
                data = read_resource(resource, allow_directory=chosen == [Mode.TREE])
            mode = chosen[0] if chosen else detect_mode(data)
            invoked_mode = mode.value
            _warn_ignored(
                mode,
                head_tail=head is not None or tail is not None,
                text_align=text_align_value != "default",
                vertical=vertical_align is not VerticalAlign.MIDDLE,
                panel=panel_on,
            )
            animated = animate and console.is_terminal
            built = build_output(mode, data, cfg, console, animated=animated)
            if isinstance(built, Runnable):
                runner = built
            else:
                renderable = built

        if runner is not None:
            runner.run()
            return
        assert renderable is not None
        if pager:
            with console.pager(styles=True):
                console.print(renderable)
        else:
            console.print(renderable)
        if export_svg or export_html:
            export_renderable(renderable, svg=export_svg, html=export_html, width=console.width)
    except ResourceError as exc:
        raise _fail(str(exc)) from exc
    except ValueError as exc:
        raise _fail(str(exc)) from exc
    except OSError as exc:
        where = f"{exc.filename}: " if exc.filename else ""
        raise _fail(f"{where}{exc.strerror or exc}") from exc


__all__ = ["VERSION", "app", "invoked_mode", "main"]
