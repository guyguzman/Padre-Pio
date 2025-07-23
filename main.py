#!/usr/bin/env python3
"""
extract_letters.py
Read a 366-page PDF of letters, structure each page into
date / paragraphs / metadata, and write extracted_pages.json
"""

import re
import json
from pypdf import PdfReader

INPUT_PDF  = "Letters.pdf"
OUTPUT_JSON = "extracted_pages.json"

# ------------------------------------------------------------------
# Helper regexes
MONTH_NAMES = {
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
}
CAPITALIZED_MONTH_RE = re.compile(r"^(January|February|March|April|May|June|"
                                  r"July|August|September|October|November|December)$")

DATE_RE = re.compile(
    r"^(January|February|March|April|May|June|"
    r"July|August|September|October|November|December)\s+"
    r"(?:[1-9]|[12][0-9]|3[01])(?:st|nd|rd|th)$"
)

def is_capitalized_month(text: str) -> bool:
    return bool(CAPITALIZED_MONTH_RE.match(text.strip()))

def is_date(text: str) -> bool:
    return bool(DATE_RE.match(text.strip()))
# ------------------------------------------------------------------

def parse_page(text: str):
    """
    Turn raw page text into (date, paragraphs, metadata).
    Paragraphs are split on blank lines.
    """
    lines = text.splitlines()
    # Split into non-empty blocks/paragraphs
    blocks = []
    current = []
    for ln in lines:
        stripped = ln.strip()
        if stripped:
            current.append(stripped)
        else:
            if current:
                blocks.append(" ".join(current))
                current = []
    if current:
        blocks.append(" ".join(current))

    # Remove blocks that are just a capitalized month
    blocks = [b for b in blocks if not is_capitalized_month(b)]

    date_block = None
    date_idx   = None
    for idx, blk in enumerate(blocks):
        if is_date(blk):
            date_block = blk
            date_idx   = idx
            break

    if date_block is None:
        # Fallback: first non-empty block becomes date
        date_block = blocks[0] if blocks else ""
        date_idx   = 0

    paragraphs = blocks[date_idx+1:-1]   # between date and last block
    metadata   = blocks[-1] if blocks else ""

    return date_block, paragraphs, metadata

def main():
    reader = PdfReader(INPUT_PDF)
    out_pages = []

    for page_obj in reader.pages:
        raw_text = page_obj.extract_text() or ""
        date, paras, meta = parse_page(raw_text)
        out_pages.append({
            "date": date,
            "paragraphs": paras,
            "metadata": meta
        })

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out_pages, f, indent=2, ensure_ascii=False)

    print(f"Extracted {len(out_pages)} pages → {OUTPUT_JSON}")

if __name__ == "__main__":
    main()