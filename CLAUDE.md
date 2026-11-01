# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`rich-gradient-cli` is the terminal CLI for [`rich-gradient`](../rich-gradient) (a separate sibling package/dependency). It wraps `rich-gradient`'s renderables (Text, Gradient, Panel, Rule, Markdown, Spectrum, and generic Rich renderables like Table/Tree/Columns/Syntax) as Typer subcommands, plus a `view` command that does `rich-cli`-style auto-detected file rendering.

## Commands

Use `uv` for everything.

- Install: `uv sync` (or `uv pip install -e ".[dev]"`)
- Run tests: `uv run pytest`
- Run a single test: `uv run pytest tests/test_cli.py -k test_name`
- Lint: `uv run ruff check .`
- Type check: `uv run mypy`
- Docs (local preview): `uv pip install -e ".[docs]"` then `zensical serve` (Python 3.11+ only; the `docs` extra is skipped on 3.10)
- Manual CLI smoke test: `uv run gradient print --colors 'red,orange' "hello"` (the console-script entrypoint is `gradient`, defined in `pyproject.toml` as `gradient = "rich_gradient_cli:entrypoint"`)

## Architecture

- **`__init__.py`** builds the Typer `app` and registers every subcommand (`print`, `gradient`, `columns`, `panel`, `rule`, `markdown`, `spectrum`, `syntax`, `table`, `tree`, `view`). It uses a custom `DefaultTyperGroup` (subclass of `RichTyperGroup` from `help.py`) so that when no subcommand is given, unrecognized args are routed to the `print` command by default — e.g. `gradient "hello"` behaves like `gradient print "hello"`.
- Each `*_command.py` module (`text_command.py`, `gradient_command.py`, `panel_command.py`, `rule_command.py`, `markdown_command.py`, `spectrum_command.py`) implements one Typer subcommand and is responsible for parsing its own CLI flags into `rich-gradient` constructor args.
- **`renderable_commands.py`** holds the generic Rich-renderable wrappers (`columns_command`, `syntax_command`, `table_command`, `tree_command`) that don't need their own file.
- **`common.py`** has the shared argument-parsing helpers (color lists, styles, etc.) — reuse these instead of re-parsing color/style strings in a new command.
- **`help.py`** defines `RichTyperCommand`/`RichTyperGroup`, the shared Rich-themed help rendering used by every registered command — use these classes (not bare `typer.Typer`/`click.Command`) when adding a new subcommand so help output stays consistent.
- **`view_command.py`** (largest module) is the `rich-cli`-style file viewer: auto-detects Markdown/JSON/CSV/TSV/source files, accepts `-` for stdin and `http://`/`https://` URLs, and supports `--export-html`.
- This package only depends on `rich-gradient` for rendering — it does not duplicate gradient/color math. If a bug looks like it's in color interpolation rather than CLI argument handling, it likely belongs in the `rich-gradient` repo instead.

## Notes

- The CLI used to live inside `rich-gradient` itself; it was split out into this package as of `rich-gradient` v0.3.12. Don't reintroduce CLI code into `rich-gradient` — extend it here.
- `docs/` + `zensical.toml` back the published docs site; `site/` is a generated build artifact (not hand-edited, and per `.gitignore`/history is no longer tracked).
