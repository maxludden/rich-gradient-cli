"""Generate terminal-screenshot SVGs for the single ``gradient`` command.

The look matches the SVGs on https://maxludden.github.io/rich-gradient: the
``GRADIENT_TERMINAL_THEME`` (black background), a narrow window, and the command
line as the window title. Each example is run as a subprocess with forced
colour output; the ANSI result is replayed into a recording Rich console and
exported.

Outputs (``uv run python scripts/generate_command_svgs.py``):

* ``docs/img/commands/`` - ``help.svg`` plus one ``<mode>-example.svg`` per renderable.
* ``docs/img/options/`` - one ``<option>.svg`` per gradient/layout/content/output option.

``--animate`` and ``--pager`` need an interactive terminal and have no SVG.
"""

from __future__ import annotations

import os
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

from rich.console import Console
from rich.text import Text
from rich_gradient.theme import GRADIENT_TERMINAL_THEME

ROOT = Path(__file__).resolve().parent.parent
COMMANDS_OUT = ROOT / "docs" / "img" / "commands"
OPTIONS_OUT = ROOT / "docs" / "img" / "options"
WIDTH = 72
HELP_WIDTH = 100  # --help tables need more room than the examples
TITLE_MAX = 78

CSV = "name,language,stars\nrich,python,50000\ntyper,python,15000\nuv,rust,40000\n"
SEMI_CSV = "name;language;stars\nrich;python;50000\ntyper;python;15000\n"
PY = "def greet(name):\n    if name:\n        for _ in range(2):\n            print(f'hi {name}')\n"
LOREM = "Gradients make terminal output easier to scan and a lot more fun to read."

#: One command: ``(argv after "gradient", optional stdin)``.
Command = tuple[list[str], str | None]
#: An example is one or more commands stacked in a single screenshot, plus an optional title.
Example = tuple[list[Command], str | None]


def one(argv: list[str], stdin: str | None = None) -> Example:
    """Build an example that runs a single command."""
    return ([(argv, stdin)], None)


def many(*argvs: list[str], title: str | None = None) -> Example:
    """Build an example that stacks several commands in one screenshot."""
    return ([(argv, None) for argv in argvs], title)


# Renderable modes -> docs/img/commands/<name>-example.svg
MODES: dict[str, Example] = {
    "text": one(["--colors", "red,#ff9900,#ffff00,lime,cyan", "-s", "bold", "Hello gradient"]),
    "highlight": one(
        ["--colors", "magenta,cyan", "--highlight-word", "error=bold white on red",
         "-s", "bold", "Highlight error text"],
    ),
    "markdown": one(["-", "--markdown", "--colors", "magenta,cyan"],
                    "# Hello\n\nSome **bold** and *italic* text.\n\n- one\n- two\n"),
    "panel": one(["--panel", "rounded", "--title", "Error", "--colors", "red,#ff7090",
                  "-s", "bold", "This is an error message."]),
    "rule": one(["--rule", "Blue to Green to Cyan", "--colors", "blue,#00ff00,cyan"]),
    "spectrum": one(["--spectrum", "--hues", "7"]),
    "syntax": one(["pyproject.toml", "--lexer", "toml", "--line-numbers", "--head", "8",
                   "--colors", "yellow,magenta"]),
    "json": one(["-", "--json", "--colors", "cyan,magenta"],
                '{"name": "gradient", "tags": ["cli", "rich"], "stars": 5}'),
    "csv": one(["-", "--csv", "--colors", "cyan,magenta"], CSV),
    "tree": one(["--tree", "src", "--colors", "lime,cyan"]),
    "columns": one(["-", "--columns", "--colors", "red,blue"],
                   "alpha\nbeta\ngamma\ndelta\nepsilon\n"),
    "rst": one(["-", "--rst", "--colors", "orange,magenta"],
               "Title\n=====\n\nSome *emphasis* and a list:\n\n- one\n- two\n"),
    "inspect": one(["str", "--inspect", "--colors", "green,cyan"]),
    "ipynb": one(["-", "--ipynb", "--colors", "cyan,magenta"],
                 '{"cells":[{"cell_type":"code","execution_count":1,"source":["print(1 + 1)"],'
                 '"outputs":[{"output_type":"stream","text":["2\\n"]}]}],'
                 '"metadata":{"kernelspec":{"language":"python"}}}'),
    "print": one(["-p", "[bold]Bold[/bold], [italic]italic[/italic] and [u]underlined[/u]",
                  "--colors", "red,gold,lime"]),
}

