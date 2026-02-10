# rich-gradient-cli

This is an example of a Markdown file that can be used to demonstrate the capabilities of the `rich-gradient-cli` tool. The tool allows you to create colorful gradients in your terminal output, making it easier to visualize data or simply add some flair to your command-line applications.

## Installation

You can install rich-gradient-cli from PyPI

### uv (recommended)

```shell
uv add rich-gradient-cli
```

### pip

```shell
pip install rich-gradient-cli
```

## Usage


### Print

To use the `rich-gradient-cli`, you can run the following command in your terminal:

```bash
gradient print --colors 'red,#ff9900,#ffff00' "This is gradient text that starts red, transitions through orange, and ends in yellow\!"
```

![Gradient Text Example](print-example.svg)


### Rule

You can also create gradient rules using the `rule` command:

```bash
gradient rule --colors 'blue,#00ff00,cyan' "Blue to Green to Cyan Rule"
```

![Gradient Rule Example](rule-example.svg)

### Panel

To create a gradient panel, you can use the `panel` command:

```bash
gradient panel --colors "red,#ff9999" -t "Error" --title-style "bold #ffffff" --title-align left 'This is an error message with a red to pink gradient background.'
```

![Gradient Panel Example](panel-example.svg)

### Markdown

You can also render Markdown with gradients:

```bash
echo "# Hello\n\n- This is **bold**.\n- This is *italic*." | gradient markdown -
```

![Gradient Markdown Example](markdown-example.svg)
