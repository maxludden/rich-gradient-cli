"""Tests for the opt-in telemetry module."""

import uuid
from pathlib import Path

import pytest
from typer.testing import CliRunner

from rich_gradient_cli import app, telemetry

runner = CliRunner()


@pytest.fixture(autouse=True)
def _isolated_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Point the config at a temp dir and clear the API key."""
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    monkeypatch.delenv(telemetry.API_KEY_ENV, raising=False)


def test_disabled_by_default() -> None:
    assert not telemetry.is_enabled()
    result = runner.invoke(app, ["telemetry", "status"])
    assert result.stdout.strip() == "disabled"


def test_enable_creates_stable_random_id_and_disable_removes_it() -> None:
    first = telemetry.enable()
    assert str(uuid.UUID(first)) == first
    assert telemetry.enable() == first
    assert telemetry.is_enabled()
    telemetry.disable()
    assert not telemetry.is_enabled()
    assert "install_id" not in telemetry._load()
    assert telemetry.enable() != first


def test_fresh_configs_get_different_ids(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ids = set()
    for name in ("a", "b"):
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / name))
        ids.add(telemetry.enable())
    assert len(ids) == 2


def test_track_swallows_config_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(telemetry.API_KEY_ENV, "key")
    monkeypatch.setattr(telemetry, "config_path", lambda: (_ for _ in ()).throw(RuntimeError))
    telemetry.track_command("print")  # must not raise


def test_track_is_noop_without_opt_in_or_key(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[object] = []
    monkeypatch.setattr("amplitude.Amplitude", lambda *a, **k: calls.append(a))
    monkeypatch.setenv(telemetry.API_KEY_ENV, "key")
    telemetry.track_command("print")  # key but no opt-in
    telemetry.enable()
    monkeypatch.delenv(telemetry.API_KEY_ENV)
    telemetry.track_command("print")  # opt-in but no key
    assert calls == []


def test_cli_commands_still_work_with_telemetry_off() -> None:
    result = runner.invoke(app, ["print", "hello"])
    assert result.exit_code == 0
    assert "hello" in result.stdout
