# Changelog

All notable changes to this project will be documented in this file.

## 0.3.0 - 2026-11-01

### Added

- Added a GitHub Actions workflow that builds and publishes to PyPI (trusted publishing) when a release is published. It first checks that the tag matches the package version, then runs ruff, mypy, pytest and a docs build.
- Added VS Code tasks to build and serve the docs with Zensical and to build the package with `uv`.
- Added a VS Code launch configuration that runs the CLI as a module.

### Changed

- Migrated the docs site config from `mkdocs.yml` (Material for MkDocs) to `zensical.toml`, matching `rich-gradient`; the `docs` extra now installs `zensical` instead of `mkdocs`/`mkdocs-material` and requires Python 3.11+.
- Renamed `docs/assets/` to `docs/img/` (links to `docs/assets/...` no longer resolve) and replaced `MaxLogo-animated.svg` with the static `MaxLogo.svg`.
- Removed the `ty:ignore[unresolved-import]` comments on the `click`/`typer` imports; `mypy` is the project's type checker.
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
