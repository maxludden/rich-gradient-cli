# Commands

## print

Render gradient text.

```bash
gradient print --colors 'red,#ff9900,#ffff00' "Hello gradient"
```

| Option | Description |
| --- | --- |
| `-c, --colors` | Comma-separated gradient colors. |
| `-r, --rainbow` | Use rainbow colors. |
| `-h, --hues` | Number of hues for a random gradient. |
| `--style` | Rich style string (non-color styles only). |
| `-j, --justify` | `left`, `center`, or `right`. |
| `--overflow` | `crop`, `fold`, or `ellipsis`. |
| `--no-wrap` | Disable wrapping. |
| `--end` | String appended after output. |
| `--bgcolors` | Comma-separated background colors. |
| `--svg` | Save output as SVG. |

## rule

Render a gradient rule.

```bash
gradient rule --colors 'blue,#00ff00,cyan' "Blue to Green to Cyan Rule"
```

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
| `-a, --align` | `left`, `center`, or `right`. |
| `--svg` | Save output as SVG. |

## panel

Render a gradient panel.

```bash
gradient panel --colors "red,#ff9999" -t "Error" --title-style "bold #ffffff" --title-align left 'This is an error message with a red to pink gradient background.'
```

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
| `-V, --vertical-justify` | `top`, `middle`, or `bottom`. |
| `-J, --text-justify` | `left`, `center`, or `right`. |
| `-j, --justify` | Panel alignment: `left`, `center`, `right`. |
| `--expand/--no-expand` | Expand to full width. |
| `--width` | Fixed width (use with `--no-expand`). |
| `--height` | Fixed height. |
| `--end` | String appended after output. |
| `--box` | Border box style. |
| `-a, --animate` | Animate gradient. |
| `-d, --duration` | Animation duration in seconds. |
| `--svg` | Save output as SVG. |

## markdown

Render gradient markdown.

```bash
echo "# Hello" | gradient markdown -
```

| Option | Description |
| --- | --- |
| `-c, --colors` | Comma-separated gradient colors. |
| `--bgcolors` | Comma-separated background colors. |
| `-r, --rainbow` | Use rainbow colors. |
| `--hues` | Number of hues for a random gradient. |
| `--style` | Rich style for markdown text. |
| `-j, --justify` | `left`, `center`, or `right`. |
| `--vertical-justify` | `top`, `middle`, or `bottom`. |
| `--no-wrap` | Disable wrapping. |
| `--end` | String appended after output. |
| `--animate` | Animate gradient. |
| `-d, --duration` | Animation duration in seconds. |
| `--svg` | Save output as SVG. |
