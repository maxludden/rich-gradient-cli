# Usage

## Installation

`rich-gradient-cli` requires Python 3.11 or newer. Install it with any of:

```bash
uv tool install rich-gradient-cli               # uv
pip install rich-gradient-cli                   # pip
```

With Homebrew, trust the tap first. Homebrew won't load formulae from a third-party tap until you do:

```bash
brew tap maxludden/tap
brew trust maxludden/tap
brew install maxludden/tap/rich-gradient-cli
```

New releases reach the Homebrew tap about a day after PyPI.

Check that it works with `gradient --version`.

## Text

Literal text and stdin (`echo "piped text" | gradient -`) are printed as gradient text. Rich console markup such as `[b]bold[/b]` is parsed unless you pass `--no-markup`.

```bash
--8<-- "docs/snippets/commands/text.sh"
```

![text](img/commands/text.svg)

```bash
--8<-- "docs/snippets/commands/print.sh"
```

![print](img/commands/print.svg)

To style particular words or patterns, use `--highlight-word WORD=STYLE` or `--highlight-regex PATTERN=STYLE`. Both can be repeated.

```bash
--8<-- "docs/snippets/commands/highlight.sh"
```

![highlight](img/commands/highlight.svg)

## Files and URLs

The file extension picks the renderable:

| Extension | Rendered as |
|---|---|
| `.md`, `.markdown` | Markdown |
| `.rst` | reStructuredText |
| `.ipynb` | Jupyter notebook |
| `.json` | Pretty-printed JSON |
| `.csv`, `.tsv` | Table |
| `.txt`, no extension | Gradient text |
| anything else | Syntax-highlighted code |

`http(s)://` URLs and `-` (stdin) work the same way as files. A URL uses the extension of its path. Stdin has no extension, so add a mode flag such as `--markdown` when you pipe in anything other than plain text.

```bash
gradient README.md
gradient doc.rst
gradient notebook.ipynb
gradient data.csv
gradient config.json
gradient pyproject.toml -n -g --head 20
gradient https://example.com/page.md
```

```bash
--8<-- "docs/snippets/commands/markdown.sh"
```

![markdown](img/commands/markdown.svg)

```bash
--8<-- "docs/snippets/commands/rst.sh"
```

![rst](img/commands/rst.svg)

```bash
--8<-- "docs/snippets/commands/ipynb.sh"
```

![ipynb](img/commands/ipynb.svg)

```bash
--8<-- "docs/snippets/commands/json.sh"
```

![json](img/commands/json.svg)

```bash
--8<-- "docs/snippets/commands/csv.sh"
```

![csv](img/commands/csv.svg)

```bash
--8<-- "docs/snippets/commands/syntax.sh"
```

![syntax](img/commands/syntax.svg)

## Panels and rules

`--panel BOX` wraps any renderable in a gradient panel. The box styles are `ascii`, `ascii2`, `square`, `rounded`, `heavy`, `double` and `none`. Add `--title` and `--caption` to label the panel, and `--border-only` to color just the border and leave the content as it is.

`--rule` draws a horizontal rule with the text as its title.

```bash
--8<-- "docs/snippets/commands/panel.sh"
```

![panel](img/commands/panel.svg)

```bash
--8<-- "docs/snippets/commands/rule.sh"
```

![rule](img/commands/rule.svg)

## Trees, columns, spectrum and inspect

`--tree` shows a directory (or lines of text) as a tree, `--columns` lays each line out as a column cell, `--spectrum` shows the color palette, and `--inspect` reports on a Python object.

```bash
--8<-- "docs/snippets/commands/tree.sh"
```

![tree](img/commands/tree.svg)

```bash
--8<-- "docs/snippets/commands/columns.sh"
```

![columns](img/commands/columns.svg)

```bash
--8<-- "docs/snippets/commands/spectrum.sh"
```

![spectrum](img/commands/spectrum.svg)

```bash
--8<-- "docs/snippets/commands/inspect.sh"
```

![inspect](img/commands/inspect.svg)

!!! warning
    `--inspect` imports or evaluates its argument as Python. Never pass it text you don't trust.

## Animation

`--animate` animates the gradient in an interactive terminal. Add `--duration SECONDS` to stop automatically; otherwise press <kbd>Ctrl</kbd>+<kbd>C</kbd> to stop it.

When the output is not a terminal (for example, piped to a file), a single static frame is printed instead. `--animate` cannot be combined with `--export-svg`, `--export-html` or `--pager`.

## Export and paging

```bash
gradient README.md --export-svg readme.svg   # print, then also save as SVG
gradient README.md -o readme.html            # ... or as HTML
gradient README.md --pager                   # scroll through it in a pager
```

## Telemetry

Telemetry is off by default. Manage it with `gradient --telemetry enable|disable|status`. Even when enabled, events are sent only if `AMPLITUDE_API_KEY` is also set.
