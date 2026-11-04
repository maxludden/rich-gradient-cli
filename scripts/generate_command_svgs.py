"""Generate example and ``--help`` SVG screenshots for every ``gradient`` command.

Each command is run as a subprocess with forced colour output; the ANSI result
is replayed into a recording Rich console and exported to ``docs/img/commands``.

Usage: ``uv run python scripts/generate_command_svgs.py``
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

from rich.console import Console
from rich.terminal_theme import MONOKAI
from rich.text import Text

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "img" / "commands"
WIDTH = 100

CSV = "name,language,stars\nrich,python,50000\ntyper,python,15000\nuv,rust,40000\n"

# name -> (argv after ``gradient``, optional stdin)
EXAMPLES: dict[str, tuple[list[str], str | None]] = {
    "print": (["print", "--colors", "red,#ff9900,#ffff00", "Hello gradient"], None),
    "gradient": (
        ["gradient", "--colors", "magenta,cyan", "--highlight-word",
         "error=bold white on red", "Highlight error text"],
        None,
    ),
    "columns": (["columns", "alpha", "beta", "gamma", "delta", "epsilon", "--colors", "red,blue"], None),
    "panel": (
        ["panel", "--colors", "red,#ff9999", "-t", "Error", "--title-style",
         "bold #ffffff", "--title-align", "left",
         "This is an error message with a red to pink gradient background."],
        None,
    ),
    "rule": (["rule", "--colors", "blue,#00ff00,cyan", "--title", "Blue to Green to Cyan Rule"], None),
    "markdown": (["markdown", "-", "--colors", "magenta,cyan"], "# Hello\n\nSome **bold** and *italic* text.\n\n- one\n- two\n"),
    "spectrum": (["spectrum", "--hues", "7", "--seed", "42"], None),
    "syntax": (["syntax", "pyproject.toml", "--lexer", "toml",
                "--line-numbers", "--colors", "yellow,magenta"], None),
    "table": (["table", "-", "--colors", "cyan,magenta"], CSV),
    "tree": (["tree", "project", "src/app.py", "docs/index.md", "--colors", "lime,cyan"], None),
    "telemetry": (["telemetry", "status"], None),
    "view": (["view", "sample.md", "--head", "12"], None),
}


def run(argv: list[str], stdin: str | None) -> str:
    """Run ``gradient`` with ``argv`` and return its ANSI-coloured stdout."""
    env = {**os.environ, "FORCE_COLOR": "1", "COLUMNS": str(WIDTH), "COLORTERM": "truecolor"}
    for name in ("NO_COLOR", "AMPLITUDE_API_KEY"):
        env.pop(name, None)
    with tempfile.TemporaryDirectory() as config_home:
        env["XDG_CONFIG_HOME"] = config_home  # never read the user's real telemetry config
        result = _run_cli(argv, stdin, env)
    if result.returncode != 0:
        raise RuntimeError(f"{argv} failed ({result.returncode}): {result.stderr}")
    return result.stdout.rstrip("\n")


def _run_cli(argv: list[str], stdin: str | None, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    """Run the CLI module; ``argv`` comes only from the static ``EXAMPLES`` table."""
    return subprocess.run(  # nosec B603 # nosemgrep
        [sys.executable, "-m", "rich_gradient_cli", *argv],
        input=stdin, capture_output=True, text=True, cwd=ROOT, env=env, check=False,
    )


def export(ansi: str, title: str, path: Path) -> None:
    """Write ``ansi`` to ``path`` as an SVG with the given window ``title``."""
    console = Console(record=True, width=WIDTH, file=open(os.devnull, "w"), force_terminal=True)
    console.print(Text.from_ansi(ansi), soft_wrap=True)
    console.save_svg(str(path), title=title, theme=MONOKAI)


def main() -> None:
    """Generate every SVG."""
    OUT.mkdir(parents=True, exist_ok=True)
    jobs: dict[str, tuple[list[str], str | None]] = {"root-help": (["--help"], None)}
    for name, (argv, stdin) in EXAMPLES.items():
        jobs[f"{name}-example"] = (argv, stdin)
        jobs[f"{name}-help"] = ([argv[0], "--help"], None)
    for stem, (argv, stdin) in jobs.items():
        export(run(argv, stdin), "gradient " + " ".join(argv[:1]), OUT / f"{stem}.svg")
        print(f"wrote {stem}.svg")


if __name__ == "__main__":
    main()
