"""Dependency-free command selection for the desktop control panel."""

from __future__ import annotations

import shlex


def analysis_action(raw_arguments: str) -> tuple[str, tuple[str, ...]]:
    """Select the bundled demo or preserve an operator's CLI arguments."""
    parsed = tuple(shlex.split(raw_arguments))
    if parsed:
        return "cli.sh", parsed
    return "demo.sh", ()
