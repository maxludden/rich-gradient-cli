# Commands

## print

Render gradient text.

```bash
gradient print --colors 'red,#ff9900,#ffff00' "Hello gradient"
```

Arguments: `TEXT...` (optional). If omitted, `print` reads from stdin when piped.

| Option | Description |
| --- | --- |
| `-c, --colors` | Comma-separated gradient colors. |
| `-r, --rainbow` | Use rainbow colors. |
| `-h, --hues` | Number of hues for a random gradient. |
| `--style` | Rich style string (non-color styles only). |
| `-j, --justify` | `left`, `center`, or `right`. |
| `--overflow` | `crop`, `fold`, or `ellipsis`. |
| `--no-wrap` | Disable wrapping. |
| `--tab-size` | Number of spaces used to render tabs. |
| `--markup/--no-markup` | Enable or disable Rich markup parsing. |
| `--end` | String appended after output. |
| `--bgcolors` | Comma-separated background colors. |
| `--svg` | Save output as SVG. |
| `-a, --animate` | Animate gradient text. |
| `-d, --duration` | Animation duration in seconds. |
| `--repeat-scale` | Animated gradient repeat scale. |

Note: `print` returns an error if `--svg` and `--animate` are used together.

## gradient

Render text through rich-gradient's generic `Gradient` renderable.

```bash
gradient gradient --colors 'magenta,cyan' --highlight-word error='bold white on red' "Highlight error text"
```

Argument: `TEXT` (required). Use `-` to read from stdin.

| Option | Description |
| --- | --- |
| `-c, --colors` | Comma-separated gradient colors. |
| `--bgcolors` | Comma-separated background colors. |
| `-r, --rainbow` | Use rainbow colors. |
| `--hues` | Number of hues for a random gradient. |
| `--expand/--no-expand` | Expand to full width. |
| `-j, --justify` | `left`, `center`, or `right`. |
| `--vertical-justify` | `top`, `middle`, or `bottom`. |
| `--repeat-scale` | Gradient repeat scale. |
| `--highlight-word` | Highlight `WORD=STYLE`; may be repeated. |
| `--highlight-regex` | Highlight `PATTERN=STYLE`; may be repeated. |
| `--end` | String appended after output. |
| `-a, --animate` | Animate gradient. |
| `-d, --duration` | Animation duration in seconds. |
| `--svg` | Save output as SVG. |

Note: `gradient` returns an error if `--svg` and `--animate` are used together.

## spectrum

Render rich-gradient's `Spectrum` colors.

```bash
gradient spectrum --hues 7 --seed 42
```

| Option | Description |
| --- | --- |
| `-h, --hues` | Number of spectrum colors. |
| `--invert` | Reverse the generated colors. |
| `--seed` | Seed for deterministic color selection. |
| `-o, --output` | `table`, `names`, `hex`, or `csv`. |
| `--end` | String appended after output. |
| `--svg` | Save table output as SVG. |

## columns

Render Rich `Columns` through `Gradient`.

```bash
gradient columns alpha beta gamma --colors 'red,blue'
```

Arguments: `ITEM...` (optional). If omitted, `columns` reads one item per stdin line.

| Option | Description |
| --- | --- |
| `-c, --colors` | Comma-separated gradient colors. |
| `--bgcolors` | Comma-separated background colors. |
| `-r, --rainbow` | Use rainbow colors. |
| `--hues` | Number of hues for a random gradient. |
| `-p, --padding` | Column padding. |
| `--width` | Fixed column width. |
| `--columns-expand` | Expand columns to full width. |
| `--equal` | Use equal-width columns. |
| `--column-first` | Fill columns before rows. |
| `--right-to-left` | Render columns right-to-left. |
| `--align` | Column content alignment. |
| `--title` | Columns title. |
| `--expand/--no-expand` | Expand the gradient wrapper. |
| `-j, --justify` | Gradient justification. |
| `--vertical-justify` | Gradient vertical justification. |
| `--repeat-scale` | Gradient repeat scale. |
| `--highlight-word` | Highlight `WORD=STYLE`; may be repeated. |
| `--highlight-regex` | Highlight `PATTERN=STYLE`; may be repeated. |
| `--end` | String appended after output. |
| `-a, --animate` | Animate gradient. |
| `-d, --duration` | Animation duration in seconds. |
| `--svg` | Save output as SVG. |

