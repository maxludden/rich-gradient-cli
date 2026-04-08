from typer.testing import CliRunner

from rich_gradient_cli import app


runner = CliRunner()


def test_version_flag_exits_successfully() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "gradient version" in result.stdout

