# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

### Fixed

- Fixed `gradient` crashing with `AttributeError` when text is piped in with no arguments (e.g. `echo hi | gradient`).
- Fixed `gradient syntax` printing a traceback for a missing or unreadable file; it now reports a usage error.
- Fixed `gradient tree --path --max-depth N` listing files one level deeper than directories.
- Fixed `gradient tree . --path` showing an empty root label; it now uses the real directory name.
- Fixed the `view --print` test expecting plain text under `--force-terminal`.

### Added

- Added regression tests for piped stdin routing, missing `syntax` files, and `tree --path` depth and root label.

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