## tree

Render Rich `Tree` through `Gradient`.

```bash
gradient tree project src/app.py docs/index.md --colors 'lime,cyan'
```

Arguments: `ROOT BRANCH...`. Branch values are slash-delimited paths. Use `--path` to render a directory tree from `ROOT`.

| Option | Description |
| --- | --- |
| `--path` | Treat `ROOT` as a directory path. |
| `--max-depth` | Maximum directory depth for `--path`. |
| `--style` | Tree branch style. |
| `--guide-style` | Tree guide-line style. |
| `--expanded/--collapsed` | Expand or collapse tree nodes. |
| `--highlight` | Enable Rich label highlighting. |
| `--hide-root` | Hide the root label. |
| `-c, --colors` | Comma-separated gradient colors. |
| `--bgcolors` | Comma-separated background colors. |
| `-r, --rainbow` | Use rainbow colors. |
| `--hues` | Number of hues for a random gradient. |
| `--expand/--no-expand` | Expand the gradient wrapper. |
| `-j, --justify` | Gradient justification. |
| `--vertical-justify` | Gradient vertical justification. |
| `--repeat-scale` | Gradient repeat scale. |
| `--highlight-word` | Highlight `WORD=STYLE`; may be repeated. |
| `--highlight-regex` | Highlight `PATTERN=STYLE`; may be repeated. |
| `--end` | String appended after output. |
| `-a, --animate` | Animate gradient. |
| `-d, --duration` | Animation duration in seconds. |
| `--svg` | Save output as SVG. |

## syntax

Render Rich `Syntax` through `Gradient`.

```bash
gradient syntax pyproject.toml --lexer toml --line-numbers --colors 'yellow,magenta'
```

Argument: `PATH_OR_CODE` (required). Use `-` or `--code` to render inline/stdin code.

| Option | Description |
| --- | --- |
| `-x, --lexer` | Pygments lexer. |
| `--theme` | Pygments theme. |
| `-n, --line-numbers` | Show line numbers. |
| `--word-wrap` | Enable word wrapping. |
| `-g, --guides` | Show indentation guides. |
| `--dedent` | Dedent code before rendering. |
| `--start-line` | Starting line number. |
| `--code-width` | Syntax code width. |
| `--tab-size` | Tab size. |
| `--background-color` | Syntax background color. |
| `-p, --padding` | Syntax padding. |
| `--code` | Treat `PATH_OR_CODE` as code text. |
| `-c, --colors` | Comma-separated gradient colors. |
| `--bgcolors` | Comma-separated background colors. |
| `-r, --rainbow` | Use rainbow colors. |
| `--hues` | Number of hues for a random gradient. |
| `--expand/--no-expand` | Expand the gradient wrapper. |
| `-j, --justify` | Gradient justification. |
| `--vertical-justify` | Gradient vertical justification. |
| `--repeat-scale` | Gradient repeat scale. |
| `--highlight-word` | Highlight `WORD=STYLE`; may be repeated. |
| `--highlight-regex` | Highlight `PATTERN=STYLE`; may be repeated. |
| `--end` | String appended after output. |
| `-a, --animate` | Animate gradient. |
| `-d, --duration` | Animation duration in seconds. |
| `--svg` | Save output as SVG. |

## table

Render CSV data as a Rich `Table` through `Gradient`.

```bash
cat data.csv | gradient table - --colors 'cyan,magenta'
```

Argument: `CSV_OR_ROWS` (required). Pass a CSV file path, inline CSV text, or `-` for stdin.

