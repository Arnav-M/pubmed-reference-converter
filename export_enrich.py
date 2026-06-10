"""Post-process CSV export with citation columns."""

from __future__ import annotations

import csv
from pathlib import Path

from citations import format_ama, format_vancouver

CITATION_COLUMNS = {
    "CitationVancouver": format_vancouver,
    "CitationAMA": format_ama,
}


def enrich_csv_citations(csv_path: Path, columns: list[str]) -> list[str]:
    """Add citation columns to an exported CSV. Returns columns that were added."""
    wanted = [name for name in columns if name in CITATION_COLUMNS]
    if not wanted:
        return []

    csv_path = Path(csv_path)
    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            return []
        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    insert_at = fieldnames.index("SourceFile") if "SourceFile" in fieldnames else len(fieldnames)
    for column in wanted:
        if column not in fieldnames:
            fieldnames.insert(insert_at, column)
            insert_at += 1

    for row in rows:
        for column in wanted:
            row[column] = CITATION_COLUMNS[column](row)

    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    return wanted
