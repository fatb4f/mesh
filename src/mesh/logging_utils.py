"""Logging setup for mesh."""

from __future__ import annotations

import logging

from rich.logging import RichHandler


_LOGGING_READY = False


def setup_logging(level: int = logging.INFO) -> None:
    global _LOGGING_READY
    if _LOGGING_READY:
        return

    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, show_path=False)],
    )
    _LOGGING_READY = True
