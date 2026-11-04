# rich-gradient-cli

`gradient` is a single-command CLI for [`rich-gradient`](https://github.com/maxludden/rich-gradient), modeled on [`rich-cli`](https://github.com/Textualize/rich-cli): point it at a file, a URL, `-` for stdin, or literal text and it renders the result with a gradient.

```text
gradient [OPTIONS] [PATH,TEXT,URL, or '-']
```

## Installation

```shell
uv tool install rich-gradient-cli   # or: pip install rich-gradient-cli
```

Requires Python 3.11+.

## Usage

The renderable is chosen from the file extension (`.md`, `.rst`, `.ipynb`, `.json`, `.csv`/`.tsv`, source code) or by a mode flag, exactly like `rich-cli`. Literal text and stdin are printed as gradient text.

```bash
gradient --colors 'red,#ff9900,#ffff00' "Gradient text that runs red, orange, yellow!"
gradient README.md                        # Markdown, auto-detected
gradient pyproject.toml -n -g             # syntax with line numbers and guides
gradient data.csv --colors cyan,magenta   # table
gradient notebook.ipynb                   # Jupyter notebook
cat doc.rst | gradient - --rst            # reStructuredText from stdin
gradient https://example.com/page.md      # URL
gradient "Title" --rule --colors blue,cyan
gradient "Heads up" --panel rounded --title Notice
gradient str --inspect                    # inspect a Python object
gradient --spectrum --hues 7
gradient --tree src                       # directory tree
gradient README.md --export-svg out.svg   # also: -o out.html, --pager
```

![Gradient text](docs/img/commands/text-example.svg)

### Options at a glance

Shared flags keep their `rich-cli` spelling (`-p --print`, `-u --rule`, `-m --markdown`, `-J --json`, `-a --panel BOX`, `-d --padding`, `-s --style`, `-S --panel-style`, `-l/-c/-r` block alignment, `-L/-C/-R/-F` text justify, `-w/-W` width, `-h/-t` head/tail, `-n -g -x -y -j`, `-o --export-html`, `--export-svg`, `--pager`, `-v --version`). Gradient-specific options are long-only: `--colors`, `--bgcolors`, `--rainbow`, `--hues`, `--repeat-scale`, `--highlight-word`, `--highlight-regex`, `--animate`, `--duration`.

See [docs/options.md](docs/options.md) or run `gradient --help` for the grouped list.

### From `0.3` subcommands

Versions up to 0.3 used subcommands (`gradient print`, `gradient panel`, `gradient view`, ...). They were replaced by flags on the one command; see the [CHANGELOG](CHANGELOG.md) for the mapping.

### Telemetry

Anonymous usage telemetry is **off by default**. `gradient --telemetry enable|disable|status` manages it; when enabled and `AMPLITUDE_API_KEY` is set, a `Command Run` event with the render mode and a random install ID is sent after a command succeeds.

## Docs

Build and preview the documentation locally with [Zensical](https://zensical.org):

```bash
uv pip install -e ".[docs]"
zensical serve
```

<div align="center">
  <a href="https://github.com/maxludden/maxludden" style="text-decoration:none; color:inherit;">
      <p>Designed by Max Ludden</p>
  </a>
  <br />
  <a href="https://github.com/maxludden/maxludden" style="text-decoration:none; color:inherit;">
    <img
      src="docs/img/MaxLogo.svg"
      alt="Max Ludden's Logo"
      width="20%"
    />
  </a>
</div>
