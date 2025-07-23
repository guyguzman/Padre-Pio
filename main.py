import pdfplumber
import json
import re

def extract_letters_to_json(pdf_path, json_path):
    """
    Extract structured text from a PDF file containing 366 pages of letters.
    Each page has a consistent format:
    - A capitalized month name (ignored)
    - A date in the format "Month Day(st/nd/rd/th)" (e.g., "January 1st")
    - Paragraphs of the letter
    - A final metadata block

    The function extracts the date, paragraphs, and metadata into a JSON array.
    """
    extracted_pages = []

    # Regular expression to match the date line (e.g., "January 1st")
    date_pattern = re.compile(
        r'^(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(st|nd|rd|th)$',
        re.IGNORECASE
    )

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if not text:
                continue  # Skip empty pages

            lines = [line.strip() for line in text.split('\n') if line.strip()]
            if not lines:
                continue  # Skip if no content

            # Find the date line index
            date_index = None
            for i, line in enumerate(lines):
                if date_pattern.match(line):
                    date_index = i
                    break

            if date_index is None:
                # Handle cases where date is not found
                print(f"Warning: Date not found on page {page_num}. Skipping.")
                continue

            date = lines[date_index]

            # Extract paragraphs (everything after the date until the last line)
            paragraphs_start = date_index + 1
            paragraphs_end = len(lines) - 1  # Exclude the last line (metadata)

            if paragraphs_end <= paragraphs_start:
                # Handle cases where there might be no paragraphs
                paragraphs = []
            else:
                paragraphs = lines[paragraphs_start:paragraphs_end]

            # The last line is the metadata
            metadata = lines[-1] if lines else ""

            # Structure the page data
            page_data = {
                "page": page_num,
                "date": date,
                "paragraphs": paragraphs,
                "metadata": metadata
            }

            extracted_pages.append(page_data)

    # Write the extracted data to JSON file
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(extracted_pages, json_file, indent=4, ensure_ascii=False)

    print(f"Successfully extracted {len(extracted_pages)} pages to '{json_path}'.")

# Usage
if __name__ == "__main__":
    extract_letters_to_json('Letters.pdf', 'extracted_pages.json')