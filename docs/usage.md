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

`markdown` and `panel` do not allow `--svg` with `--animate`.
