import json
from importlib.metadata import version

from rich.text import Text
from typer.testing import CliRunner

from rich_gradient_cli import app


runner = CliRunner()


def test_version_flag_exits_successfully() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert f"gradient version {version('rich-gradient-cli')}" in result.stdout


def test_view_auto_detects_markdown_file(tmp_path) -> None:
    markdown_path = tmp_path / "README.md"
    markdown_path.write_text("# Title\n\nBody", encoding="utf-8")

    result = runner.invoke(app, ["view", str(markdown_path), "--force-terminal"])

    assert result.exit_code == 0
    assert "Title" in result.stdout
    assert "Body" in result.stdout


def test_view_renders_json_file(tmp_path) -> None:
    json_path = tmp_path / "data.json"
    json_path.write_text('{"name": "Ada", "count": 3}', encoding="utf-8")

    result = runner.invoke(app, ["view", str(json_path), "--force-terminal"])

    assert result.exit_code == 0
    assert '"name"' in result.stdout
    assert '"Ada"' in result.stdout


def test_view_exports_html(tmp_path) -> None:
    text_path = tmp_path / "example.py"
    html_path = tmp_path / "example.html"
    text_path.write_text("print('hello')\n", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "view",
            str(text_path),
            "--lexer",
            "python",
            "--export-html",
            str(html_path),
        ],
    )

    assert result.exit_code == 0
    assert html_path.exists()
    assert "print" in html_path.read_text(encoding="utf-8")


def test_view_reads_markdown_from_stdin() -> None:
    result = runner.invoke(
        app,
        ["view", "-", "--markdown", "--force-terminal"],
        input="# From stdin\n",
    )

    assert result.exit_code == 0
    assert "From stdin" in result.stdout


def test_view_print_treats_resource_as_markup_text() -> None:
    result = runner.invoke(
        app,
        ["view", "Hello, [bold]World[/]!", "--print", "--force-terminal"],
    )

    assert result.exit_code == 0
    assert "Hello, World!" in Text.from_ansi(result.stdout).plain


def test_gradient_command_renders_text() -> None:
    result = runner.invoke(
        app,
        ["gradient", "Hello gradient", "--colors", "red,blue", "--no-expand"],
    )

    assert result.exit_code == 0
    assert "Hello gradient" in result.stdout


def test_spectrum_command_outputs_hex_values() -> None:
    result = runner.invoke(
        app,
        ["spectrum", "--hues", "3", "--seed", "1", "--output", "hex"],
    )

    assert result.exit_code == 0
    assert result.stdout.count("#") == 3


def test_print_command_can_disable_markup() -> None:
    result = runner.invoke(app, ["print", "[bold]literal[/]", "--no-markup"])

    assert result.exit_code == 0
    assert "[bold]literal[/]" in result.stdout


def test_rule_command_accepts_custom_characters() -> None:
    result = runner.invoke(
        app,
        ["rule", "--title", "Title", "--characters", "=", "--colors", "red,blue"],
    )

    assert result.exit_code == 0
    assert "Title" in result.stdout


def test_columns_command_renders_items() -> None:
    result = runner.invoke(
        app,
        ["columns", "alpha", "beta", "gamma", "--colors", "red,blue"],
    )

    assert result.exit_code == 0
    assert "alpha" in result.stdout
    assert "beta" in result.stdout


def test_tree_command_renders_branches() -> None:
    result = runner.invoke(
        app,
        ["tree", "root", "src/app.py", "docs/index.md", "--colors", "red,blue"],
    )

    assert result.exit_code == 0
    assert "root" in result.stdout
    assert "src" in result.stdout
    assert "docs" in result.stdout


def test_syntax_command_renders_file(tmp_path) -> None:
    code_path = tmp_path / "example.py"
    code_path.write_text("print('hello')\n", encoding="utf-8")

    result = runner.invoke(
        app,
        ["syntax", str(code_path), "--lexer", "python", "--line-numbers"],
    )

    assert result.exit_code == 0
    assert "print" in result.stdout
    assert "hello" in result.stdout


def test_table_command_renders_csv_from_stdin() -> None:
    result = runner.invoke(
        app,
        ["table", "-", "--colors", "red,blue"],
        input="name,count\nAda,3\nGrace,5\n",
    )

    assert result.exit_code == 0
    assert "name" in result.stdout
    assert "Ada" in result.stdout


def test_view_auto_detects_rst_file(tmp_path) -> None:
    rst_path = tmp_path / "doc.rst"
    rst_path.write_text("Title\n=====\n\nSome *emphasis* text.\n", encoding="utf-8")
    result = runner.invoke(app, ["view", str(rst_path), "--force-terminal"])
    assert result.exit_code == 0
    assert "Title" in result.output
    assert "emphasis" in result.output


def test_view_renders_ipynb_file(tmp_path) -> None:
    notebook = {
        "metadata": {"kernelspec": {"language": "python"}},
        "cells": [
            {"cell_type": "markdown", "source": ["# Heading"]},
            {
                "cell_type": "code",
                "execution_count": 1,
                "source": ["print('hi')"],
                "outputs": [
                    {"output_type": "stream", "name": "stdout", "text": ["hi\n"]}
                ],
            },
        ],
    }
    path = tmp_path / "nb.ipynb"
    path.write_text(json.dumps(notebook), encoding="utf-8")
    result = runner.invoke(app, ["view", str(path), "--force-terminal"])
    assert result.exit_code == 0
    assert "Heading" in result.output
    assert "print" in result.output
    assert "hi" in result.output


def test_view_ipynb_rejects_invalid_notebook(tmp_path) -> None:
    path = tmp_path / "bad.ipynb"
    path.write_text("not json", encoding="utf-8")
    result = runner.invoke(app, ["view", str(path)])
    assert result.exit_code != 0


def test_view_inspect_dotted_path() -> None:
    result = runner.invoke(app, ["view", "rich.console.Console", "--inspect"])
    assert result.exit_code == 0
    assert "Console" in result.output


def test_view_inspect_expression() -> None:
    result = runner.invoke(app, ["view", "[1, 2, 3]", "--inspect"])
    assert result.exit_code == 0
    assert "list" in result.output


def test_view_inspect_bad_expression() -> None:
    result = runner.invoke(app, ["view", "no_such_thing_xyz", "--inspect"])
    assert result.exit_code != 0
