# rich-gradient-cli

`gradient` is a single-command CLI for [`rich-gradient`](https://github.com/maxludden/rich-gradient), modeled on [`rich-cli`](https://github.com/Textualize/rich-cli). Give it a file, a URL, `-` for stdin, or literal text and it renders the content with a gradient.

```bash
uv tool install rich-gradient-cli
gradient --colors 'red,#ff9900,#ffff00' "Hello gradient"
```

![Gradient text](img/commands/text-example.svg)

## How it works

- One command: `gradient [OPTIONS] [PATH,TEXT,URL, or '-']`.
- The renderable is auto-detected from the extension, or forced with a flag (`--markdown`, `--rst`, `--ipynb`, `--json`, `--csv`, `--syntax`, `--rule`, `--tree`, `--columns`, `--spectrum`, `--inspect`).
- Layout, styling and export flags use the same short options as `rich-cli`.
- Gradient flags (`--colors`, `--bgcolors`, `--rainbow`, `--animate`, ...) apply to whatever is rendered.

See [Usage](usage.md) for examples and [Options](options.md) for every flag.
