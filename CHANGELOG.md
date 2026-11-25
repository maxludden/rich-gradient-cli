# Changelog

All notable changes to this project will be documented in this file.

## 0.4.8 - 2026-11-25

### Added

- `.github/workflows/homebrew.yml` updates the `rich-gradient-cli` formula in [`maxludden/homebrew-tap`](https://github.com/maxludden/homebrew-tap). It runs daily (or by hand with a version), and once the latest PyPI release is a day old (Homebrew resolves Python resources with a 1-day upload cooldown) it points the formula at the new sdist, regenerates the Python resources with `brew bump-formula-pr --write-only`, builds and tests the formula from source, and pushes the commit. It needs a `HOMEBREW_TAP_TOKEN` secret with write access to the tap.

### Changed

- The README and Usage page's Homebrew instructions now run `brew trust maxludden/tap` before installing (recent Homebrew refuses formulae from untrusted third-party taps) and note that releases reach the tap about a day after PyPI.

## 0.4.7 - 2026-11-24

### Changed

- The build backend is now [hatchling](https://hatch.pypa.io/) (`hatchling>=1.27`) instead of `uv_build`. The wheel has the same files, entry point and metadata; the sdist now also includes `CHANGELOG.md`.

## 0.4.6 - 2026-11-24

### Changed

- The build backend requirement is now `uv_build>=0.13.9,<0.14.0` (was `>=0.10.0,<0.11.0`), matching current uv and silencing its version warning.

## 0.4.5 - 2026-11-24

### Changed

- Regenerated all doc screenshots with 0.4.5.
- `--spectrum` shows the full 17-color palette by default instead of 5 hues. `--hues N` still limits it; gradients from `--rainbow` or no `--colors` keep the default of 5.
- Regenerated the `--help` and `--spectrum-output` doc screenshots for the new `--hues` help text and the 17-color palette.

## 0.4.4 - 2026-11-24

### Added

- `--border-only` (with `--panel`) paints only the panel border and title with the gradient, leaving the content's own colors alone (rich-gradient 0.4.4's `border_only`).
- Warnings when `--title`/`--caption` are given without `--panel` (outside CSV and rule mode), when `--panel` is used with `--rule`, and when `--border-only` is used without `--panel`; these were silently ignored.
- `.github/workflows/docs.yml` builds the docs with Zensical and deploys them to GitHub Pages on every push to `master` (or by manual dispatch).

### Fixed

- An invalid `--colors`/`--bgcolors` color, an invalid `--highlight-regex` pattern, or an invalid style in `--highlight-word`/`--highlight-regex`/`--rule-style` is now a usage error (exit 2) instead of a traceback.
- `--panel-style` with a foreground color (e.g. `-S red`, `-S 'bold white'`) now colors the panel border. rich-gradient replaces a border color with the gradient, so the color was silently dropped and only attributes such as bold applied. The content still gets the gradient. With `--animate` the gradient border is kept and a warning is printed.
- `--rule` titles are centered by default, matching Rich's and rich-gradient's `Rule`; `-l`/`-r` still align them left or right.
- `--rule-char` with more than one character is a usage error (exit 2) instead of a runtime error.
- `--export-svg`/`--export-html` pointing at an existing directory fails before rendering, instead of printing the output and then erroring.

### Changed

- Requires `rich-gradient>=0.4.4` (locked to 0.4.5). 0.4.4 fixes `--panel --animate` (`AnimatedPanel` rejected `text_justify`) and full-width animated panels. `rich-gradient` is exempt from `exclude-newer`, like the docs theme.
- `--inspect` uses rich-gradient's `Inspect`, so attribute names, values and signatures keep Rich's colors inside the gradient frame, and `--panel BOX`, `--title` and `--panel-style` style that frame. `--inspect --animate` still uses Rich's report.
- Rewrote the README and docs for readability: install options per tool, a "what gets rendered" table, an options-at-a-glance table, option tables with descriptions on the Options page, the missing notebook/columns/spectrum/markup screenshots on the Usage page, and a link to the published docs. Regenerated the doc screenshots (panel style, rule, inspect, and the rich-gradient 0.4.5 spectrum). The README header image uses an absolute URL so it shows on PyPI.
- The docs site now uses [`zensical-gradient-theme`](https://pypi.org/project/zensical-gradient-theme/) (`name = "gradient"`), the same theme as the rich-gradient docs. It supplies the variant, fonts, gradient-dark/light palette and feature list, so `zensical.toml` no longer sets them.
- The `docs` extra now requires `zensical>=0.1.3` and adds `zensical-gradient-theme>=0.1.1`.
- `[tool.uv]` now sets `exclude-newer = "3 days"` in the project (so CI resolves like local) and exempts `zensical-gradient-theme` via `exclude-newer-package`, so new theme releases are picked up immediately.

### Removed

- The custom `docs/styles/style.css` and `docs/styles/extra.css` overrides (astral palette, local font paths); the theme replaces them.

## 0.4.3 - 2026-11-06

### Fixed

- Syntax-highlighted output (`--lexer`, source files, notebook code cells) keeps its token colors instead of being flattened to the gradient; only plain code, line numbers and the panel border take the gradient.
- An expanding `--panel` fills the full width, so the border and its content share one gradient ramp (needs `rich-gradient` 0.4.3, which fixes the panel measuring).

### Changed

- Requires `rich-gradient>=0.4.3`.

## 0.4.2 - 2026-11-06

### Fixed

- README links and images now use absolute URLs so they work on PyPI (relative paths 404 there); added `[project.urls]` metadata.

### Changed

- Regenerated all doc screenshots in the style of the rich-gradient site (rich-gradient's `GRADIENT_TERMINAL_THEME`, narrow window, vivid gradients, the command as the window title).
- `--rule-char` help now says it takes a single character (a longer string was always rejected).

### Added

- One screenshot per option in `docs/img/options/` (gradient, layout and content options), embedded in `docs/options.md`, plus new `print` and `ipynb` mode examples. `scripts/generate_command_svgs.py` generates them all.

## 0.4.1 - 2026-11-06

### Fixed

- Literal text longer than the OS path limit is no longer misreported as "File name too long"; path probing falls back to literal text.
- `gradient -` no longer crashes with a traceback on non-UTF-8 stdin; it reports a clean error like files and URLs.
- `--width` and `--max-width` can be combined: the maximum now clamps the width.
- A bad `--export-svg`/`--export-html` destination is now detected before rendering, and I/O errors name the file.
- Exporting both `--export-svg` and `--export-html` in one run no longer writes an empty HTML file (the SVG export cleared the recording).
- URL downloads are capped at 10 MB.
- `--head`/`--tail`, `--text-*` and `--vertical-align` now warn when they are ignored for the selected mode.
- `--tree .` labels the root with the real directory name instead of `.` (ported from the pre-rewrite `tree` fix). The pre-rewrite stdin-routing and missing-syntax-file fixes no longer apply: the subcommands they patched were removed in 0.4.0.

### Changed

- `--inspect` help and docs warn that it imports/evaluates its argument (never pass untrusted text).
- Removed unused `Align`/`TextAlign` enums and a redundant `--hues` clamp.

### Added

- Tests for `render.py` and `export.py`, plus regression tests for the fixes above.

## 0.4.0 - 2026-11-06

### Changed

- **Breaking:** rewrote the CLI as a single command modeled on `rich-cli`: `gradient [OPTIONS] [PATH,TEXT,URL, or '-']`. The renderable is auto-detected from the file extension or chosen with a mode flag. The subcommands are gone:
  `print` -> `gradient TEXT` (or `-p`), `gradient` -> `--highlight-word/--highlight-regex/--animate`, `panel` -> `--panel BOX`, `rule` -> `--rule`, `markdown` -> `--markdown`, `spectrum` -> `--spectrum`, `syntax` -> `--syntax`, `table` -> `--csv`, `tree` -> `--tree`, `columns` -> `--columns`, `view` -> the same flags on the main command, `telemetry enable|disable|status` -> `--telemetry enable|disable|status`.
- Shared flags now match `rich-cli`: `-p --print`, `-u --rule`, `-a --panel BOX`, `-d --padding`, `-s --style`, `-S --panel-style`, `-l/-c/-r`, `-L/-C/-R/-F`, `-w/-W`, `-h/-t` (head/tail), `-n -g -x -y -j`, `-o --export-html`, `--export-svg`, `--pager`, `-v --version`. Only `--help` shows help. Gradient options (`--colors`, `--bgcolors`, `--rainbow`, `--hues`, `--repeat-scale`, `--highlight-word`, `--highlight-regex`, `--animate`, `--duration`) are long-only.
- Requires Python 3.11+ and `rich-gradient>=0.4.1`, `rich>=15`, `rich-color-ext>=3` (the CI matrix is 3.11/3.12).
- Telemetry events now report the render mode instead of a subcommand name.
- Replaced the per-command docs and SVGs with `docs/options.md`, a rewritten usage page, and one set of example screenshots generated by `scripts/generate_command_svgs.py`.

### Added

- Added an MIT `LICENSE` file and declared `license = "MIT"` / `license-files` in `pyproject.toml`, so the license shows up on PyPI and in downstream packaging (e.g. the Homebrew tap formula).
- Documented Homebrew installation (`brew install maxludden/tap/rich-gradient-cli`) in the README.
- `--rst` (reStructuredText, auto-detected for `.rst`), `--ipynb` (Jupyter notebooks, auto-detected for `.ipynb`) and `--inspect` (inspect a Python object by dotted path or expression), plus the `rich-rst` dependency.
- Panel `none` box and `-e/--expand/--no-expand`.
- Added a `dev` dependency group with `pytest` and VS Code settings that enable pytest test discovery in `tests/`.
- Added opt-in, anonymous usage telemetry via Amplitude (`amplitude-analytics`). It is off by default; `gradient --telemetry enable|disable|status` manages it. When enabled and `AMPLITUDE_API_KEY` is set, each successful run sends a `Command Run` event with the render mode and a random install ID. Events are sent only after a command completes successfully (not for `--help` or usage errors), flushing is bounded by a 5-second timeout, and the config is written atomically.

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
