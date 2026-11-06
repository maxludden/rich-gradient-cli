"""Build the rich-gradient renderable for a resource."""

from __future__ import annotations

import csv
import importlib
import io
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, cast, runtime_checkable

from rich.columns import Columns as RichColumns
from rich.align import Align
from rich._inspect import Inspect
from rich.console import Console, Group, RenderableType
from rich.constrain import Constrain
from rich.measure import Measurement
from rich.markdown import Markdown as RichMarkdown
from rich.markup import MarkupError, escape
from rich.padding import Padding
from rich.panel import Panel as RichPanel
from rich.table import Table as RichTable
from rich.text import Text as RichText
from rich.tree import Tree as RichTree
from rich_gradient import Gradient, Panel, Pretty, Rule, Spectrum
from rich_gradient.animated_gradient import AnimatedGradient
from rich_gradient.animated_panel import AnimatedPanel
from rich_gradient.animated_rule import AnimatedRule
from rich.syntax import Syntax as RichSyntax

from .options import BOXES, parse_colors, parse_mapping, parse_padding
from .resource import Mode, Resource, ResourceError


@runtime_checkable
class Runnable(Protocol):
    """An animated rich-gradient object that can be run to completion."""

    def run(self) -> None:
        """Run the animation until it finishes or is interrupted."""


@dataclass
class RenderConfig:
    """Every option that influences rendering, independent of the CLI layer."""

    # Gradient
    colors: str | None = None
    bgcolors: str | None = None
    rainbow: bool = False
    hues: int = 5
    repeat_scale: float | None = None
    highlight_words: list[str] = field(default_factory=list)
    highlight_regex: list[str] = field(default_factory=list)
    # Animation
    animate: bool = False
    duration: float | None = None
    # Layout
    align: str = "left"
    text_align: str = "default"
    vertical_align: str = "middle"
    expand: bool | None = None
    padding: str | None = None
    panel: bool = False
    box: str = "rounded"
    panel_style: str = ""
    title: str | None = None
    caption: str | None = None
    # Content
    style: str = ""
    markup: bool = True
    emoji: bool = False
    hyperlinks: bool = False
    no_wrap: bool = False
    tab_size: int = 4
    head: int | None = None
    tail: int | None = None
    lexer: str | None = None
    theme: str = "monokai"
    line_numbers: bool = False
    guides: bool = False
    rule_char: str | None = None
    thickness: int = 2
    delimiter: str | None = None
    no_header: bool = False
    max_depth: int = 2
    rule_style: str = ""
    spectrum_output: str = "table"


def slice_lines(text: str, head: int | None, tail: int | None) -> str:
    """Keep only the first ``head`` or last ``tail`` lines of ``text``."""
    if head is None and tail is None:
        return text
    lines = text.splitlines()
    if head is not None:
        lines = lines[:head]
    elif tail is not None:
        lines = lines[-tail:]
    return "\n".join(lines)


def _text(resource: Resource, cfg: RenderConfig) -> RichText:
    """Build a plain Rich ``Text`` honoring markup, emoji, and wrapping flags."""
    try:
        if cfg.markup:
            text = RichText.from_markup(
                resource.text.rstrip("\n"), emoji=cfg.emoji, style=cfg.style
            )
        else:
            text = RichText(resource.text.rstrip("\n"), style=cfg.style)
    except MarkupError as exc:
        raise ResourceError(f"Invalid markup: {exc} (use --no-markup to print verbatim).") from exc
    text.justify = cast(Any, cfg.text_align)
    text.no_wrap = cfg.no_wrap
    text.tab_size = cfg.tab_size
    return text


def _syntax(resource: Resource, cfg: RenderConfig) -> RichSyntax:
    """Build a ``Syntax`` block, guessing the lexer from the file name."""
    code = slice_lines(resource.text, cfg.head, cfg.tail)
    lexer = cfg.lexer or RichSyntax.guess_lexer(resource.name or "", code)
    return RichSyntax(
        code,
        lexer,
        theme=cfg.theme,
        line_numbers=cfg.line_numbers,
        indent_guides=cfg.guides,
        word_wrap=not cfg.no_wrap,
        tab_size=cfg.tab_size,
    )


