#!/usr/bin/env python3
"""
extract_padre_pio.py
Read `padrePioLetters.pdf` and write `padrePioLetters.json`.

Rules implemented
-----------------
1. Each page becomes one JSON object.
2. Page numbers are 1 … 366.
3. Ignore any text block that
      – contains a month name, and
      – does NOT contain '('
4. A text block that contains '(' followed by a month name is *metadata*.
5. Everything else (text without any month name) is body text.
6. Body text is split into paragraphs by vertical spacing.
   - Line-feeds inside a paragraph are removed.
   - Each paragraph becomes one string in the `paragraphs` array.
7. The last metadata block on the page (if any) is stored under the key
   `metadata`.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple

import PyPDF2

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MONTHS = {
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
}
MONTH_RE = re.compile(r"\b(" + "|".join(MONTHS) + r")\b", re.IGNORECASE)

INPUT_FILE  = Path("padrePioLetters.pdf")
OUTPUT_FILE = Path("padrePioLetters.json")

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def contains_month(text: str) -> bool:
    """True if any month name appears in the text."""
    return bool(MONTH_RE.search(text))

def contains_paren_month(text: str) -> bool:
    """True if text contains '(' and a month name somewhere after it."""
    # Simple check: presence of '(' and a month *anywhere* after it.
    if "(" not in text:
        return False
    after_paren = text.split("(", 1)[1]
    return contains_month(after_paren)

def split_into_paragraphs(lines: List[str]) -> List[str]:
    """
    Group consecutive non-empty lines into paragraphs.
    Blank lines (or vertical gaps represented as empty strings) are paragraph
    separators.
    """
    paragraphs = []
    current = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current:
                paragraphs.append(" ".join(current))
                current = []
        else:
            current.append(stripped)

    if current:
        paragraphs.append(" ".join(current))

    return paragraphs

def extract_page(page: PyPDF2.PageObject) -> Tuple[List[str], List[str]]:
    """
    Extract text blocks from a single PDF page.

    Returns (metadata_blocks, body_blocks)
    """
    # PyPDF2's extract_text() returns a single string.
    # We split it into lines and then group into blocks by vertical gaps.
    text = page.extract_text()
    lines = text.splitlines()
    metadata_blocks, body_blocks = [], []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if contains_paren_month(line):
            metadata_blocks.append(line)
        elif contains_month(line):
            # Ignore blocks with month but no '('
            continue
        else:
            # Body text
            body_blocks.append(line)

    return metadata_blocks, body_blocks

# ---------------------------------------------------------------------------
# Main routine
# ---------------------------------------------------------------------------

def main() -> None:
    if not INPUT_FILE.exists():
        raise SystemExit(f"Input file not found: {INPUT_FILE}")

    pages: List[Dict] = []

    with INPUT_FILE.open("rb") as f:
        reader = PyPDF2.PdfReader(f)
        total_pages = len(reader.pages)

        # Sanity check: 366 pages expected
        if total_pages != 366:
            print(
                f"Warning: PDF has {total_pages} pages, "
                "but 366 pages were expected."
            )

        for idx in range(total_pages):
            page_obj = reader.pages[idx]
            meta_blocks, body_blocks = extract_page(page_obj)
            if(idx == 1): print(f"{meta_blocks}, {body_blocks}")

            # Join body blocks into one string and split into paragraphs
            body_text = "\n".join(body_blocks)
            paragraphs = split_into_paragraphs(body_text.splitlines())

            # Last metadata block on this page (if any)
            metadata = meta_blocks[-1] if meta_blocks else None

            pages.append(
                {
                    "page_number": idx + 1,
                    "paragraphs": paragraphs,
                    "metadata": metadata,
                }
            )

    # Write the final JSON
    with OUTPUT_FILE.open("w", encoding="utf-8") as out:
        json.dump(pages, out, ensure_ascii=False, indent=2)

    print(f"Done. Wrote {len(pages)} pages to {OUTPUT_FILE}")

# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()