"""Opt-in, anonymous usage telemetry for the ``gradient`` CLI.

Nothing is sent unless the user runs ``gradient telemetry enable`` *and* an
``AMPLITUDE_API_KEY`` is present in the environment. The only data sent is the
event name ``Command Run``, the render mode, and a random install ID that
is generated locally on enable and never derived from the machine or user.
"""

from __future__ import annotations

import json
import os
import tempfile
import uuid
from pathlib import Path
from typing import Any

EVENT_NAME = "Command Run"
API_KEY_ENV = "AMPLITUDE_API_KEY"
REGION_ENV = "AMPLITUDE_SERVER_ZONE"
FLUSH_TIMEOUT_SECONDS = 5.0


def config_path() -> Path:
    """Return the path of the telemetry config file (honors ``XDG_CONFIG_HOME``)."""
    base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / "rich-gradient-cli" / "telemetry.json"


def _load() -> dict[str, Any]:
    """Read the config file, returning an empty dict if missing or invalid."""
    try:
        data = json.loads(config_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _save(data: dict[str, Any]) -> None:
    """Atomically write the config file, creating its directory if needed."""
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle)
        os.replace(tmp_name, path)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise


def is_enabled() -> bool:
    """Return True if the user has opted in to telemetry."""
    return bool(_load().get("enabled")) and bool(_load().get("install_id"))


def enable() -> str:
    """Opt in, generating a random install ID on first use; return the ID."""
    data = _load()
    install_id = str(data.get("install_id") or uuid.uuid4())
    _save({"enabled": True, "install_id": install_id})
    return install_id


def disable() -> None:
    """Opt out and discard the stored install ID."""
    _save({"enabled": False})


def track_command(command: str) -> None:
    """Send a ``Command Run`` event if opted in and a key is configured.

    The process is short-lived, so the event is flushed and awaited before
    returning. Telemetry must never break the CLI: all failures are swallowed.
    """
    try:
        api_key = os.environ.get(API_KEY_ENV)
        config = _load()
        if not api_key or not (config.get("enabled") and config.get("install_id")):
            return
        from amplitude import Amplitude, BaseEvent

        client = Amplitude(api_key)
        client.configuration.server_zone = os.environ.get(REGION_ENV, "US")
        client.track(
            BaseEvent(
                event_type=EVENT_NAME,
                user_id=str(config["install_id"]),
                event_properties={"command": command},
            )
        )
        for future in client.flush() or []:
            if future is not None:
                future.result(timeout=FLUSH_TIMEOUT_SECONDS)
        client.shutdown()
    except Exception:  # noqa: BLE001 - telemetry must never affect the CLI
        return


def run_telemetry_action(action: str) -> str:
    """Apply ``enable``, ``disable`` or ``status`` and return the message to show."""
    if action == "enable":
        enable()
        return "Telemetry enabled. Only the render mode is sent, with a random ID."
    if action == "disable":
        disable()
        return "Telemetry disabled."
    if action == "status":
        return "enabled" if is_enabled() else "disabled"
    raise ValueError(f"Unknown telemetry action {action!r}.")