def _csv(resource: Resource, cfg: RenderConfig) -> RichTable:
    """Build a table from CSV/TSV text, escaping cells so they are not parsed as markup."""
    sample = resource.text[:1024]
    delimiter = cfg.delimiter
    if delimiter is None:
        if resource.suffix == ".tsv":
            delimiter = "\t"
        else:
            try:
                delimiter = csv.Sniffer().sniff(sample, delimiters=",\t|;").delimiter
            except csv.Error:
                delimiter = ","
    rows = list(csv.reader(io.StringIO(resource.text), delimiter=delimiter))
    rows = [row for row in rows if row]
    if not rows:
        raise ResourceError("The CSV input is empty.")
    table = RichTable(title=cfg.title, caption=cfg.caption, show_header=not cfg.no_header)
    width = max(len(row) for row in rows)
    if cfg.no_header:
        header, body = [""] * width, rows
    else:
        header, body = rows[0], rows[1:]
    body = body[: cfg.head] if cfg.head is not None else body
    body = body[-cfg.tail :] if cfg.tail is not None and cfg.head is None else body
    for index in range(width):
        label = header[index] if index < len(header) else ""
        table.add_column(escape(label))
    for row in body:
        table.add_row(*(escape(cell) for cell in row + [""] * (width - len(row))))
    return table


def _json(resource: Resource, cfg: RenderConfig) -> Pretty:
    """Build a pretty-printed view of parsed JSON."""
    try:
        data = json.loads(resource.text)
    except json.JSONDecodeError as exc:
        raise ResourceError(f"Invalid JSON: {exc}") from exc
    return Pretty(data, indent_guides=cfg.guides, expand_all=True, no_wrap=cfg.no_wrap)


def _tree(resource: Resource, cfg: RenderConfig) -> RichTree:
    """Build a tree from a directory, or from lines (first line is the root)."""
    if resource.path is not None and resource.path.is_dir():
        root = RichTree(escape(resource.path.name or str(resource.path)))
        _walk(resource.path, root, cfg.max_depth)
        return root
    lines = [line for line in resource.text.splitlines() if line.strip()]
    if not lines:
        raise ResourceError("--tree needs a directory or at least one line of text.")
    tree = RichTree(escape(lines[0]))
    for line in lines[1:]:
        tree.add(escape(line))
    return tree