# Options -> docs/img/options/<name>.svg
OPTIONS: dict[str, Example] = {
    # --- Gradient ---------------------------------------------------------------
    "colors": one(["--colors", "red,#ff9900,#ffff00,lime,cyan,magenta", "-s", "bold",
                   "Any Rich, CSS or hex colors"]),
    "bgcolors": one(["--colors", "white", "--bgcolors", "navy,purple", "-s", "bold",
                     "Background gradient"]),
    "rainbow": one(["--rainbow", "-s", "bold", "Rainbow gradient text"]),
    "hues": many(["--hues", "3", "-s", "bold", "Three hues"],
                 ["--hues", "9", "-s", "bold", "Nine hues, a smoother sweep"],
                 title="gradient --hues N"),
    "repeat-scale": many(["--repeat-scale", "1", "--rule", "repeat 1", "--colors", "red,cyan"],
                         ["--repeat-scale", "3", "--rule", "repeat 3", "--colors", "red,cyan"],
                         title="gradient --repeat-scale N"),
    "highlight-word": one(["--colors", "magenta,cyan", "-s", "bold",
                           "--highlight-word", "error=bold white on red",
                           "--highlight-word", "ok=bold black on lime",
                           "ok ok error ok"]),
    "highlight-regex": one(["--colors", "magenta,cyan", "-s", "bold",
                            "--highlight-regex", r"\d+=bold black on yellow",
                            "Build 42 passed in 7 seconds"]),
    # --- Layout -----------------------------------------------------------------
    "align": many(["--left", "-w", "60", "--colors", "red,gold", "-s", "bold", "left"],
                  ["--center", "-w", "60", "--colors", "red,gold", "-s", "bold", "center"],
                  ["--right", "-w", "60", "--colors", "red,gold", "-s", "bold", "right"],
                  title="gradient --left | --center | --right"),
    "text-align": many(
        ["-L", "-w", "44", "--colors", "cyan,magenta", LOREM],
        ["-C", "-w", "44", "--colors", "cyan,magenta", LOREM],
        ["-R", "-w", "44", "--colors", "cyan,magenta", LOREM],
        ["-F", "-w", "44", "--colors", "cyan,magenta", LOREM],
        title="gradient -L | -C | -R | -F",
    ),
    "width": many(["-w", "30", "--colors", "lime,cyan", LOREM],
                  ["-W", "40", "--colors", "lime,cyan", "short"],
                  title="gradient --width / --max-width"),
    "expand": many(["--expand", "--colors", "red,blue", "-s", "bold", "expanded"],
                   ["--no-expand", "--panel", "square", "--colors", "red,blue", "shrunk"],
                   title="gradient --expand / --no-expand"),
    "padding": one(["--panel", "rounded", "-d", "1,6", "--colors", "yellow,magenta",
                    "-s", "bold", "1 line, 6 columns of padding"]),
    "panel-boxes": many(
        *(["--panel", box, "--colors", "cyan,magenta", "--no-expand", "-s", "bold", box]
          for box in ("ascii", "square", "rounded", "heavy", "double")),
        title="gradient --panel BOX",
    ),
    "panel-style": one(["--panel", "heavy", "--panel-style", "bold white", "--colors", "red,gold",
                        "-s", "bold", "A white panel border"]),
    "title-caption": one(["--panel", "rounded", "--title", "Build", "--caption", "42 passed",
                          "--colors", "lime,cyan", "-s", "bold", "All checks passed."]),
    # --- Content ----------------------------------------------------------------
    "style": one(["--colors", "orange,magenta", "-s", "bold italic underline", "Styled text"]),
    "no-markup": many(["--colors", "cyan,magenta", "[bold]markup[/bold] is parsed"],
                      ["--no-markup", "--colors", "cyan,magenta", "[bold]markup[/bold] is literal"],
                      title="gradient --markup / --no-markup"),
    "emoji": one(["-j", "--colors", "yellow,magenta", "-s", "bold", "Ship it :rocket: :sparkles:"]),
    "head-tail": many(["pyproject.toml", "--syntax", "--head", "4", "--colors", "yellow,magenta"],
                      ["pyproject.toml", "--syntax", "--tail", "4", "--colors", "yellow,magenta"],
                      title="gradient --head N / --tail N"),
    "lexer-theme": one(["-", "--syntax", "--lexer", "python", "--theme", "dracula",
                        "--colors", "cyan,magenta"], PY),
    "line-numbers": one(["-", "--syntax", "--lexer", "python", "-n", "--colors", "lime,cyan"], PY),
    "guides": one(["-", "--syntax", "--lexer", "python", "-g", "--colors", "orange,magenta"], PY),
    "rule-style": many(["--rule", "thickness 0", "--thickness", "0", "--colors", "cyan,magenta"],
                       ["--rule", "thickness 1", "--thickness", "1", "--colors", "cyan,magenta"],
                       ["--rule", "thickness 2", "--thickness", "2", "--colors", "cyan,magenta"],
                       ["--rule", "thickness 3", "--thickness", "3", "--colors", "cyan,magenta"],
                       ["--rule", "custom char", "--rule-char", "*", "--colors", "cyan,magenta"],
                       title="gradient --rule --thickness N / --rule-char"),
    "delimiter": one(["-", "--csv", "--delimiter", ";", "--colors", "cyan,magenta"], SEMI_CSV),
    "no-header": one(["-", "--csv", "--no-header", "--colors", "cyan,magenta"], CSV),
    "max-depth": many(["--tree", "src", "--max-depth", "1", "--colors", "lime,cyan"],
                      ["--tree", "src", "--max-depth", "3", "--colors", "lime,cyan"],
                      title="gradient --tree --max-depth N"),
    "spectrum-output": many(["--spectrum", "--spectrum-output", "names", "--hues", "5"],
                            ["--spectrum", "--spectrum-output", "hex", "--hues", "5"],
                            title="gradient --spectrum --spectrum-output FORMAT"),
}


