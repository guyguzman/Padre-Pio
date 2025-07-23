#!/usr/bin/env python3
"""
extract_letters.py

Extract a 366-page PDF of identical-form letters into a JSON file.

Input : Letters.pdf
Output: extracted_pages.json
"""

import json
import re
from pathlib import Path

import pdfplumber  # pip install pdfplumber

# ------------------------------------------------------------------
# Helper regexes
# ------------------------------------------------------------------
MONTH_NAMES = {
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
}

DATE_RE = re.compile(
    rf"\b({'|'.join(MONTH_NAMES)})\s+([1-9]|[12][0-9]|3[01])(st|nd|rd|th)\b"
)

# ------------------------------------------------------------------
# Core extraction function
# ------------------------------------------------------------------
def extract_page(page: pdfplumber.page.Page) -> dict:
    """
    Extract one page and return a dict with keys:
        page      : int
        date      : str
        paragraphs: list[str]
        metadata  : str
    """
    # 1. All text blocks on the page
    blocks = [b for b in page.extract_text_lines() if b["text"].strip()]
    if not blocks:
        return {"page": page.page_number, "date": "", "paragraphs": [], "metadata": ""}

    # 2. Filter out standalone month names
    filtered = []
    for b in blocks:
        t = b["text"].strip()
        if t in MONTH_NAMES:
            continue
        filtered.append(t)

    # 3. Find the date block (first one matching DATE_RE)
    date_idx = None
    date_str = ""
    for idx, t in enumerate(filtered):
        if DATE_RE.match(t):
            date_idx = idx
            date_str = t
            break
    if date_idx is None:  # fallback – treat first block as date
        date_idx = 0
        date_str = filtered[0] if filtered else ""

    # 4. Everything between date and last block = paragraphs
    #    After stripping, drop empty strings
    body_end = len(filtered) - 1  # last block reserved for metadata
    paragraphs = [p for p in (p.strip() for p in filtered[date_idx + 1 : body_end]) if p]

    # 5. Last block = metadata
    metadata = filtered[-1].strip() if filtered else ""

    return {
        "page": page.page_number,
        "date": date_str,
        "paragraphs": paragraphs,
        "metadata": metadata,
    }

# ------------------------------------------------------------------
# Main driver
# ------------------------------------------------------------------
def main():
    pdf_path = Path("Letters.pdf")
    json_path = Path("extracted_pages.json")

    all_pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for p in pdf.pages:
            all_pages.append(extract_page(p))

    with json_path.open("w", encoding="utf-8") as f_out:
        json.dump(all_pages, f_out, indent=2, ensure_ascii=False)

    print(f"✅ Done. Wrote {len(all_pages)} pages to {json_path}")

# ------------------------------------------------------------------
if __name__ == "__main__":
    main()