"""Typer library stub file."""

from __future__ import annotations

from typing import Any, Callable, TextIO, TypeVar

_T = TypeVar("_T", bound=Callable[..., Any])

class Context:
    """Typer context object passed to callbacks and commands."""

    invoked_subcommand: str | None
    args: list[str]

    def get_help(self) -> str: ...


class Exit(Exception):
    """Signal an early, successful CLI exit."""

    ...


class BadParameter(Exception):
    """Raised when a parameter value is invalid."""

    ...


class UsageError(Exception):
    """Raised for invalid command usage."""

    ...

class Typer:
    """Application object used to register CLI callbacks and commands."""

    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...
    def callback(self, *args: Any, **kwargs: Any) -> Callable[[_T], _T]: ...
    def command(self, *args: Any, **kwargs: Any) -> Callable[[_T], _T]: ...


def Argument(default: Any = ..., *param_decls: str, **kwargs: Any) -> Any: ...
def Option(default: Any = ..., *param_decls: str, **kwargs: Any) -> Any: ...
def get_text_stream(name: str, encoding: str | None = ..., errors: str | None = ...) -> TextIO: ...

def echo(message: Any = ..., **kwargs: Any) -> None: ...
