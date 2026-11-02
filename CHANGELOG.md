# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

### Added

- Added opt-in, anonymous usage telemetry via Amplitude (`amplitude-analytics`). It is off by default; `gradient telemetry enable|disable|status` manages it. When enabled and `AMPLITUDE_API_KEY` is set, each subcommand run sends a `Command Run` event with the subcommand name and a random install ID. Events are sent only after a command completes successfully (not for `--help` or usage errors), flushing is bounded by a 5-second timeout, and the config is written atomically.
- Documented the `telemetry` commands and the root `--help` screenshot in `docs/commands.md`, and added them to the SVG generator.

## 0.3.0 - 2026-11-01

### Added

- Added `scripts/generate_command_svgs.py`, which generates an example SVG and a `--help` SVG for every `gradient` command (plus the root `--help`) into `docs/img/commands/`, and embedded them in `docs/commands.md`.
- Added a GitHub Actions workflow that builds and publishes to PyPI (trusted publishing) when a release is published. It first checks that the tag matches the package version, then runs ruff, mypy, pytest and a docs build.
- Added VS Code tasks to build and serve the docs with Zensical and to build the package with `uv`.
- Added a VS Code launch configuration that runs the CLI as a module.
- Added `.vscode/settings.json` with the project interpreter and watcher/search/analysis excludes for `.venv`, `site`, `dist` and tool caches, to keep VS Code responsive.
- Tuned `.vscode/settings.json` for speed: Pylance checks open files only, and the `.cache`, `.git/objects` and `typings` paths are excluded from watching, search and analysis.

### Changed

- Migrated the docs site config from `mkdocs.yml` (Material for MkDocs) to `zensical.toml`, matching `rich-gradient`; the `docs` extra now installs `zensical` instead of `mkdocs`/`mkdocs-material` and requires Python 3.11+.
- Renamed `docs/assets/` to `docs/img/` (links to `docs/assets/...` no longer resolve) and replaced `MaxLogo-animated.svg` with the static `MaxLogo.svg`.
- Removed the `ty:ignore[unresolved-import]` comments on the `click`/`typer` imports; `mypy` is the project's type checker.
- The release workflow now tests on Python 3.10 and 3.12 and checks that the built distributions match the release tag before publishing.
- Docs palette toggle cycles auto, light and dark; the auto entry now uses `astral-light` instead of duplicating `astral-dark`.
- Pointed the docs "edit this page" links at `edit/master/docs/`.
- Bumped the package version to 0.3.0.

### Fixed

- Fixed `test_view_print_treats_resource_as_markup_text` by parsing ANSI output with `Text.from_ansi` before asserting.

## 0.2.0 - 2026-06-02

### Added

- Added `gradient view`, a Rich-CLI-style file viewer for Markdown, JSON, CSV/TSV, syntax-highlighted source, stdin, and URLs.
- Added `gradient gradient` for the generic `rich-gradient` `Gradient` and `AnimatedGradient` renderables.
- Added `gradient spectrum` for `rich-gradient` `Spectrum` table, names, hex, CSV, and SVG output.
- Added `gradient columns`, `gradient tree`, `gradient syntax`, and `gradient table` convenience commands that wrap Rich renderables with `rich-gradient` `Gradient`.
- Added CLI access to highlights, repeat scale, safe boxes, custom rule characters, text markup toggling, tab size, and text/rule animation options.
- Added `view` support for Rich markup printing, horizontal rules, pager output, HTML export, SVG export, syntax themes, lexers, line numbers, indentation guides, wrapping, alignment, padding, and panels.
- Added CLI regression coverage for `view` Markdown auto-detection, JSON rendering, HTML export, stdin Markdown, Rich markup printing, generic gradients, spectrum output, text markup toggling, and custom rule characters.
- Documented the new `view` command in the README and MkDocs pages.

### Changed

- Centered the custom Rich help header title across root and subcommand help output.
- Changed `gradient --version` to read the installed package version from metadata instead of a hard-coded constant.
- Reserved `-h` for `view --head` by keeping help on `--help`.
