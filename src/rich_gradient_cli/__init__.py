"""rich-gradient CLI entry point."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Sequence

import click  # ty:ignore[unresolved-import]
import typer  # ty:ignore[unresolved-import]

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from rich_gradient_cli.common import VERSION
    from rich_gradient_cli.help import RichTyperCommand, RichTyperGroup
    from rich_gradient_cli.markdown_command import markdown_command
    from rich_gradient_cli.panel_command import panel_command
    from rich_gradient_cli.rule_command import rule_command
    from rich_gradient_cli.text_command import print_command
else:
    from .common import VERSION
    from .help import RichTyperCommand, RichTyperGroup
    from .markdown_command import markdown_command
    from .panel_command import panel_command
    from .rule_command import rule_command
    from .text_command import print_command


class DefaultTyperGroup(RichTyperGroup):
    """Route unknown commands/options to the default command."""

    def __init__(
        self,
        name: str | None = None,
        commands: dict[str, click.Command] | Sequence[click.Command] | None = None,
        invoke_without_command: bool = False,
        no_args_is_help: bool | None = None,
        subcommand_metavar: str | None = None,
        chain: bool = False,
        result_callback: Any | None = None,
        *,
        default_cmd_name: str = "print",
        **kwargs: Any,
    ) -> None:
        """Initialize the group with a default command name fallback."""
        super().__init__(
            name=name,
            commands=commands,
            invoke_without_command=invoke_without_command,
            no_args_is_help=no_args_is_help,
            subcommand_metavar=subcommand_metavar,
            chain=chain,
            result_callback=result_callback,
            **kwargs,
        )
        self.default_cmd_name: str = default_cmd_name

    def resolve_command(
        self, ctx: click.Context, args: list[str]
    ) -> tuple[str | None, click.Command | None, list[str]]:
        """Resolve the command, routing unknown input to the default command."""
        if args:
            cmd = self.get_command(ctx, args[0])
            if cmd is None or args[0].startswith("-"):
                args.insert(0, self.default_cmd_name)
        return super().resolve_command(ctx, args)


app = typer.Typer(
    cls=DefaultTyperGroup,
    invoke_without_command=True,
    add_completion=False,
    help="Create gradient-rich text, panels, and markdown.",
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"], "color": True},
)


@app.callback()
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        help="Show the version and exit.",
        is_eager=True,
    ),
) -> None:
    """CLI entry callback for version handling and default routing."""
    if version:
        typer.echo(f"gradient version {VERSION}")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        if ctx.args or not sys.stdin.isatty():
            print_command(text=list(ctx.args) if ctx.args else None)
            raise typer.Exit()
        typer.echo(ctx.get_help())


app.command("print", cls=RichTyperCommand)(print_command)
app.command("panel", cls=RichTyperCommand)(panel_command)
app.command("rule", cls=RichTyperCommand)(rule_command)
app.command("markdown", cls=RichTyperCommand)(markdown_command)


cli = app


def entrypoint() -> None:
    """Run the Typer CLI application."""
    app()

__all__ = ["app", "cli", "entrypoint"]


if __name__ == "__main__":
    entrypoint()