def _walk(directory: Path, node: RichTree, depth: int) -> None:
    """Add ``directory``'s children to ``node`` down to ``depth`` levels."""
    if depth <= 0:
        return
    try:
        entries = sorted(directory.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except OSError:
        return
    for entry in entries:
        if entry.name.startswith("."):
            continue
        child = node.add(escape(entry.name + ("/" if entry.is_dir() else "")))
        if entry.is_dir():
            _walk(entry, child, depth - 1)


def _rst(resource: Resource, cfg: RenderConfig) -> RenderableType:
    """Render reStructuredText with ``rich-rst``."""
    from rich_rst import RestructuredText

    return RestructuredText(
        resource.text,
        code_theme=cfg.theme,
        default_lexer=cfg.lexer or "python",
        show_errors=False,
    )


def _ipynb(resource: Resource, cfg: RenderConfig) -> RenderableType:
    """Render a Jupyter notebook's cells and outputs (same layout as ``rich-cli``)."""
    try:
        notebook = json.loads(resource.text)
        cells_data = notebook["cells"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise ResourceError(f"Invalid notebook: {exc}") from exc
    language = cfg.lexer or notebook.get("metadata", {}).get("kernelspec", {}).get(
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
        item: RenderableType
        if cell.get("cell_type") == "code":
            item = RichPanel(
                RichSyntax(
                    slice_lines(source, cfg.head, cfg.tail),
                    language,
                    theme=cfg.theme,
                    line_numbers=cfg.line_numbers,
                    indent_guides=cfg.guides,
                    word_wrap=not cfg.no_wrap,
                ),
                border_style="dim",
            )
        elif cell.get("cell_type") == "markdown":
            item = RichMarkdown(source, code_theme=cfg.theme, hyperlinks=cfg.hyperlinks)
        else:
            item = RichText(source)
        blank_before = True
        cells.append(item)
        for output in cell.get("outputs", []):
            kind = output.get("output_type")
            if kind == "stream":
                item = RichText.from_ansi("".join(output["text"]))
                blank_before = False
            elif kind == "error":
                item = RichText.from_ansi("\n".join(output["traceback"]).rstrip())
                blank_before = True
            elif kind == "execute_result":
                count = output.get("execution_count") or " "
                plain = output.get("data", {}).get("text/plain", "")
                if isinstance(plain, list):
                    plain = "".join(plain)
                item = RichText.from_markup(
                    f"[red]Out[[#ee4b2b]{count}[/#ee4b2b]]:[/red]\n"
                ) + RichText.from_ansi(plain)
                blank_before = True
            else:
                continue
            cells.append(item)
    return Group(*cells)


def resolve_object(expression: str) -> Any:
    """Resolve a dotted ``module.attr`` path, falling back to ``eval``.

    Dotted paths are imported without ``eval``; any other expression is
    evaluated, exactly like ``rich --inspect``.

    Warning:
        Importing a dotted path executes that module, and any other expression
        is passed to ``eval``. Never pass untrusted text to ``--inspect``.

    Raises:
        ResourceError: If the expression cannot be resolved.
    """
    expression = expression.strip()
    parts = expression.split(".")
    if all(part.isidentifier() for part in parts):
        import builtins

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
        if hasattr(builtins, parts[0]):
            try:
                obj = getattr(builtins, parts[0])
                for attr in parts[1:]:
                    obj = getattr(obj, attr)
                return obj
            except AttributeError:
                pass
    try:
        return eval(expression, {})  # noqa: S307 - user-supplied CLI expression
    except Exception as exc:  # noqa: BLE001
        raise ResourceError(f"Unable to evaluate {expression!r}: {exc}") from exc


def _inspect(resource: Resource, cfg: RenderConfig) -> RenderableType:
    """Inspect the Python object named by the resource text."""
    return Inspect(resolve_object(resource.text), help=False, dunder=False, all=False, methods=True)


def build_inner(mode: Mode, resource: Resource, cfg: RenderConfig) -> RenderableType:
    """Build the plain Rich renderable for ``mode`` (before gradient styling)."""
    if mode is Mode.TEXT:
        return _text(resource, cfg)
    if mode is Mode.MARKDOWN:
        return RichMarkdown(
            resource.text,
            code_theme=cfg.theme,
            hyperlinks=cfg.hyperlinks,
            justify=cast(Any, cfg.text_align),
        )
    if mode is Mode.SYNTAX:
        return _syntax(resource, cfg)
    if mode is Mode.JSON:
        return _json(resource, cfg)
    if mode is Mode.CSV:
        return _csv(resource, cfg)
    if mode is Mode.TREE:
        return _tree(resource, cfg)
    if mode is Mode.RST:
        return _rst(resource, cfg)
    if mode is Mode.IPYNB:
        return _ipynb(resource, cfg)
    if mode is Mode.INSPECT:
        return _inspect(resource, cfg)
    if mode is Mode.COLUMNS:
        items = [line for line in resource.text.splitlines() if line.strip()]
        if not items:
            raise ResourceError("--columns needs at least one non-empty line.")
        return RichColumns([RichText.from_markup(escape(item)) for item in items])
    raise ValueError(f"Mode {mode.value!r} has no inner renderable.")


def resolve_expand(mode: Mode, cfg: RenderConfig) -> bool:
    """Decide whether the gradient spans the full width.

    Panels, Markdown and code fill the terminal; text, tables, JSON, trees and
    columns shrink to their content so the gradient is visible across it.
    """
    if cfg.expand is not None:
        return cfg.expand
    return cfg.panel or mode in {Mode.MARKDOWN, Mode.SYNTAX, Mode.RST, Mode.IPYNB}


def _gradient_kwargs(cfg: RenderConfig) -> dict[str, Any]:
    """Keyword arguments shared by every rich-gradient class."""
    return {
        "colors": parse_colors(cfg.colors),
        "bg_colors": parse_colors(cfg.bgcolors),
        "rainbow": cfg.rainbow,
        "hues": cfg.hues,
    }


def _highlights(cfg: RenderConfig) -> dict[str, Any]:
    """Highlight keyword arguments (``None`` when unset)."""
    return {
        "highlight_words": parse_mapping(cfg.highlight_words),
        "highlight_regex": parse_mapping(cfg.highlight_regex),
    }


def build_rule(resource: Resource, cfg: RenderConfig, *, animated: bool) -> RenderableType | Runnable:
    """Build a gradient rule whose title is the resource text."""
    title = resource.text.strip() or cfg.title or None
    kwargs: dict[str, Any] = {
        "title": title,
        "style": cfg.rule_style or cfg.style,
        "thickness": cfg.thickness,
        "characters": cfg.rule_char,
        "align": cfg.align,
        **_gradient_kwargs(cfg),
    }
    if animated:
        return cast(Runnable, AnimatedRule(**kwargs, duration=cfg.duration))
    return Rule(**kwargs)


def build_output(
    mode: Mode,
    resource: Resource,
    cfg: RenderConfig,
    console: Console,
    *,
    animated: bool,
) -> RenderableType | Runnable:
    """Build the final gradient renderable (or an animation to ``run()``).

    The plain renderable for ``mode`` is padded, then wrapped in a gradient
    ``Panel`` (``--panel``) or a plain ``Gradient``.
    """
    if mode is Mode.SPECTRUM:
        raise ValueError("Use spectrum_output() for --spectrum.")
    if mode is Mode.RULE:
        return build_rule(resource, cfg, animated=animated)

    inner = build_inner(mode, resource, cfg)
    expand = resolve_expand(mode, cfg)
    padding = parse_padding(cfg.padding)
    common = {**_gradient_kwargs(cfg), **_highlights(cfg)}

    if cfg.panel:
        panel_kwargs: dict[str, Any] = {
            "title": cfg.title,
            "subtitle": cfg.caption,
            "border_style": cfg.panel_style,
            "box": BOXES[cfg.box],
            "expand": expand,
            "justify": cfg.align,
            "vertical_justify": "top",
            "text_justify": cfg.align if cfg.text_align == "default" else cfg.text_align,
            **common,
        }
        if padding is not None:
            panel_kwargs["padding"] = padding
        if animated:
            return cast(
                Runnable,
                AnimatedPanel(
                    inner,
                    repeat_scale=cfg.repeat_scale or 4.0,
                    duration=cfg.duration,
                    **panel_kwargs,
                ),
            )
        return Panel(inner, **panel_kwargs)

    if padding is not None:
        inner = Padding(inner, padding)
    gradient_kwargs: dict[str, Any] = {
        "expand": expand,
        "justify": cfg.align,
        "vertical_justify": cfg.vertical_align,
        **common,
    }
    if animated:
        return cast(
            Runnable,
            AnimatedGradient(
                cast(Any, inner),
                repeat_scale=cfg.repeat_scale or 4.0,
                duration=cfg.duration,
                **gradient_kwargs,
            ),
        )
    gradient = Gradient(cast(Any, inner), repeat_scale=cfg.repeat_scale, **gradient_kwargs)
    if expand:
        return gradient
    # rich-gradient always spans the available width, so shrink that width to
    # the content to make the gradient visible across it.
    content_width = Measurement.get(console, console.options, inner).maximum
    constrained = Constrain(gradient, min(content_width, console.width))
    if cfg.align == "left":
        return constrained
    return Align(constrained, align=cast(Any, cfg.align))


def spectrum_output(cfg: RenderConfig) -> RenderableType:
    """Render the palette as a table, or as plain ``names``/``hex``/``csv`` text."""
    spectrum = Spectrum(hues=cfg.hues)
    if cfg.spectrum_output == "names":
        return RichText("\n".join(spectrum.names))
    if cfg.spectrum_output == "hex":
        return RichText("\n".join(spectrum.hex))
    if cfg.spectrum_output == "csv":
        return RichText("\n".join(f"{n},{h}" for n, h in zip(spectrum.names, spectrum.hex)))
    return cast(RenderableType, spectrum.rich)


__all__ = [
    "RenderConfig",
    "Runnable",
    "build_inner",
    "build_output",
    "build_rule",
    "resolve_expand",
    "slice_lines",
    "spectrum_output",
]