| Option | Description |
| --- | --- |
| `--delimiter` | CSV delimiter. |
| `--no-header` | Treat all rows as data. |
| `--title` | Table title. |
| `--caption` | Table caption. |
| `--table-width` | Fixed table width. |
| `--table-expand` | Expand the table. |
| `--show-lines` | Draw row separators. |
| `--safe-box/--unsafe-box` | Toggle safe box characters. |
| `-c, --colors` | Comma-separated gradient colors. |
| `--bgcolors` | Comma-separated background colors. |
| `-r, --rainbow` | Use rainbow colors. |
| `--hues` | Number of hues for a random gradient. |
| `--expand/--no-expand` | Expand the gradient wrapper. |
| `-j, --justify` | Gradient justification. |
| `--vertical-justify` | Gradient vertical justification. |
| `--repeat-scale` | Gradient repeat scale. |
| `--highlight-word` | Highlight `WORD=STYLE`; may be repeated. |
| `--highlight-regex` | Highlight `PATTERN=STYLE`; may be repeated. |
| `--end` | String appended after output. |
| `-a, --animate` | Animate gradient. |
| `-d, --duration` | Animation duration in seconds. |
| `--svg` | Save output as SVG. |

## rule

Render a gradient rule.

```bash
gradient rule --colors 'blue,#00ff00,cyan' --title "Blue to Green to Cyan Rule"
```

This command has no positional arguments; use `--title` for rule text.

| Option | Description |
| --- | --- |
| `-t, --title` | Rule title text. |
| `-s, --title-style` | Rich style for title text. |
| `-c, --colors` | Comma-separated gradient colors. |
| `--bgcolors` | Comma-separated background colors. |
| `-r, --rainbow` | Use rainbow colors. |
| `--hues` | Number of hues for a random gradient. |
| `--end` | String appended after output. |
| `-T, --thickness` | Line thickness (0-3). |
| `--characters` | Characters used to draw the rule line. |
| `--style` | Rich style for the rule. |
| `-a, --align` | `left`, `center`, or `right`. |
| `--svg` | Save output as SVG. |
| `--animate` | Animate gradient. |
| `-d, --duration` | Animation duration in seconds. |
| `--repeat-scale` | Animated gradient repeat scale. |

Note: `rule` returns an error if `--svg` and `--animate` are used together.

## panel

Render a gradient panel.

```bash
gradient panel --colors "red,#ff9999" -t "Error" --title-style "bold #ffffff" --title-align left 'This is an error message with a red to pink gradient background.'
```

Argument: `TEXT` (required). Use `-` to read from stdin.

| Option | Description |
| --- | --- |
| `-c, --colors` | Comma-separated gradient colors. |
| `--bgcolors` | Comma-separated background colors. |
| `-r, --rainbow` | Use rainbow colors. |
| `--hues` | Number of hues for a random gradient. |
| `-t, --title` | Panel title text. |
| `--title-style` | Style for the title. |
| `--title-align` | `left`, `center`, or `right`. |
| `-s, --subtitle` | Panel subtitle text. |
| `--subtitle-style` | Style for the subtitle. |
| `--subtitle-align` | `left`, `center`, or `right`. |
| `--style` | Panel style. |
| `--border-style` | Border style. |
| `-p, --padding` | Padding in 1, 2, or 4 integers. |
| `--safe-box` | Use box characters safe for legacy Windows terminals. |
| `-V, --vertical-justify` | `top`, `middle`, or `bottom`. |
| `-J, --text-justify` | `left`, `center`, or `right`. |
| `-j, --justify` | Panel alignment: `left`, `center`, `right`. |
| `--expand/--no-expand` | Expand to full width. |
| `--width` | Fixed width (use with `--no-expand`). |
| `--height` | Fixed height. |
| `--highlight-word` | Highlight `WORD=STYLE`; may be repeated. |
| `--highlight-regex` | Highlight `PATTERN=STYLE`; may be repeated. |
| `--end` | String appended after output. |
| `--box` | Border box style. |
| `-a, --animate` | Animate gradient. |
| `-d, --duration` | Animation duration in seconds. |
| `--repeat-scale` | Animated gradient repeat scale. |
| `--svg` | Save output as SVG. |

