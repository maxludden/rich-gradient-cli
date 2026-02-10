# Usage

## Installation

```bash
uv add rich-gradient-cli
```

```bash
pip install rich-gradient-cli
```

## Basics

The CLI is installed as `gradient`.

```bash
gradient --help
```

The default command is `print`, so you can pass text directly.

```bash
gradient "Hello world"
```

## Reading from stdin

Any command that accepts text can read from stdin with `-`.

```bash
echo "Hello" | gradient print -
```

```bash
echo "# Title" | gradient markdown -
```

## SVG export

Use `--svg` to export a renderable to an SVG file.

```bash
gradient print "SVG output" --svg output.svg
```

```bash
gradient panel "Panel SVG" --svg panel.svg
```
