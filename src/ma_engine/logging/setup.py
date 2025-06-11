"""Logging config for the engine."""
from __future__ import annotations

import logging
import sys


def configure(level: str = "INFO") -> None:
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=fmt,
        stream=sys.stdout,
    )