Note: `panel` returns an error if `--svg` and `--animate` are used together.

## markdown

Render gradient markdown.

```bash
echo "# Hello" | gradient markdown -
```

Argument: `MARKDOWN` (required). Use `-` to read from stdin.

| Option | Description |
| --- | --- |
| `-c, --colors` | Comma-separated gradient colors. |
| `--bgcolors` | Comma-separated background colors. |
| `-r, --rainbow` | Use rainbow colors. |
| `--hues` | Number of hues for a random gradient. |
| `--style` | Rich style for markdown text. |
| `-j, --justify` | `left`, `center`, or `right`. |
| `--vertical-justify` | `top`, `middle`, or `bottom`. |
| `--expand/--no-expand` | Expand markdown renderables to full width. |
| `--repeat-scale` | Gradient repeat scale. |
| `--highlight-word` | Highlight `WORD=STYLE`; may be repeated. |
| `--highlight-regex` | Highlight `PATTERN=STYLE`; may be repeated. |
| `--no-wrap` | Disable wrapping. |
| `--end` | String appended after output. |
| `--animate` | Animate gradient. |
| `-d, --duration` | Animation duration in seconds. |
| `--svg` | Save output as SVG. |

Note: `markdown` returns an error if `--svg` and `--animate` are used together.

## view

Render files, URLs, stdin, or markup with Rich-CLI-style behavior.

```bash
gradient view README.md
```

```bash
gradient view pyproject.toml --lexer toml --line-numbers --guides
```

```bash
cat data.json | gradient view - --json --force-terminal
```

Argument: `PATH_OR_URL` (required). Use `-` to read from stdin.

Auto-detection uses the resource extension: Markdown (`.md`), JSON (`.json`), CSV/TSV (`.csv`, `.tsv`), otherwise syntax highlighting.

| Option | Description |
| --- | --- |
| `-p, --print` | Treat input as Rich console markup. |
| `--syntax` | Render as syntax-highlighted text. |
| `-m, --markdown` | Render as Markdown. |
| `-J, --json` | Render as JSON. |
| `--csv` | Render CSV/TSV as a table. |
| `-u, --rule` | Render a horizontal rule. |
| `-h, --head` | Display first lines for syntax or CSV output. |
| `-t, --tail` | Display last lines for syntax or CSV output. |
| `--theme` | Pygments syntax theme; also reads `RICH_THEME`. |
| `-x, --lexer` | Pygments lexer override. |
| `-n, --line-numbers` | Show syntax line numbers. |
| `-g, --guides` | Show syntax indentation guides. |
| `--no-wrap` | Disable syntax word wrap. |
| `-y, --hyperlinks` | Render Markdown links as terminal hyperlinks. |
| `-j, --emoji` | Enable emoji markup. |
| `-l, --left` | Align output block left. |
| `-c, --center` | Align output block center. |
| `-r, --right` | Align output block right. |
| `-L, --text-left` | Justify text left. |
| `-C, --text-center` | Justify text center. |
| `-R, --text-right` | Justify text right. |
| `-F, --text-full` | Fully justify text. |
| `-w, --width` | Render output at a fixed width. |
| `-W, --max-width` | Constrain console print width. |
| `-s, --style` | Rich style for the output. |
| `-d, --padding` | Padding around output. |
| `-a, --panel` | Draw a panel around output. |
| `-S, --panel-style` | Style the panel border. |
| `--title` | Panel/table title. |
| `--caption` | Panel/table caption. |
| `-e, --expand` | Expand panel or padding. |
| `--rule-style` | Rich style for `--rule`. |
| `--rule-char` | Character used for `--rule`. |
| `--force-terminal` | Keep terminal color when output is captured or piped. |
| `-o, --export-html` | Write rendered output as HTML. |
| `--export-svg` | Write rendered output as SVG. |
| `--pager` | Display output in a pager. |
