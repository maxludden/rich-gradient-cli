# rich-gradient-cli

 `rich-gradient-cli`  is a CLI for [`rich-gradient`](https://github.com/maxludden/rich-gradient). The tool allows you to create colorful gradients in your terminal output, making it easier to visualize data or simply add some flair to your command-line applications.

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

<video
  src="docs/assets/rich-gradient-cli-help.mp4"
  controls
  muted
  loop>
</video>

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

## Docs

Build and preview the documentation locally with MkDocs:

```bash
uv pip install -e ".[docs]"
mkdocs serve
```



<div align="center">
  <a href="https://github.com/maxludden/maxludden" style="text-decoration:none; color:inherit;">
      <p>Designed by Max Ludden</p>
  </a>
  <br />
  <a href="https://github.com/maxludden/maxludden" style="text-decoration:none; color:inherit;">
    <img
      src="docs/assets/MaxLogo-animated.svg"
      alt="Max Ludden's Logo"
      width="20%"
    />
  </a>
</div>
