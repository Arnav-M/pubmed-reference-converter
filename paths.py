"""Resolve bundled files for dev runs and PyInstaller builds."""

from __future__ import annotations

import sys
from pathlib import Path


def app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def asset_path(name: str) -> Path:
    return app_root() / "assets" / name