#: Named colors are drawn from the terminal theme's muted ANSI palette; the site's
#: screenshots use vivid hex values, so ``--colors``/``--bgcolors`` names are swapped
#: for these when generating (window titles keep the readable names).
VIVID = {
    "red": "#ff3b3b", "orange": "#ff9500", "yellow": "#ffd700", "gold": "#ffd700",
    "lime": "#7dff00", "green": "#22c55e", "cyan": "#22d3ee", "blue": "#3b82f6",
    "magenta": "#d946ef", "white": "#ffffff", "navy": "#1e3a8a", "purple": "#a855f7",
}


def vivid(argv: list[str]) -> list[str]:
    """Replace named colors that follow ``--colors``/``--bgcolors`` with vivid hex values."""
    out = list(argv)
    for i, arg in enumerate(out[:-1]):
        if arg in {"--colors", "--bgcolors"}:
            out[i + 1] = ",".join(VIVID.get(c.strip(), c.strip()) for c in out[i + 1].split(","))
    return out


def _env() -> dict[str, str]:
    """Environment for subprocesses: forced truecolor, fixed width, no user config."""
    env = {**os.environ, "FORCE_COLOR": "1", "COLUMNS": str(WIDTH), "COLORTERM": "truecolor"}
    for name in ("NO_COLOR", "AMPLITUDE_API_KEY", "GRADIENT_COLORS", "RICH_THEME"):
        env.pop(name, None)
    return env


def run(argv: list[str], stdin: str | None, *, columns: int = WIDTH) -> str:
    """Run ``gradient`` with ``argv`` and return its ANSI-coloured stdout."""
    env = _env()
    env["COLUMNS"] = str(columns)
    with tempfile.TemporaryDirectory() as config_home:
        env["XDG_CONFIG_HOME"] = config_home  # never read the user's real telemetry config
        result = _run_cli(vivid(argv), stdin, env)
    if result.returncode != 0:
        raise RuntimeError(f"{argv} failed ({result.returncode}): {result.stderr}")
    return result.stdout.rstrip("\n")


def _run_cli(argv: list[str], stdin: str | None, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    """Run the CLI module; ``argv`` comes only from the static example tables."""
    return subprocess.run(  # nosec B603 # nosemgrep
        [sys.executable, "-m", "rich_gradient_cli", *argv],
        input=stdin, capture_output=True, text=True, cwd=ROOT, env=env, check=False,
    )


def window_title(argv: list[str]) -> str:
    """Render ``argv`` as a shell-style ``gradient ...`` command, truncated to fit the window."""
    shown = ["gradient", *("-" if a == "-" else a for a in argv)]
    title = shlex.join(shown)
    return title if len(title) <= TITLE_MAX else title[: TITLE_MAX - 1] + "…"


def export(ansi: str, title: str, path: Path, *, width: int = WIDTH) -> None:
    """Write ``ansi`` to ``path`` as an SVG with the given window ``title``."""
    console = Console(record=True, width=width, file=open(os.devnull, "w"), force_terminal=True)
    console.print(Text.from_ansi(ansi), soft_wrap=True)
    console.save_svg(str(path), title=title, theme=GRADIENT_TERMINAL_THEME)


def render_example(example: Example) -> tuple[str, str]:
    """Run every command of ``example``; return ``(combined ANSI output, window title)``."""
    commands, title = example
    blocks = [run(argv, stdin) for argv, stdin in commands]
    return "\n\n".join(blocks) if len(blocks) > 1 else blocks[0], title or window_title(commands[0][0])


def main() -> None:
    """Generate every SVG."""
    COMMANDS_OUT.mkdir(parents=True, exist_ok=True)
    OPTIONS_OUT.mkdir(parents=True, exist_ok=True)
    export(run(["--help"], None, columns=HELP_WIDTH), "gradient --help", COMMANDS_OUT / "help.svg",
           width=HELP_WIDTH)
    print("wrote commands/help.svg")
    for name, example in MODES.items():
        ansi, title = render_example(example)
        export(ansi, title, COMMANDS_OUT / f"{name}-example.svg")
        print(f"wrote commands/{name}-example.svg")
    for name, example in OPTIONS.items():
        ansi, title = render_example(example)
        export(ansi, title, OPTIONS_OUT / f"{name}.svg")
        print(f"wrote options/{name}.svg")


if __name__ == "__main__":
    main()
