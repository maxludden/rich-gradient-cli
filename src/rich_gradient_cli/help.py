"""Custom Rich help rendering for Typer commands."""

from __future__ import annotations

import io
import re
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Tuple

import click
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from typer.core import TyperCommand, TyperGroup

from .common import (
    FOOTER_TEXT,
    HEADER_TEXT,
    USAGE_BRACKET_STYLE,
    USAGE_CMD_STYLE,
    USAGE_PREFIX,
    USAGE_PROG_STYLE,
)


@dataclass(frozen=True)
class HelpStyles:
    border: str = "#2a4fff"
    option_name: str = "cyan"
    metavar: str = "bold #99ff00"
    help_text: str = "white"
    dim: str = "dim"


_STYLES = HelpStyles()


def _usage_markup(command_path: str, pieces: Sequence[str]) -> str:
    parts = command_path.split()
    prog = parts[0] if parts else ""
    subcommands = parts[1:]

    def color_token(token: str) -> str:
        if token.startswith("[") and token.endswith("]"):
            inner = token[1:-1]
            return (
                f"[{USAGE_BRACKET_STYLE}][[/][{USAGE_CMD_STYLE}]"
                f"{inner}[/][{USAGE_BRACKET_STYLE}]][/]"
            )
        if token.startswith("[") and token.endswith("]..."):
            inner = token[1:-4]
            return (
                f"[{USAGE_BRACKET_STYLE}][[/][{USAGE_CMD_STYLE}]"
                f"{inner}[/][{USAGE_BRACKET_STYLE}]][/]"
                f"[{USAGE_CMD_STYLE}]...[/]"
            )
        if token.isupper() or re.match(r"^[A-Z_]+(\.\.\.)?$", token):
            return f"[{USAGE_CMD_STYLE}]{token}[/]"
        return token

    colored_prog = f"[{USAGE_PROG_STYLE}]{prog}[/]" if prog else ""
    colored_subcommands = " ".join(
        f"[{USAGE_CMD_STYLE}]{cmd}[/]" for cmd in subcommands
    )
    args = " ".join(color_token(piece) for piece in pieces)
    if args:
        args = f"  {args}"
    usage = " ".join(p for p in [colored_prog, colored_subcommands] if p)
    return f"{USAGE_PREFIX} {usage}{args}".strip()


def _split_option_name(name: str) -> Tuple[str, str]:
    parts = name.split()
    if not parts:
        return name, ""
    last = parts[-1]
    if not last.startswith("-") and last.isupper():
        return " ".join(parts[:-1]), last
    return name, ""


def _normalize_metavar(metavar: str) -> str:
    value = metavar.strip()
    if value.startswith("[") and value.endswith("]..."):
        value = value[1:-4]
    elif value.startswith("[") and value.endswith("]"):
        value = value[1:-1]
    if value.endswith("..."):
        value = value[:-3]
    return value


def _build_arguments_table(
    args: Iterable[click.Argument], ctx: click.Context
) -> Optional[Table]:
    rows: List[Tuple[str, str]] = []
    for arg in args:
        metavar = _normalize_metavar(arg.make_metavar(ctx))
        rows.append((metavar, metavar))

    if not rows:
        return None

    table = Table.grid(padding=(0, 2))
    table.add_column(justify="left", style="bold #ffff00", no_wrap=True)
    table.add_column(justify="left", style=_STYLES.metavar)
    for name, meta in rows:
        table.add_row(name, meta)
    return table


def _build_options_table(
    options: Iterable[click.Option], ctx: click.Context
) -> Optional[Table]:
    rows: List[Tuple[str, str, Text]] = []
    for opt in options:
        record = opt.get_help_record(ctx)
        if record is None:
            continue
        name, help_text = record
        opt_names, metavar = _split_option_name(name)
        help_rich = Text.from_markup(help_text, style=_STYLES.help_text)
        rows.append((opt_names, metavar, help_rich))

    if not rows:
        return None

    table = Table.grid(padding=(0, 2))
    table.add_column(justify="left", style="bold #ffff00", no_wrap=True)
    table.add_column(justify="left", style=_STYLES.metavar, no_wrap=True)
    table.add_column(justify="left", style=_STYLES.help_text)
    for opt_names, metavar, help_rich in rows:
        table.add_row(opt_names, metavar, help_rich)
    return table


def _build_commands_table(group: click.Group) -> Optional[Table]:
    if not group.commands:
        return None

    table = Table.grid(padding=(0, 2))
    table.add_column(justify="left", style="bold #ffff00", no_wrap=True)
    table.add_column(justify="left", style=_STYLES.help_text)
    for name, cmd in group.commands.items():
        help_text = cmd.get_short_help_str() if cmd.help else ""
        table.add_row(name, help_text)
    return table


def render_help(command: click.Command, ctx: click.Context) -> str:
    """Render help text for a Click command using Rich for formatting."""
    console = Console(
        record=True,
        force_terminal=True,
        color_system="truecolor",
        file=io.StringIO(),
    )

    console.print(Text.from_markup(HEADER_TEXT))
    console.print()

    usage_line = _usage_markup(ctx.command_path, command.collect_usage_pieces(ctx))
    console.print(Text.from_markup(usage_line))

    if command.help:
        console.print()
        console.print(Text.from_markup(command.help))

    args = [p for p in command.params if isinstance(p, click.Argument)]
    options = [p for p in command.params if isinstance(p, click.Option)]

    args_table = _build_arguments_table(args, ctx)
    if args_table is not None:
        console.print()
        console.print(
            Panel(
                args_table,
                title="[b #ffffff]Arguments[/]",
                title_align="left",
                border_style=_STYLES.border,
                box=box.SQUARE,
            )
        )

    options_table = _build_options_table(options, ctx)
    if options_table is not None:
        console.print()
        console.print(
            Panel(
                options_table,
                title="[b #ffffff]Options[/]",
                title_align="left",
                border_style=_STYLES.border,
                box=box.SQUARE,
            )
        )

    if isinstance(command, click.Group):
        commands_table = _build_commands_table(command)
        if commands_table is not None:
            console.print()
            console.print(
                Panel(
                    commands_table,
                    title="[b #ffffff]Commands[/]",
                    title_align="left",
                    border_style=_STYLES.border,
                    box=box.SQUARE,
                )
            )

    console.print()
    console.print(Text.from_markup(FOOTER_TEXT))

    return console.export_text(styles=True)


class RichTyperCommand(TyperCommand):
    """Custom TyperCommand that uses Rich for help rendering."""

    def get_help(self, ctx: click.Context) -> str:  # type: ignore[override]
        return render_help(self, ctx).rstrip("\n")


class RichTyperGroup(TyperGroup):
    """Custom TyperGroup that uses Rich for help rendering."""

    def get_help(self, ctx: click.Context) -> str:  # type: ignore[override]
        return render_help(self, ctx).rstrip("\n")
