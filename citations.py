"""Vancouver and AMA citation formatting for export rows."""

from __future__ import annotations


def _split_authors(authors: str) -> list[str]:
    if not authors or not authors.strip():
        return []
    return [part.strip() for part in authors.split(";") if part.strip()]


def _format_author_list_vancouver(authors: str, *, max_authors: int = 6) -> str:
    names = _split_authors(authors)
    if not names:
        return ""
    if len(names) > max_authors:
        shown = names[:max_authors]
        return ", ".join(shown) + ", et al"
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + ", " + names[-1]


def _format_author_list_ama(authors: str, *, max_authors: int = 6) -> str:
    names = _split_authors(authors)
    if not names:
        return ""
    if len(names) > max_authors:
        shown = names[:3]
        return ", ".join(shown) + ", et al"
    return ", ".join(names)


def _journal_segment(row: dict[str, str]) -> str:
    journal = (row.get("Journal") or "").strip()
    year = (row.get("Year") or "").strip()
    volume = (row.get("Volume") or "").strip()
    issue = (row.get("Issue") or "").strip()
    pages = (row.get("Pages") or "").strip()

    if not journal and not year:
        return ""

    segment = journal
    if year:
        segment += f". {year}" if segment else year
    if volume:
        segment += f";{volume}"
        if issue:
            segment += f"({issue})"
        if pages:
            segment += f":{pages}"
    elif pages:
        segment += f":{pages}"
    return segment


def format_vancouver(row: dict[str, str]) -> str:
    authors = _format_author_list_vancouver(row.get("Authors", ""))
    title = (row.get("Title") or "").strip().rstrip(".")
    journal_part = _journal_segment(row)
    doi = (row.get("DOI") or "").strip()
    pmid = (row.get("PMID") or "").strip()

    parts: list[str] = []
    if authors:
        parts.append(f"{authors}.")
    if title:
        parts.append(f"{title}.")
    if journal_part:
        parts.append(f"{journal_part}.")
    if doi:
        parts.append(f"doi:{doi}")
    elif pmid:
        parts.append(f"PMID:{pmid}")

    return " ".join(parts).strip()


def format_ama(row: dict[str, str]) -> str:
    authors = _format_author_list_ama(row.get("Authors", ""))
    title = (row.get("Title") or "").strip().rstrip(".")
    journal = (row.get("Journal") or "").strip()
    year = (row.get("Year") or "").strip()
    volume = (row.get("Volume") or "").strip()
    issue = (row.get("Issue") or "").strip()
    pages = (row.get("Pages") or "").strip()
    doi = (row.get("DOI") or "").strip()

    parts: list[str] = []
    if authors:
        parts.append(f"{authors}.")
    if title:
        parts.append(f"{title}.")
    journal_bits = journal
    if year:
        journal_bits = f"{journal_bits} {year}".strip() if journal_bits else year
    if volume:
        detail = volume
        if issue:
            detail += f"({issue})"
        if pages:
            detail += f":{pages}"
        journal_bits = f"{journal_bits};{detail}".strip(";") if journal_bits else detail
    elif pages and journal_bits:
        journal_bits += f":{pages}"
    if journal_bits:
        parts.append(f"{journal_bits}.")
    if doi:
        parts.append(f"doi:{doi}")

    return " ".join(parts).strip()
