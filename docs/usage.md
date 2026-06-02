# Usage

## Installation

```bash
uv add rich-gradient-cli
```

```bash
pip install rich-gradient-cli
```

Requires Python `>=3.10`.

## Basics

The CLI is installed as `gradient`.

```bash
gradient --help
```

Show the installed version:

```bash
gradient --version
```

The default command is `print`, so you can pass text directly without writing `print`.

```bash
gradient "Hello world"
```

Equivalent explicit form:

```bash
gradient print "Hello world"
```

## Reading from stdin

`print` can read piped input directly:

```bash
echo "Hello" | gradient
```

Commands that accept positional text can also read from stdin with `-`.

```bash
echo "Hello" | gradient print -
```

```bash
echo "Hello" | gradient gradient -
```

```bash
echo "# Title" | gradient markdown -
```

```bash
echo "Failure details" | gradient panel - --title "Error"
```

## SVG export

Use `--svg` to export a renderable to an SVG file.

```bash
gradient print "SVG output" --svg output.svg
```

```bash
gradient panel "Panel SVG" --svg panel.svg
```

```bash
gradient spectrum --svg spectrum.svg
```

`print`, `gradient`, `rule`, `markdown`, and `panel` do not allow `--svg` with `--animate`.

## Highlighting

Commands backed by `Gradient`, `Panel`, and `Markdown` can apply highlight rules.

```bash
gradient gradient "error: retry later" --highlight-word error="bold white on red"
```

```bash
gradient markdown "# Status" --highlight-regex "Status=bold cyan"
```

## Spectrum output

Use `spectrum` to inspect generated colors.

```bash
gradient spectrum --hues 7 --seed 42
```

```bash
gradient spectrum --hues 7 --output hex
```

## Rich renderables

Wrap common Rich renderables in gradients.

```bash
gradient columns alpha beta gamma --colors "red,blue"
```

```bash
gradient tree project src/app.py docs/index.md --colors "lime,cyan"
```

```bash
gradient syntax pyproject.toml --lexer toml --line-numbers --colors "yellow,magenta"
```

```bash
cat data.csv | gradient table - --colors "cyan,magenta"
```

## Rich-style file viewing

Use `view` when you want behavior closer to `rich-cli`: render files, URLs, or stdin with Rich's Markdown, JSON, CSV table, and syntax-highlighting renderers.

```bash
gradient view README.md
```

```bash
gradient view pyproject.toml --lexer toml --line-numbers --guides
```

```bash
cat data.json | gradient view - --json --force-terminal
```

You can also export the rendered output.

```bash
gradient view README.md --export-html readme.html
```

```bash
gradient view README.md --export-svg readme.svg
```
