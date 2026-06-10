"""Desktop GUI for PubMed Reference Converter."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from collections.abc import Callable
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

from dnd import install_root_drop_target, start_drop_polling
from excel_export import DEFAULT_CSV_NAME, csv_to_formatted_xlsx
from export_enrich import enrich_csv_citations
from prisma_report import parse_merge_ok_line, parse_ps_ok_line, write_prisma_summary
from gui_theme import (
    apply_modern_theme,
    configure_log_widget,
    make_accent_button,
    make_add_files_button,
    make_browse_button,
    make_ghost_button,
    make_grey_button,
    make_secondary_button,
    set_button_enabled,
    set_window_icon,
)
from paths import app_root
from user_settings import load_settings, save_settings

ROOT = app_root()
APP_TITLE = "PubMed Reference Converter"
APP_VERSION = "1.1.0"
CANONICAL_RIS = "references.ris"
WORK_SUBDIR = ".pubmed-work"

PS_OPTIONAL_COLUMNS = frozenset({
    "Include?", "ExcludeReason", "Notes", "HasAbstract", "RecordType",
})
PYTHON_OPTIONAL_COLUMNS = frozenset({"CitationVancouver", "CitationAMA"})

OPTIONAL_CSV_COLUMNS: list[tuple[str, str, str]] = [
    ("col_include", "Include?", "Empty column for screening (Y / N / Maybe)"),
    ("col_exclude_reason", "ExcludeReason", "Why a record was excluded"),
    ("col_notes", "Notes", "Free-text reviewer notes"),
    ("col_has_abstract", "HasAbstract", "Yes/No — quick filter for records with an abstract"),
    ("col_record_type", "RecordType", "Publication types from PubMed (e.g. Journal Article, RCT)"),
    ("col_citation_vancouver", "CitationVancouver", "Vancouver-style reference string for manuscripts"),
    ("col_citation_ama", "CitationAMA", "AMA-style reference string for manuscripts"),
]


_PS_ERRORS: dict[str, dict[int, str]] = {
    "process_ris_files.ps1": {
        1: "No .ris files found in the working folder.\n\nConvert NBIB files first, or choose a folder that contains .ris files.",
        2: "No exportable entries found.\n\nYour .ris files need at least a title (TI) on each record.",
    },
    "extract_urls_with_titles.ps1": {
        1: "No .ris files found in the working folder.\n\nAdd URL-enriched .ris files first, or change the working folder.",
        2: "No URLs found in your .ris files.\n\nRun “Add links” on tab 2 before fetching web titles.",
    },
}


def run_powershell(
    script: str,
    args: list[str],
    cwd: Path,
    log: Callable[[str], None],
    *,
    quiet: bool = False,
) -> tuple[int, str]:
    cmd = [
        "powershell", "-NoProfile", "-ExecutionPolicy", "RemoteSigned",
        "-File", str(ROOT / script), *args,
    ]
    if not quiet:
        log(f"$ {script} {' '.join(args)}".strip())
    result = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    output = (result.stdout or "") + (result.stderr or "")
    if not quiet:
        if result.stdout:
            log(result.stdout.rstrip())
        if result.stderr:
            log(result.stderr.rstrip())
    return result.returncode, output


class PubmedConverterApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{APP_TITLE} {APP_VERSION}")
        self.geometry("780x740")
        self.minsize(700, 620)
        self._busy = False
        self._lockable_widgets: list[tuple[tk.Misc, str]] = []
        self._nbib_batch: list[str] = []
        self._ris_batch: list[str] = []
        self.colors = apply_modern_theme(self)
        set_window_icon(self, ROOT / "assets")

        self.work_dir = tk.StringVar(value=str(Path.home() / "Documents"))
        self.status_var = tk.StringVar(value="Ready")
        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_label_var = tk.StringVar(value="")
        self._progress_visible = False
        self._last_save_folder: Path | None = None
        self._optional_column_vars: dict[str, tk.BooleanVar] = {
            attr: tk.BooleanVar(value=False) for attr, _, _ in OPTIONAL_CSV_COLUMNS
        }
        self._last_merge_stats: dict[str, int] | None = None
        self._settings_save_pending = False

        self._load_user_settings()
        self._build_ui()
        self._bind_settings_autosave()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        outer = ttk.Frame(self, padding=20)
        outer.pack(fill=tk.BOTH, expand=True)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(2, weight=3)
        outer.rowconfigure(5, weight=2)

        header = ttk.Frame(outer)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        ttk.Label(header, text=APP_TITLE, style="Header.TLabel").pack(anchor="w")

        folder_card = tk.Frame(outer, bg=self.colors["card"], highlightthickness=1, highlightbackground=self.colors["border"])
        folder_card.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        folder_body = ttk.Frame(folder_card, style="Card.TFrame", padding=14)
        folder_body.pack(fill=tk.X)
        ttk.Label(folder_body, text="Working folder", style="Card.TLabel").pack(side=tk.LEFT)
        self.work_dir_entry = ttk.Entry(folder_body, textvariable=self.work_dir)
        self.work_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(12, 12))
        self._register_lockable(self.work_dir_entry, "entry")
        browse_btn = make_browse_button(folder_body, "Browse", self._browse_work_dir, self.colors)
        browse_btn.pack(side=tk.LEFT)
        self._register_lockable(browse_btn, "browse")
        make_secondary_button(folder_body, "Open folder", self._open_work_dir, self.colors).pack(side=tk.LEFT, padx=(8, 0))

        main_card = tk.Frame(outer, bg=self.colors["card"], highlightthickness=1, highlightbackground=self.colors["border"])
        main_card.grid(row=2, column=0, sticky="nsew")
        main_body = ttk.Frame(main_card, style="Card.TFrame", padding=14)
        main_body.pack(fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(main_body)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.nbib_listbox = self._add_queue_tab(
            self.notebook, "1 · NBIB → RIS", ".nbib", self._nbib_batch,
            self._add_nbib_files, self._remove_nbib_files, self._clear_nbib_files,
            self._convert_nbib, "Convert all",
        )
        self.ris_listbox = self._add_queue_tab(
            self.notebook, "2 · Add links", ".ris", self._ris_batch,
            self._add_ris_files, self._remove_ris_files, self._clear_ris_files,
            self._add_urls, "Add links to all",
        )
        self._add_action_tab(self.notebook, "3 · Full CSV", self._export_csv, "Export full CSV")
        self._add_action_tab(self.notebook, "4 · Web titles", self._fetch_titles, "Fetch titles")
        self._add_properties_tab(self.notebook)

        if install_root_drop_target(self):
            start_drop_polling(self, self._route_file_drop)

        pipeline_row = ttk.Frame(main_body, style="Card.TFrame")
        pipeline_row.pack(fill=tk.X, pady=(14, 0))
        self.pipeline_btn = make_accent_button(pipeline_row, "Run batch pipeline", self._run_pipeline, self.colors)
        self.pipeline_btn.pack(side=tk.LEFT)
        self._register_lockable(self.pipeline_btn, "accent")
        make_secondary_button(pipeline_row, "Open output folder", self._open_save_folder, self.colors).pack(side=tk.LEFT, padx=(10, 0))

        self.progress_wrap = ttk.Frame(outer)
        self.progress_label = ttk.Label(
            self.progress_wrap, textvariable=self.progress_label_var, style="Muted.TLabel",
        )
        self.progress_label.pack(anchor="w")
        self.progress = ttk.Progressbar(
            self.progress_wrap, variable=self.progress_var, maximum=100,
            style="Accent.Horizontal.TProgressbar", mode="determinate",
        )
        self.progress.pack(fill=tk.X, pady=(4, 0))
        self.progress_wrap.grid(row=3, column=0, sticky="ew", pady=(12, 0))

        self.log_header = ttk.Frame(outer)
        self.log_header.grid(row=4, column=0, sticky="ew", pady=(14, 6))
        ttk.Label(self.log_header, text="Activity", font=("Segoe UI Semibold", 10)).pack(side=tk.LEFT)
        clear_log_btn = make_ghost_button(self.log_header, "Clear log", self._clear_log, self.colors)
        clear_log_btn.pack(side=tk.RIGHT)

        log_wrap = tk.Frame(outer, bg=self.colors["log_bg"])
        log_wrap.grid(row=5, column=0, sticky="nsew")
        log_wrap.columnconfigure(0, weight=1)
        log_wrap.rowconfigure(0, weight=1)
        self.log = scrolledtext.ScrolledText(log_wrap, height=8, state=tk.DISABLED, wrap=tk.WORD)
        self.log.grid(row=0, column=0, sticky="nsew")
        configure_log_widget(self.log, self.colors)

        tk.Label(
            outer, textvariable=self.status_var, bg=self.colors["bg"], fg=self.colors["muted"],
            font=("Segoe UI", 9), anchor="w",
        ).grid(row=6, column=0, sticky="ew", pady=(10, 0))

    def _add_queue_tab(
        self,
        notebook: ttk.Notebook,
        title: str,
        extension: str,
        batch: list[str],
        add_cmd,
        remove_cmd,
        clear_cmd,
        run_cmd,
        run_label: str,
    ) -> tk.Listbox:
        tab = ttk.Frame(notebook, padding=12, style="Card.TFrame")
        notebook.add(tab, text=title)

        hint = ttk.Label(
            tab,
            text=f"Drag & drop {extension} files onto the window (this tab selected), or use Add files",
            style="CardMuted.TLabel",
        )
        hint.pack(anchor="w", pady=(0, 8))

        list_wrap = ttk.Frame(tab, style="Card.TFrame")
        list_wrap.pack(fill=tk.BOTH, expand=True)
        listbox = tk.Listbox(
            list_wrap, height=6, selectmode=tk.EXTENDED, exportselection=False, activestyle="none",
            bg="#f9fafb", fg="#111827", relief=tk.FLAT,
            highlightthickness=1, highlightbackground=self.colors["border"],
            font=("Segoe UI", 9),
        )
        scroll = ttk.Scrollbar(list_wrap, orient=tk.VERTICAL, command=listbox.yview)
        listbox.configure(yscrollcommand=scroll.set)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        toolbar = ttk.Frame(tab, style="Card.TFrame")
        toolbar.pack(fill=tk.X, pady=(10, 0))

        queue_btns = ttk.Frame(toolbar, style="Card.TFrame")
        queue_btns.pack(side=tk.LEFT)
        add_btn = make_add_files_button(queue_btns, "Add files", add_cmd, self.colors)
        add_btn.pack(side=tk.LEFT)
        self._register_lockable(add_btn, "add_files")
        remove_btn = make_grey_button(queue_btns, "Remove", remove_cmd, self.colors)
        remove_btn.pack(side=tk.LEFT, padx=(8, 0))
        self._register_lockable(remove_btn, "grey")
        clear_btn = make_grey_button(queue_btns, "Clear all", clear_cmd, self.colors)
        clear_btn.pack(side=tk.LEFT, padx=(8, 0))
        self._register_lockable(clear_btn, "grey")

        run_btn = make_accent_button(toolbar, run_label, run_cmd, self.colors)
        run_btn.pack(side=tk.RIGHT)
        self._register_lockable(run_btn, "accent")

        self._register_lockable(listbox, "listbox")
        listbox.bind("<Delete>", lambda _e: remove_cmd())
        return listbox

    def _add_action_tab(self, notebook: ttk.Notebook, title: str, command, button_label: str) -> None:
        tab = ttk.Frame(notebook, padding=12, style="Card.TFrame")
        notebook.add(tab, text=title)
        action_btn = make_accent_button(tab, button_label, command, self.colors)
        action_btn.pack(anchor="w")
        self._register_lockable(action_btn, "accent")

    def _add_properties_tab(self, notebook: ttk.Notebook) -> None:
        tab = ttk.Frame(notebook, style="Card.TFrame")
        notebook.add(tab, text="Properties")

        canvas = tk.Canvas(tab, bg=self.colors["card"], highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=canvas.yview)
        inner = ttk.Frame(canvas, style="Card.TFrame", padding=12)
        inner.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
        window_id = canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def _resize_inner(event: tk.Event) -> None:
            canvas.itemconfigure(window_id, width=event.width)

        canvas.bind("<Configure>", _resize_inner)

        def _on_mousewheel(event: tk.Event) -> None:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<Enter>", lambda _e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda _e: canvas.unbind_all("<MouseWheel>"))

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Label(inner, text="CSV export — optional columns", style="Card.TLabel").pack(anchor="w")
        ttk.Label(
            inner,
            text="Selected columns are added to extracted_ris_data.csv. Screening columns start empty for Excel.",
            style="CardMuted.TLabel",
            wraplength=600,
        ).pack(anchor="w", pady=(4, 12))

        for attr, column_name, description in OPTIONAL_CSV_COLUMNS:
            row = ttk.Frame(inner, style="Card.TFrame")
            row.pack(fill=tk.X, pady=(0, 8))
            ttk.Checkbutton(
                row,
                text=column_name,
                variable=self._optional_column_vars[attr],
                style="Card.TCheckbutton",
            ).pack(anchor="w")
            ttk.Label(
                row, text=description, style="CardMuted.TLabel", wraplength=580,
            ).pack(anchor="w", padx=(22, 0))

    def _load_user_settings(self) -> None:
        saved = load_settings()
        columns = saved.get("optional_columns", {})
        if isinstance(columns, dict):
            for attr, _, _ in OPTIONAL_CSV_COLUMNS:
                if attr in columns:
                    self._optional_column_vars[attr].set(bool(columns[attr]))

        work_dir = saved.get("work_dir", "")
        if isinstance(work_dir, str) and work_dir.strip():
            folder = Path(work_dir.strip())
            if folder.is_dir():
                self.work_dir.set(str(folder.resolve()))

        geometry = saved.get("geometry", "")
        if isinstance(geometry, str) and geometry.strip():
            try:
                self.geometry(geometry.strip())
            except tk.TclError:
                pass

    def _save_user_settings(self) -> None:
        save_settings({
            "optional_columns": {
                attr: self._optional_column_vars[attr].get()
                for attr, _, _ in OPTIONAL_CSV_COLUMNS
            },
            "work_dir": self.work_dir.get().strip(),
            "geometry": self.geometry(),
        })

    def _schedule_settings_save(self, *_args) -> None:
        if self._settings_save_pending:
            return
        self._settings_save_pending = True
        self.after_idle(self._flush_settings_save)

    def _flush_settings_save(self) -> None:
        self._settings_save_pending = False
        self._save_user_settings()

    def _bind_settings_autosave(self) -> None:
        for var in self._optional_column_vars.values():
            var.trace_add("write", self._schedule_settings_save)
        self.work_dir.trace_add("write", self._schedule_settings_save)

    def _register_lockable(self, widget: tk.Misc, kind: str) -> None:
        self._lockable_widgets.append((widget, kind))

    def _clear_log(self) -> None:
        self.log.configure(state=tk.NORMAL)
        self.log.delete("1.0", tk.END)
        self.log.configure(state=tk.DISABLED)

    def _on_close(self) -> None:
        self._save_user_settings()
        self.destroy()

    def _selected_optional_columns(self) -> list[str]:
        return [
            column_name
            for attr, column_name, _ in OPTIONAL_CSV_COLUMNS
            if self._optional_column_vars[attr].get()
        ]

    def _export_csv_args(self) -> list[str]:
        selected = [name for name in self._selected_optional_columns() if name in PS_OPTIONAL_COLUMNS]
        if not selected:
            return []
        return ["-OptionalColumns", "|".join(selected)]

    def _csv_output_path(self) -> Path:
        return self._work_path() / DEFAULT_CSV_NAME

    def _enrich_csv_citations(self) -> None:
        citation_columns = [
            name for name in self._selected_optional_columns() if name in PYTHON_OPTIONAL_COLUMNS
        ]
        if not citation_columns:
            return
        try:
            added = enrich_csv_citations(self._csv_output_path(), citation_columns)
        except Exception as exc:
            self.after(0, self._log, f"Citation columns skipped: {exc}")
            return
        if added:
            self.after(0, self._log, f"Added citation columns: {', '.join(added)}")

    def _write_prisma_summary(self, export_output: str) -> None:
        stats = parse_ps_ok_line(export_output)
        if not stats:
            return
        merge_stats = self._last_merge_stats or {}
        try:
            path = write_prisma_summary(
                self._work_path(),
                identified=int(stats.get("identified", stats["unique"])),
                duplicates_removed=int(stats.get("duplicates_removed", 0)),
                unique_records=int(stats["unique"]),
                with_abstract=int(stats["with_abstract"]),
                source_files=int(stats["source_files"]),
                merge_duplicates_removed=int(merge_stats.get("duplicates_removed", 0)),
            )
        except Exception as exc:
            self.after(0, self._log, f"PRISMA summary skipped: {exc}")
            return
        self.after(0, self._log, f"Saved {path.name} — PRISMA identification counts")

    def _write_formatted_excel(self) -> None:
        csv_path = self._csv_output_path()
        try:
            xlsx_path = csv_to_formatted_xlsx(csv_path)
        except ImportError:
            self.after(
                0,
                self._log,
                "Excel workbook skipped — install openpyxl: pip install openpyxl",
            )
            return
        except Exception as exc:
            self.after(0, self._log, f"Excel workbook skipped: {exc}")
            return
        self.after(0, self._log, f"Saved {xlsx_path.name} with formatted column widths")

    def _finalize_export(self, export_output: str, *, progress_step: int | None = None, progress_total: int | None = None) -> None:
        def _step(label: str, index: int) -> None:
            if progress_step is not None and progress_total:
                self._batch_progress(progress_step + index, progress_total, label)

        _step("Writing CSV summary…", 1)
        self._log_csv_summary(export_output)
        _step("Adding citation columns…", 2)
        self._enrich_csv_citations()
        _step("Writing PRISMA summary…", 3)
        self._write_prisma_summary(export_output)
        _step("Building Excel workbook…", 4)
        self._write_formatted_excel()
        if progress_step is not None and progress_total:
            self._batch_progress(progress_total, progress_total, "Export complete")

    def _route_file_drop(self, paths: list[str]) -> None:
        try:
            tab_idx = self.notebook.index(self.notebook.select())
        except tk.TclError:
            return
        if tab_idx == 0:
            self._drop_files(self.nbib_listbox, self._nbib_batch, paths, ".nbib")
        elif tab_idx == 1:
            self._drop_files(self.ris_listbox, self._ris_batch, paths, ".ris")

    def _drop_files(self, listbox: tk.Listbox, batch: list[str], paths: list[str], extension: str) -> None:
        ext = extension.lower()
        matched = [p for p in paths if p.lower().endswith(ext)]
        if matched:
            self._add_paths_to_listbox(listbox, batch, tuple(matched))

    def _work_path(self) -> Path:
        return Path(self.work_dir.get().strip() or ".").resolve()

    def _references_ris(self) -> Path:
        return self._work_path() / CANONICAL_RIS

    def _work_temp_dir(self) -> Path:
        return self._work_path() / WORK_SUBDIR

    def _cleanup_work_temp(self) -> None:
        temp = self._work_temp_dir()
        if temp.is_dir():
            shutil.rmtree(temp, ignore_errors=True)

    def _sync_batch_from_listbox(self, listbox: tk.Listbox, batch: list[str]) -> list[str]:
        batch.clear()
        batch.extend(listbox.get(0, tk.END))
        return batch

    def _get_nbib_batch(self) -> list[str]:
        return self._sync_batch_from_listbox(self.nbib_listbox, self._nbib_batch)

    def _get_ris_batch(self) -> list[str]:
        return self._sync_batch_from_listbox(self.ris_listbox, self._ris_batch)

    def _add_paths_to_listbox(self, listbox: tk.Listbox, batch: list[str], paths: tuple[str, ...]) -> None:
        for raw in paths:
            path = str(Path(raw).resolve())
            if path not in batch:
                batch.append(path)
                listbox.insert(tk.END, path)
        if paths:
            self.work_dir.set(str(Path(paths[0]).resolve().parent))

    def _pick_files(self, title: str, extension: str) -> tuple[str, ...]:
        self.lift()
        self.focus_force()
        ext = extension.lstrip(".")
        return filedialog.askopenfilenames(
            parent=self,
            title=title,
            initialdir=self._work_path(),
            filetypes=[(ext.upper(), f"*.{ext}"), ("All files", "*.*")],
        )

    def _add_nbib_files(self) -> None:
        paths = self._pick_files("Select NBIB files", ".nbib")
        if paths:
            self._add_paths_to_listbox(self.nbib_listbox, self._nbib_batch, paths)

    def _add_ris_files(self) -> None:
        paths = self._pick_files("Select RIS files", ".ris")
        if paths:
            self._add_paths_to_listbox(self.ris_listbox, self._ris_batch, paths)

    def _remove_from_listbox(self, listbox: tk.Listbox, batch: list[str]) -> None:
        selected = list(listbox.curselection())
        if not selected:
            messagebox.showinfo(APP_TITLE, "Select one or more files in the list first.")
            return
        for index in reversed(selected):
            listbox.delete(index)
        self._sync_batch_from_listbox(listbox, batch)

    def _remove_nbib_files(self) -> None:
        self._remove_from_listbox(self.nbib_listbox, self._nbib_batch)

    def _remove_ris_files(self) -> None:
        self._remove_from_listbox(self.ris_listbox, self._ris_batch)

    def _clear_nbib_files(self) -> None:
        self.nbib_listbox.delete(0, tk.END)
        self._nbib_batch.clear()

    def _clear_ris_files(self) -> None:
        self.ris_listbox.delete(0, tk.END)
        self._ris_batch.clear()

    @staticmethod
    def _select_export_ris_files(all_files: list[Path]) -> list[Path]:
        """Skip base .ris when a matching -with-urls.ris exists (avoids pipeline duplicates)."""
        names = {path.name for path in all_files}
        selected: list[Path] = []
        for path in all_files:
            stem = path.stem
            if stem.endswith("-with-urls"):
                selected.append(path)
                continue
            if f"{stem}-with-urls.ris" in names:
                continue
            selected.append(path)
        return selected

    def _ris_files_in_work_dir(self) -> list[Path]:
        folder = self._work_path()
        if not folder.is_dir():
            return []
        canonical = folder / CANONICAL_RIS
        if canonical.is_file():
            return [canonical]
        all_files = sorted(folder.glob("*.ris"))
        return self._select_export_ris_files(all_files)

    def _require_ris_files(self, purpose: str) -> bool:
        files = self._ris_files_in_work_dir()
        if files:
            return True
        messagebox.showinfo(
            APP_TITLE,
            f"No .ris files found in the working folder.\n\n{purpose}",
        )
        return False

    def _ps_error_message(self, script: str, code: int, output: str) -> str:
        if script in _PS_ERRORS and code in _PS_ERRORS[script]:
            return _PS_ERRORS[script][code]
        if "NO_RIS_FILES" in output:
            return _PS_ERRORS.get(script, {}).get(1, "No .ris files found in the working folder.")
        if "NO_ENTRIES" in output:
            return _PS_ERRORS["process_ris_files.ps1"][2]
        if "NO_URLS" in output:
            return _PS_ERRORS["extract_urls_with_titles.ps1"][2]
        return f"{script} failed (exit code {code})."

    def _merge_ris_files(self, inputs: list[str], *, label: str) -> str:
        if not inputs:
            raise RuntimeError("No .ris files to merge.")
        args = [
            "-OutputFile", str(self._references_ris()),
            "-InputFiles", "|".join(inputs),
        ]
        return self._ps_run("merge_ris.ps1", args, label=label, quiet=True)

    def _log_merge_summary(self, output: str) -> None:
        stats = parse_merge_ok_line(output)
        if stats:
            self._last_merge_stats = {
                "unique": int(stats["unique"]),
                "duplicates_removed": int(stats.get("duplicates_removed", 0)),
                "identified": int(stats["identified"]),
            }
            message = (
                f"Merged {stats['filename']} — {stats['unique']} unique records "
                f"from {stats['identified']} total"
            )
            removed = int(stats.get("duplicates_removed", 0))
            if removed > 0:
                message += f" ({removed} duplicate(s) skipped)"
            self.after(0, self._log, message)
            return
        self._last_merge_stats = None
        self.after(0, self._log, "Merge complete.")

    def _enrich_references_in_place(self, *, label: str) -> None:
        refs = str(self._references_ris())
        self._ps_run(
            "add_pubmed_urls.ps1",
            ["-InputFile", refs, "-OutputFile", refs],
            label=label,
            quiet=True,
        )

    def _ps_run(
        self,
        script: str,
        args: list[str],
        *,
        label: str,
        quiet: bool = False,
    ) -> str:
        code, output = run_powershell(
            script,
            args,
            self._work_path(),
            lambda m: self.after(0, self._log, m),
            quiet=quiet,
        )
        if code != 0:
            raise RuntimeError(self._ps_error_message(script, code, output))
        return output.strip()

    def _batch_progress(self, index: int, total: int, label: str) -> None:
        pct = round((index / total) * 100) if total else 0
        self.after(0, self._set_progress, pct, label)

    def _log(self, message: str) -> None:
        self.log.configure(state=tk.NORMAL)
        self.log.insert(tk.END, message + "\n")
        self.log.see(tk.END)
        self.log.configure(state=tk.DISABLED)

    def _show_progress(self, label: str = "") -> None:
        if label:
            self.progress_label_var.set(label)
        self._progress_visible = True
        self.update_idletasks()

    def _hide_progress(self) -> None:
        try:
            self.progress.stop()
        except tk.TclError:
            pass
        self.progress.configure(mode="determinate")
        self.progress_var.set(0.0)
        self.progress_label_var.set("")
        self._progress_visible = False

    def _set_progress(self, pct: float, label: str = "") -> None:
        self._show_progress(label)
        try:
            self.progress.stop()
        except tk.TclError:
            pass
        self.progress.configure(mode="determinate")
        self.progress_var.set(max(0.0, min(100.0, pct)))
        self.update_idletasks()

    def _start_indeterminate(self, label: str) -> None:
        self._show_progress(label)
        self.progress.configure(mode="indeterminate")
        self.progress.start(12)
        self.update_idletasks()

    def _guess_save_folder(self) -> Path:
        for path in (*self._ris_batch, *self._nbib_batch):
            if path:
                return Path(path).resolve().parent
        return self._work_path()

    def _open_path(self, target: Path) -> None:
        folder = str(target)
        if not target.is_dir():
            messagebox.showerror(APP_TITLE, f"Folder not found:\n{folder}")
            return
        if sys.platform == "win32":
            os.startfile(folder)  # noqa: S606
        elif sys.platform == "darwin":
            subprocess.run(["open", folder], check=False)
        else:
            subprocess.run(["xdg-open", folder], check=False)

    def _open_work_dir(self) -> None:
        self._open_path(self._work_path())

    def _open_save_folder(self) -> None:
        folder = self._last_save_folder or self._guess_save_folder()
        self._open_path(folder)

    def _finish_task(self, *, success: bool, title: str) -> None:
        if success:
            self._last_save_folder = self._guess_save_folder()
            self._set_progress(100, f"Done — {title}")
            self.status_var.set(f"Done — {title} — saved in {self._last_save_folder}")
            self.after(400, self._hide_progress)
        else:
            self._hide_progress()
            self.status_var.set("Failed")
        self._set_busy(False)

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        for widget, kind in self._lockable_widgets:
            if isinstance(widget, tk.Button):
                set_button_enabled(widget, self.colors, enabled=not busy, kind=kind)
            elif isinstance(widget, tk.Listbox):
                widget.configure(state=tk.NORMAL if not busy else tk.DISABLED)
            elif isinstance(widget, ttk.Entry):
                widget.configure(state="normal" if not busy else "disabled")
        try:
            self.notebook.state(["disabled"] if busy else ["!disabled"])
        except tk.TclError:
            pass
        if busy:
            self.status_var.set("Working…")
        elif self.status_var.get() in {"Working…", "Already running — please wait…"}:
            self.status_var.set("Ready")

    def _browse_work_dir(self) -> None:
        path = filedialog.askdirectory(title="Working folder", initialdir=self.work_dir.get())
        if path:
            self.work_dir.set(path)

    def _run_async(
        self,
        title: str,
        worker: Callable[[], None],
        *,
        pipeline_steps: int | None = None,
    ) -> None:
        if self._busy:
            self.status_var.set("Already running — please wait…")
            return
        self._set_busy(True)
        self._log("—" * 48)
        self._log(title)
        if pipeline_steps:
            self._set_progress(0, f"{title} — starting (0/{pipeline_steps})")
        else:
            self._start_indeterminate(title)

        def run() -> None:
            success = False
            try:
                worker()
                success = True
            except Exception as exc:
                self.after(0, lambda: messagebox.showerror(APP_TITLE, str(exc)))
                self.after(0, self._log, f"Error: {exc}")
            finally:
                self.after(0, lambda s=success, t=title: self._finish_task(success=s, title=t))

        threading.Thread(target=run, daemon=True).start()

    def _convert_nbib(self) -> None:
        files = self._get_nbib_batch()
        if not files:
            messagebox.showwarning(APP_TITLE, "Add one or more .nbib files first.")
            return

        total = len(files)

        def worker() -> None:
            temp_dir = self._work_temp_dir()
            temp_dir.mkdir(parents=True, exist_ok=True)
            temp_ris: list[str] = []
            for index, inp in enumerate(files):
                out = str(temp_dir / f"{Path(inp).stem}.ris")
                temp_ris.append(out)
                name = Path(inp).name
                self._batch_progress(index, total, f"Converting {index + 1}/{total}: {name}")
                self.after(0, self._log, f"\n>> {name}")
                self._ps_run(
                    "nbib_to_ris_converter.ps1",
                    ["-InputFile", inp, "-OutputFile", out],
                    label=f"NBIB conversion ({name})",
                )
            self._batch_progress(total, total + 1, f"Merging into {CANONICAL_RIS}")
            merge_out = self._merge_ris_files(temp_ris, label="Merge RIS")
            self._log_merge_summary(merge_out)
            self._cleanup_work_temp()
            self._batch_progress(total + 1, total + 1, "Conversion complete")

        self._run_async(
            f"NBIB → RIS ({total} file{'s' if total != 1 else ''})",
            worker,
            pipeline_steps=total + 1,
        )

    def _add_urls(self) -> None:
        files = self._get_ris_batch()
        if not files:
            messagebox.showwarning(APP_TITLE, "Add one or more .ris files first.")
            return

        total = len(files)

        def worker() -> None:
            self.after(0, self._log, f"Merging {total} .ris file(s) into {CANONICAL_RIS}")
            self._batch_progress(0, 2, "Step 1/2: Merge & dedupe")
            merge_out = self._merge_ris_files(files, label="Merge RIS")
            self._log_merge_summary(merge_out)
            self._batch_progress(1, 2, "Step 2/2: Add links")
            self._enrich_references_in_place(label="Add links")
            self._batch_progress(2, 2, "Links added")

        self._run_async(f"Add links ({total} file{'s' if total != 1 else ''})", worker, pipeline_steps=2)

    def _log_ps_summary(self, output: str, fallback: str, *, item_label: str = "entries") -> None:
        if output.startswith("OK|"):
            parts = output.split("|")
            if len(parts) >= 3:
                count, filename, file_count = parts[1], parts[2], parts[3] if len(parts) > 3 else "?"
                self.after(
                    0,
                    self._log,
                    f"Saved {filename} — {count} {item_label} from {file_count} .ris file(s)",
                )
                return
        self.after(0, self._log, fallback)

    def _log_csv_summary(self, output: str) -> None:
        if output.startswith("OK|"):
            parts = output.split("|")
            if len(parts) >= 5:
                count, filename, ris_count, abstract_count = parts[1], parts[2], parts[3], parts[4]
                removed = int(parts[5]) if len(parts) > 5 and parts[5].isdigit() else 0
                total_before = int(parts[6]) if len(parts) > 6 and parts[6].isdigit() else int(count)
                dupes_file = parts[7] if len(parts) > 7 else "duplicates_removed.csv"
                message = (
                    f"Saved {filename} — {count} unique records ({abstract_count} with abstract) "
                    f"from {ris_count} .ris file(s)"
                )
                if removed > 0:
                    message += f" — {removed} duplicate(s) removed ({total_before} before dedupe)"
                    message += f"; see {dupes_file}"
                self.after(0, self._log, message)
                return
        self._log_ps_summary(output, "CSV export complete.", item_label="records")

    def _export_csv(self) -> None:
        if not self._require_ris_files("Convert NBIB files first, or change the working folder."):
            return

        ris_count = len(self._ris_files_in_work_dir())
        folder = self._work_path()
        csv_args = self._export_csv_args()
        self._last_merge_stats = None

        export_steps = 5

        def worker() -> None:
            source = CANONICAL_RIS if (folder / CANONICAL_RIS).is_file() else f"{ris_count} .ris file(s)"
            self.after(0, self._log, f"Exporting full CSV from {source} in {folder}")
            self._batch_progress(0, export_steps, "Step 1/5: Export CSV")
            output = self._ps_run(
                "process_ris_files.ps1",
                csv_args,
                label="Export CSV",
                quiet=True,
            )
            self._finalize_export(output, progress_step=0, progress_total=export_steps)

        self._run_async("Export CSV", worker, pipeline_steps=export_steps)

    def _fetch_titles(self) -> None:
        if not self._require_ris_files("Add URL-enriched .ris files first, or change the working folder."):
            return
        if not messagebox.askyesno(
            APP_TITLE,
            f"Fetch web titles from {len(self._ris_files_in_work_dir())} .ris file(s)?\nThis can take a while.",
        ):
            return

        ris_count = len(self._ris_files_in_work_dir())
        folder = self._work_path()

        def worker() -> None:
            self.after(0, self._log, f"Fetching web titles from {ris_count} .ris file(s) in {folder}")
            output = self._ps_run("extract_urls_with_titles.ps1", [], label="Fetch web titles", quiet=True)
            self._log_ps_summary(output, "Web title fetch complete.", item_label="URLs")

        self._run_async("Fetch web titles", worker)

    def _run_pipeline(self) -> None:
        files = self._get_nbib_batch()
        if not files:
            messagebox.showwarning(APP_TITLE, "Add one or more .nbib files on tab 1 first.")
            return

        export_steps = 4
        total_steps = len(files) + 3 + export_steps
        csv_args = self._export_csv_args()

        def worker() -> None:
            step = 0
            temp_dir = self._work_temp_dir()
            temp_dir.mkdir(parents=True, exist_ok=True)
            temp_ris: list[str] = []

            for inp in files:
                name = Path(inp).name
                out_ris = str(temp_dir / f"{Path(inp).stem}.ris")
                temp_ris.append(out_ris)

                self._batch_progress(step, total_steps, f"Step {step + 1}/{total_steps}: NBIB → RIS ({name})")
                self.after(0, self._log, f"\n>> NBIB → RIS: {name}")
                self._ps_run(
                    "nbib_to_ris_converter.ps1",
                    ["-InputFile", inp, "-OutputFile", out_ris],
                    label=f"NBIB → RIS ({name})",
                )
                step += 1

            self._batch_progress(step, total_steps, f"Step {step + 1}/{total_steps}: Merge & dedupe")
            self.after(0, self._log, f"\n>> Merge into {CANONICAL_RIS}")
            merge_out = self._merge_ris_files(temp_ris, label="Merge RIS")
            self._log_merge_summary(merge_out)
            self._cleanup_work_temp()
            step += 1

            self._batch_progress(step, total_steps, f"Step {step + 1}/{total_steps}: Add links")
            self.after(0, self._log, f"\n>> Add links to {CANONICAL_RIS}")
            self._enrich_references_in_place(label="Add links")
            step += 1

            self._batch_progress(step, total_steps, f"Step {step + 1}/{total_steps}: Export CSV")
            if not self._references_ris().is_file():
                raise RuntimeError(f"{CANONICAL_RIS} was not created in the working folder.")
            self.after(0, self._log, f"\n>> Export full CSV from {CANONICAL_RIS}")
            output = self._ps_run(
                "process_ris_files.ps1",
                csv_args,
                label="Export CSV",
                quiet=True,
            )
            self._finalize_export(output, progress_step=step, progress_total=total_steps)
            self._batch_progress(total_steps, total_steps, "Batch pipeline complete")

        count = len(files)
        self._run_async(
            f"Batch pipeline ({count} file{'s' if count != 1 else ''})",
            worker,
            pipeline_steps=total_steps,
        )


def main() -> None:
    PubmedConverterApp().mainloop()


if __name__ == "__main__":
    main()
