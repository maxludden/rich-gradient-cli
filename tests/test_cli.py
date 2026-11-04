"""End-to-end tests for the ``gradient`` command."""

import json
from pathlib import Path

import click
import pytest
from typer.main import get_command
from typer.testing import CliRunner

from rich_gradient_cli import VERSION, app

runner = CliRunner()


def run(*args: str, input: str | None = None):  # noqa: A002
    return runner.invoke(app, list(args), input=input)


def test_version() -> None:
    result = run("--version")
    assert result.exit_code == 0 and VERSION in result.output


def test_no_duplicate_option_strings() -> None:
    """Every option string is declared exactly once."""
    command = get_command(app)
    seen: list[str] = []
    for param in command.params:
        if isinstance(param, click.Option):
            seen.extend(param.opts + param.secondary_opts)
    assert len(seen) == len(set(seen))
    assert command.context_settings["help_option_names"] == ["--help"]
    assert {"-h", "-t", "-p", "-u", "-a", "-d", "-S", "-v"} <= set(seen)


def test_text() -> None:
    result = run("Hello [b]world[/b]", "--colors", "red,blue")
    assert result.exit_code == 0 and "Hello world" in result.output


def test_no_markup() -> None:
    result = run("[b]x[/b]", "--no-markup")
    assert "[b]x[/b]" in result.output


def test_bad_markup_exit_code() -> None:
    result = run("[/nope]")
    assert result.exit_code == 1


def test_markdown_panel_stdin() -> None:
    result = run("-", "--markdown", "--panel", "rounded", "--title", "T", input="# Head\n")
    assert result.exit_code == 0 and "Head" in result.output and "╭" in result.output


def test_rule() -> None:
    result = run("--rule", "Title", "--colors", "cyan,magenta")
    assert result.exit_code == 0 and "Title" in result.output


def test_json_and_invalid_json() -> None:
    assert "alpha" in run("-", "--json", input='{"alpha": 1}').output
    assert run("-", "--json", input="{").exit_code == 1


def test_csv_escapes_markup() -> None:
    result = run("-", "--csv", input="a,b\n1,[bold]x\n")
    assert result.exit_code == 0 and "[bold]x" in result.output


def test_csv_empty() -> None:
    assert run("-", "--csv", input="").exit_code == 1


def test_syntax_file(tmp_path: Path) -> None:
    path = tmp_path / "a.py"
    path.write_text("print('hi')\nx = 1\n", encoding="utf-8")
    result = run(str(path), "-n", "-h", "1")
    assert result.exit_code == 0 and "print" in result.output and "x = 1" not in result.output


def test_tree_directory(tmp_path: Path) -> None:
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "f.txt").write_text("x", encoding="utf-8")
    result = run("--tree", str(tmp_path))
    assert result.exit_code == 0 and "sub/" in result.output and "f.txt" in result.output


def test_columns() -> None:
    result = run("-", "--columns", input="one\ntwo\nthree\n")
    assert result.exit_code == 0 and "three" in result.output


def test_spectrum_outputs() -> None:
    result = run("--spectrum", "--spectrum-output", "hex")
    assert result.exit_code == 0 and "#" in result.output


def test_exports(tmp_path: Path) -> None:
    svg, html = tmp_path / "o.svg", tmp_path / "o.html"
    result = run("hi", "--export-svg", str(svg), "--export-html", str(html))
    assert result.exit_code == 0
    assert svg.read_text().startswith("<svg") and "<html" in html.read_text().lower()


@pytest.mark.parametrize(
    "args",
    [
        ["x", "--markdown", "--json"],
        ["x", "--animate", "--export-svg", "o.svg"],
        ["x", "-h", "1", "-t", "1"],
        ["x", "-l", "-r"],
        ["x", "-L", "-R"],
        ["x", "--padding", "1,2,3"],
        ["x", "--highlight-word", "bad"],
        ["x", "--style", "not-a-style-$$"],
    ],
)
def test_usage_errors_exit_2(args: list[str]) -> None:
    assert run(*args).exit_code == 2


def test_missing_file_is_literal_and_directory_errors(tmp_path: Path) -> None:
    assert run(str(tmp_path)).exit_code == 1


def test_animate_falls_back_when_not_a_terminal() -> None:
    result = run("hi", "--animate", "--duration", "1")
    assert result.exit_code == 0 and "hi" in result.output


def test_panel_none_means_no_panel() -> None:
    result = run("hi", "--panel", "none")
    assert result.exit_code == 0 and "╭" not in result.output


def test_print_flag_forces_markup_text(tmp_path: Path) -> None:
    path = tmp_path / "a.py"
    path.write_text("[b]x[/b]\n", encoding="utf-8")
    result = run(str(path), "--print")
    assert result.exit_code == 0 and "x" in result.output and "[b]" not in result.output


def test_rst_auto_detected(tmp_path: Path) -> None:
    path = tmp_path / "doc.rst"
    path.write_text("Title\n=====\n\nSome *emphasis* text.\n", encoding="utf-8")
    result = run(str(path))
    assert result.exit_code == 0 and "Title" in result.output and "emphasis" in result.output


def test_rst_flag_from_stdin() -> None:
    assert "Heading" in run("-", "--rst", input="Heading\n=======\n").output


def test_ipynb_auto_detected(tmp_path: Path) -> None:
    notebook = {
        "metadata": {"kernelspec": {"language": "python"}},
        "cells": [
            {"cell_type": "markdown", "source": ["# Heading"]},
            {
                "cell_type": "code",
                "execution_count": 1,
                "source": ["print('hi')"],
                "outputs": [{"output_type": "stream", "name": "stdout", "text": ["hi\n"]}],
            },
        ],
    }
    path = tmp_path / "nb.ipynb"
    path.write_text(json.dumps(notebook), encoding="utf-8")
    result = run(str(path))
    assert result.exit_code == 0
    assert "Heading" in result.output and "print" in result.output


def test_ipynb_invalid_notebook(tmp_path: Path) -> None:
    path = tmp_path / "bad.ipynb"
    path.write_text("not json", encoding="utf-8")
    assert run(str(path)).exit_code == 1


def test_inspect_dotted_path_and_expression() -> None:
    assert "Console" in run("rich.console.Console", "--inspect").output
    assert "list" in run("[1, 2, 3]", "--inspect").output


def test_inspect_bad_expression() -> None:
    assert run("no_such_thing_xyz", "--inspect").exit_code == 1


def test_max_width_and_width_accepted() -> None:
    assert run("hello world", "-W", "20").exit_code == 0
    assert run("hello world", "-w", "20").exit_code == 0
