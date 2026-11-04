"""rich-gradient-cli: render text, files, URLs, and stdin with rich-gradient.

The package exposes a single Typer application, :data:`app`, installed as the
``gradient`` console script.
"""

import sys

from . import cli
from .cli import VERSION, app
from .telemetry import track_command


def entrypoint() -> None:
    """Console-script entry point for ``gradient``.

    Runs the app, then sends the opt-in telemetry event only when the command
    completed successfully (not for ``--help``, ``--telemetry`` or usage errors).
    """
    try:
        app()
    except SystemExit as exc:
        if exc.code in (0, None):
            _track_success()
        raise
    _track_success()


def _track_success() -> None:
    """Send the render-mode telemetry event for a command that completed normally."""
    if cli.invoked_mode and "--help" not in sys.argv[1:]:
        track_command(cli.invoked_mode)


__version__ = VERSION
__all__ = ["VERSION", "app", "entrypoint"]
