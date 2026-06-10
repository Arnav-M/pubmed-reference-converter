"""Light modern styling for PubMed Converter."""

from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk


def apply_modern_theme(root: tk.Tk) -> dict[str, str]:
    colors = {
        "bg": "#f4f5f7",
        "card": "#ffffff",
        "text": "#111827",
        "muted": "#6b7280",
        "accent": "#0d9488",
        "accent_hover": "#0f766e",
        "accent_soft": "#ccfbf1",
        "border": "#e5e7eb",
        "log_bg": "#1e1e2e",
        "log_fg": "#cdd6f4",
        "browse_bg": "#e8eaed",
        "browse_hover": "#d8dce3",
        "browse_fg": "#4b5563",
        "add_files_bg": "#ccfbf1",
        "add_files_hover": "#99f6e4",
        "add_files_fg": "#0f766e",
        "add_files_border": "#0d9488",
        "grey_btn_bg": "#f3f4f6",
        "grey_btn_hover": "#e5e7eb",
        "grey_btn_border": "#d1d5db",
    }

    root.configure(bg=colors["bg"])
    root.option_add("*Font", ("Segoe UI", 10))

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(".", background=colors["bg"], foreground=colors["text"])
    style.configure("TFrame", background=colors["bg"])
    style.configure("Card.TFrame", background=colors["card"])
    style.configure("TLabel", background=colors["bg"], foreground=colors["text"])
    style.configure("Card.TLabel", background=colors["card"], foreground=colors["text"])
    style.configure("Muted.TLabel", background=colors["bg"], foreground=colors["muted"])
    style.configure("CardMuted.TLabel", background=colors["card"], foreground=colors["muted"])
    style.configure("Header.TLabel", background=colors["bg"], foreground=colors["text"], font=("Segoe UI Semibold", 20))
    style.configure("Subheader.TLabel", background=colors["bg"], foreground=colors["muted"], font=("Segoe UI", 10))
    style.configure("TEntry", fieldbackground="#f9fafb", padding=8)
    style.configure("TNotebook", background=colors["bg"], borderwidth=0)
    style.configure("TNotebook.Tab", padding=(14, 8), font=("Segoe UI", 10), background=colors["bg"])
    style.map("TNotebook.Tab", background=[("selected", colors["card"])], foreground=[("selected", colors["accent"])])
    style.configure("TCheckbutton", background=colors["card"])
    style.configure("Card.TCheckbutton", background=colors["card"])
    style.configure(
        "Accent.Horizontal.TProgressbar",
        troughcolor="#e5e7eb",
        background=colors["accent"],
        bordercolor=colors["border"],
        lightcolor=colors["accent_hover"],
        darkcolor=colors["accent"],
        thickness=10,
    )

    return colors


def make_accent_button(parent: tk.Misc, text: str, command, colors: dict[str, str]) -> tk.Button:
    btn = tk.Button(
        parent, text=text, command=command,
        bg=colors["accent"], fg="white",
        activebackground=colors["accent_hover"], activeforeground="white",
        relief=tk.FLAT, bd=0, padx=18, pady=9, cursor="hand2", font=("Segoe UI Semibold", 10),
    )

    def on_enter(_e) -> None:
        if str(btn["state"]) != tk.DISABLED:
            btn.configure(bg=colors["accent_hover"])

    def on_leave(_e) -> None:
        if str(btn["state"]) != tk.DISABLED:
            btn.configure(bg=colors["accent"])

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn


def make_add_files_button(parent: tk.Misc, text: str, command, colors: dict[str, str]) -> tk.Button:
    btn = tk.Button(
        parent, text=text, command=command,
        bg=colors["add_files_bg"], fg=colors["add_files_fg"],
        activebackground=colors["add_files_hover"], activeforeground=colors["add_files_fg"],
        relief=tk.FLAT, bd=0, padx=16, pady=8,
        highlightthickness=1,
        highlightbackground=colors["add_files_border"],
        highlightcolor=colors["add_files_border"],
        cursor="hand2", font=("Segoe UI Semibold", 10),
    )

    def on_enter(_e) -> None:
        btn.configure(bg=colors["add_files_hover"])

    def on_leave(_e) -> None:
        btn.configure(bg=colors["add_files_bg"])

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn


