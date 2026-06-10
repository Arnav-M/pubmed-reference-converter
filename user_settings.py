"""Persist GUI preferences across app sessions."""

from __future__ import annotations

import json
import os
from pathlib import Path

SETTINGS_VERSION = 1
_SETTINGS_DIR = Path(os.environ.get("APPDATA", Path.home())) / "PubMed Reference Converter"
_SETTINGS_FILE = _SETTINGS_DIR / "settings.json"


def settings_path() -> Path:
    return _SETTINGS_FILE


def load_settings() -> dict:
    if not _SETTINGS_FILE.is_file():
        return {}
    try:
        with _SETTINGS_FILE.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def save_settings(data: dict) -> None:
    _SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
    payload = {"version": SETTINGS_VERSION, **data}
    tmp = _SETTINGS_FILE.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    tmp.replace(_SETTINGS_FILE)
