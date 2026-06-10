"""Windows drag-and-drop onto Tkinter (Python 3.13-safe)."""

from __future__ import annotations

import queue
import sys
import tkinter as tk
from collections.abc import Callable
from pathlib import Path

_drop_queue: queue.Queue[list[str]] = queue.Queue()
_root_hooked = False


def _decode_drop_item(item: object) -> str:
    if isinstance(item, bytes):
        for encoding in ("utf-8", "gbk"):
            try:
                return item.decode(encoding).strip().strip('"')
            except UnicodeDecodeError:
                continue
        return item.decode("utf-8", errors="replace").strip().strip('"')
    return str(item).strip().strip('"')


def _windnd_enqueue(items) -> None:
    """Called from windnd's WndProc hook — queue only, no tkinter calls."""
    paths: list[str] = []
    for item in items:
        text = _decode_drop_item(item)
        if text:
            paths.append(str(Path(text)))
    if paths:
        _drop_queue.put(paths)


def install_root_drop_target(root: tk.Misc) -> bool:
    """Hook file drops once on the root window. Returns True if drag-and-drop is active."""
    global _root_hooked
    if sys.platform != "win32":
        return False
    if _root_hooked:
        return True
    try:
        import windnd
    except ImportError:
        return False

    windnd.hook_dropfiles(root, func=_windnd_enqueue)
    _root_hooked = True
    return True


def start_drop_polling(root: tk.Misc, on_files: Callable[[list[str]], None]) -> None:
    """Drain the drop queue on the Tk main thread."""

    def _poll() -> None:
        try:
            while True:
                paths = _drop_queue.get_nowait()
                if root.winfo_exists():
                    on_files(paths)
        except queue.Empty:
            pass
        except tk.TclError:
            return
        if root.winfo_exists():
            root.after(50, _poll)

    root.after(50, _poll)
