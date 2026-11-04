# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`rich-gradient-cli` is the terminal CLI for [`rich-gradient`](../rich-gradient) (a separate sibling package/dependency). It is a **single command**, `gradient`, modeled on [`rich-cli`](https://github.com/Textualize/rich-cli): `gradient [OPTIONS] [PATH,TEXT,URL, or '-']`. The renderable is auto-detected from the file extension or forced with a mode flag, and shared flags keep `rich-cli`'s spelling (`-p --print`, `-u --rule`, `-m`, `-J`, `-a --panel BOX`, `-d`, `-s`, `-S`, `-l/-c/-r`, `-L/-C/-R/-F`, `-w/-W`, `-h/-t`, `-n -g -x -y -j`, `-o`, `--export-svg`, `--pager`, `-v`). Gradient-specific options are long-only.

## Commands

Use `uv` for everything.

- Install: `uv sync --extra dev`
- Run tests: `uv run pytest`
- Run a single test: `uv run pytest tests/test_cli.py -k test_name`
- Lint: `uv run ruff check .`
- Type check: `uv run mypy`
- Docs (local preview): `uv pip install -e ".[docs]"` then `zensical serve`
- Regenerate doc screenshots: `uv run python scripts/generate_command_svgs.py`
- Smoke test: `uv run gradient --colors 'red,orange' "hello"` (entrypoint is `gradient = "rich_gradient_cli:entrypoint"`)

## Architecture

- **`cli.py`** defines the Typer `app` and the single `main` command: all options (grouped with `rich_help_panel`), mutual-exclusion checks, and the render/export/pager flow. Usage errors exit 2, runtime errors exit 1.
- **`resource.py`** resolves the positional argument (file, URL, `-`/stdin, or literal text) into a `Resource` and picks a `Mode` from the extension.
- **`render.py`** turns a `Resource` + `RenderConfig` into a plain Rich renderable per `Mode` (text, markdown, rst, ipynb, syntax, json, csv, tree, columns, inspect, rule) and wraps it in a `rich-gradient` `Gradient`/`Panel` (or the animated variants).
- **`options.py`** parses raw option strings (colors, padding, styles, `WORD=STYLE` mappings, panel boxes).
- **`export.py`** writes SVG/HTML via a recording console.
- **`telemetry.py`** is opt-in anonymous usage telemetry (`--telemetry enable|disable|status`; needs `AMPLITUDE_API_KEY` too). `__init__.entrypoint` sends the event only after a successful run.
- This package depends on `rich-gradient` for gradient/color math; interpolation bugs belong in that repo.

## Notes

- Python 3.11+ (required by `rich-gradient` 0.4).
- The CLI used to have subcommands (`print`, `panel`, `view`, ...) up to 0.3; they were replaced by flags on the one command. Don't reintroduce subcommands.
- `docs/` + `zensical.toml` back the published docs site; `site/` is a generated build artifact.
- Add a `CHANGELOG.md` entry with every change.