def make_grey_button(parent: tk.Misc, text: str, command, colors: dict[str, str]) -> tk.Button:
    btn = tk.Button(
        parent, text=text, command=command,
        bg=colors["grey_btn_bg"], fg=colors["text"],
        activebackground=colors["grey_btn_hover"], activeforeground=colors["text"],
        relief=tk.FLAT, bd=0, padx=14, pady=8,
        highlightthickness=1,
        highlightbackground=colors["grey_btn_border"],
        highlightcolor=colors["grey_btn_border"],
        cursor="hand2", font=("Segoe UI", 10),
    )

    def on_enter(_e) -> None:
        btn.configure(bg=colors["grey_btn_hover"])

    def on_leave(_e) -> None:
        btn.configure(bg=colors["grey_btn_bg"])

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn


def make_browse_button(parent: tk.Misc, text: str, command, colors: dict[str, str]) -> tk.Button:
    btn = tk.Button(
        parent, text=text, command=command,
        bg=colors["browse_bg"], fg=colors["browse_fg"],
        activebackground=colors["browse_hover"], activeforeground=colors["text"],
        relief=tk.FLAT, bd=0, padx=14, pady=8,
        highlightthickness=0,
        cursor="hand2", font=("Segoe UI", 10),
    )

    def on_enter(_e) -> None:
        btn.configure(bg=colors["browse_hover"])

    def on_leave(_e) -> None:
        btn.configure(bg=colors["browse_bg"])

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn


def make_secondary_button(parent: tk.Misc, text: str, command, colors: dict[str, str]) -> tk.Button:
    return tk.Button(
        parent, text=text, command=command,
        bg=colors["card"], fg=colors["text"],
        activebackground=colors["accent_soft"], activeforeground=colors["accent"],
        relief=tk.FLAT, bd=0, padx=14, pady=8,
        highlightthickness=1, highlightbackground=colors["border"], highlightcolor=colors["border"],
        cursor="hand2", font=("Segoe UI", 10),
    )


def make_ghost_button(parent: tk.Misc, text: str, command, colors: dict[str, str]) -> tk.Button:
    return tk.Button(
        parent, text=text, command=command,
        bg=colors["bg"], fg=colors["muted"],
        activebackground=colors["card"], activeforeground=colors["text"],
        relief=tk.FLAT, bd=0, padx=12, pady=8, cursor="hand2", font=("Segoe UI", 10),
    )


def configure_log_widget(widget: tk.Text, colors: dict[str, str]) -> None:
    widget.configure(
        bg=colors["log_bg"], fg=colors["log_fg"], insertbackground=colors["log_fg"],
        relief=tk.FLAT, bd=0, padx=12, pady=10,
        font=tkfont.Font(family="Consolas", size=10), selectbackground=colors["accent"],
    )


def set_window_icon(root: tk.Tk, assets_dir) -> None:
    from pathlib import Path

    icon = Path(assets_dir) / "icon.ico"
    if not icon.is_file():
        return
    try:
        root.iconbitmap(default=str(icon))
    except tk.TclError:
        pass


_DISABLED_BG = "#e5e7eb"
_DISABLED_FG = "#9ca3af"


def set_accent_button_state(btn: tk.Button, colors: dict[str, str], *, enabled: bool) -> None:
    if enabled:
        btn.configure(state=tk.NORMAL, bg=colors["accent"], fg="white", cursor="hand2")
    else:
        btn.configure(state=tk.DISABLED, bg=_DISABLED_BG, fg=_DISABLED_FG, cursor="arrow")


def set_button_enabled(
    btn: tk.Button,
    colors: dict[str, str],
    *,
    enabled: bool,
    kind: str,
) -> None:
    if kind == "accent":
        set_accent_button_state(btn, colors, enabled=enabled)
        return

    styles = {
        "add_files": (colors["add_files_bg"], colors["add_files_fg"], colors["add_files_border"]),
        "grey": (colors["grey_btn_bg"], colors["text"], colors["grey_btn_border"]),
        "browse": (colors["browse_bg"], colors["browse_fg"], colors["border"]),
        "secondary": (colors["card"], colors["text"], colors["border"]),
        "ghost": (colors["bg"], colors["muted"], colors["border"]),
    }
    if enabled:
        bg, fg, border = styles[kind]
        btn.configure(
            state=tk.NORMAL, bg=bg, fg=fg, cursor="hand2",
            highlightthickness=1 if kind != "browse" else 0,
            highlightbackground=border, highlightcolor=border,
        )
    else:
        btn.configure(
            state=tk.DISABLED, bg=_DISABLED_BG, fg=_DISABLED_FG, cursor="arrow",
            highlightthickness=1, highlightbackground=_DISABLED_BG, highlightcolor=_DISABLED_BG,
        )
