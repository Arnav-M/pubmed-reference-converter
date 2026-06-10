"""Write PRISMA-style identification counts for systematic reviews."""

from __future__ import annotations

from pathlib import Path

DEFAULT_PRISMA_NAME = "prisma_summary.txt"


def write_prisma_summary(
    output_dir: Path,
    *,
    identified: int,
    duplicates_removed: int,
    unique_records: int,
    with_abstract: int,
    source_files: int = 0,
    merge_duplicates_removed: int = 0,
    filename: str = DEFAULT_PRISMA_NAME,
) -> Path:
    output_dir = Path(output_dir)
    target = output_dir / filename
    screened = unique_records

    lines = [
        "PRISMA 2020 — Identification counts",
        "===================================",
        "",
        f"Records identified (all sources):     {identified}",
    ]
    if merge_duplicates_removed:
        lines.append(f"Duplicates removed (merge step):  {merge_duplicates_removed}")
    if duplicates_removed:
        lines.append(f"Duplicates removed (export step):   {duplicates_removed}")
    total_removed = merge_duplicates_removed + duplicates_removed
    if total_removed:
        lines.append(f"Total duplicates removed:           {total_removed}")
    lines.extend(
        [
            f"Records after deduplication:          {unique_records}",
            f"Records with abstract:                {with_abstract}",
            f"Records for title/abstract screening: {screened}",
            "",
        ]
    )
    if source_files:
        lines.append(f"Source .ris file(s):                {source_files}")
        lines.append("")

    lines.append("Use these counts in your PRISMA flow diagram identification box.")
    lines.append("")

    target.write_text("\n".join(lines), encoding="utf-8")
    return target


def _last_ok_line(output: str) -> str:
    for part in reversed(output.strip().splitlines()):
        if part.startswith("OK|"):
            return part
    return output.strip().splitlines()[-1] if output.strip() else ""


def parse_merge_ok_line(output: str) -> dict[str, int | str] | None:
    line = _last_ok_line(output)
    if not line.startswith("OK|"):
        return None

    parts = line.split("|")
    if len(parts) < 6:
        return None

    return {
        "unique": int(parts[1]),
        "filename": parts[2],
        "source_files": int(parts[3]),
        "duplicates_removed": int(parts[4]),
        "identified": int(parts[5]),
    }


def parse_ps_ok_line(output: str) -> dict[str, int | str] | None:
    line = _last_ok_line(output)
    if not line.startswith("OK|"):
        return None

    parts = line.split("|")
    if len(parts) < 5:
        return None

    result: dict[str, int | str] = {
        "unique": int(parts[1]),
        "filename": parts[2],
        "source_files": int(parts[3]),
        "with_abstract": int(parts[4]),
    }
    if len(parts) > 5 and parts[5].isdigit():
        result["duplicates_removed"] = int(parts[5])
    if len(parts) > 6 and parts[6].isdigit():
        result["identified"] = int(parts[6])
    return result
