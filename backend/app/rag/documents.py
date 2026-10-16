"""Turn the policy PDFs into small, searchable passages ("chunks").

Steps for each PDF:
  1. Extract the text of every page.
  2. Clean it: drop lines repeated on most pages (headers/footers) and skip
     table-of-contents pages, which mention every topic but explain none.
  3. Split it into overlapping passages of roughly CHUNK_SIZE characters,
     remembering which page(s) each passage came from, for citations.
"""

import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

POLICIES_DIR = Path(__file__).resolve().parents[2] / "policies"

# About 800 characters is a paragraph or two: small enough to be about one topic,
# and within what the local embedding model reads (it ignores text past ~1,000 characters).
CHUNK_SIZE = 800
# Each passage repeats the last ~150 characters of the previous one, so a sentence
# that falls on a boundary is still found whole in at least one passage.
CHUNK_OVERLAP = 150


@dataclass
class Chunk:
    source: str  # file name, e.g. "Kanerika Employee Handbook.pdf"
    pages: str  # e.g. "3" or "2-3"
    text: str


def load_all_chunks() -> tuple[list[Chunk], list[str]]:
    """Chunks from every PDF in the policies folder, plus notes on what was skipped."""
    chunks, notes = [], []
    for path in sorted(POLICIES_DIR.glob("*.pdf")):
        pages = _clean_pages(path, notes)
        chunks.extend(_split_into_chunks(path.name, pages))
    return chunks, notes


def _clean_pages(path: Path, notes: list[str]) -> list[tuple[int, list[str]]]:
    """Returns [(page_number, [lines])], with headers/footers and contents pages removed."""
    raw_pages = [(page.extract_text() or "") for page in PdfReader(path).pages]
    page_lines = [[_tidy(line) for line in text.splitlines() if _tidy(line)] for text in raw_pages]

    # A line that appears on at least half the pages (and at least 3) is a header or footer.
    counts = Counter(line for lines in page_lines for line in set(lines))
    threshold = max(3, len(page_lines) // 2)
    repeated = {line for line, n in counts.items() if n >= threshold}
    if repeated:
        notes.append(f"{path.name}: removed repeated header/footer: {sorted(repeated)}")

    cleaned = []
    for number, lines in enumerate(page_lines, start=1):
        lines = [line for line in lines if line not in repeated]
        if _looks_like_contents_page(lines):
            notes.append(f"{path.name}: skipped page {number} (table of contents)")
            continue
        if lines:
            cleaned.append((number, lines))
    return cleaned


def _tidy(line: str) -> str:
    return re.sub(r"\s+", " ", line).strip()


def _looks_like_contents_page(lines: list[str]) -> bool:
    """Most lines end in a page number, like "General Guidelines 7"."""
    if len(lines) < 10:
        return False
    ending_in_number = sum(1 for line in lines if re.search(r"\D\s\d{1,3}$", line))
    return ending_in_number / len(lines) > 0.5


def _split_into_chunks(source: str, pages: list[tuple[int, list[str]]]) -> list[Chunk]:
    """Group lines into passages of about CHUNK_SIZE characters, with overlap."""
    lines = [(page, line) for page, page_lines in pages for line in page_lines]
    chunks, current, has_new_lines = [], [], False

    for page, line in lines:
        current.append((page, line))
        has_new_lines = True
        if sum(len(text) + 1 for _, text in current) >= CHUNK_SIZE:
            chunks.append(_make_chunk(source, current))
            # Start the next passage with the last few lines of this one (the overlap).
            overlap, size = [], 0
            for item in reversed(current):
                size += len(item[1]) + 1
                if size > CHUNK_OVERLAP:
                    break
                overlap.insert(0, item)
            current, has_new_lines = overlap, False

    if has_new_lines:  # leftover lines at the end of the document
        chunks.append(_make_chunk(source, current))
    return chunks


def _make_chunk(source: str, lines: list[tuple[int, str]]) -> Chunk:
    first, last = lines[0][0], lines[-1][0]
    pages = str(first) if first == last else f"{first}-{last}"
    return Chunk(source=source, pages=pages, text="\n".join(text for _, text in lines))
