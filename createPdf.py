#!/usr/bin/env python3
"""
Create Padre_Pio_Letters.pdf from padrePioLetters.json
"""

import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak
)
def say_hello():
    print("Hello, this is the PDF creation script for Padre Pio Letters.")

def createPdf():
# ----------------------------------------------------------------------
# Load the JSON
# ----------------------------------------------------------------------
    with open("padrePioLetters.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # ----------------------------------------------------------------------
    # Prepare PDF document
    # ----------------------------------------------------------------------
    pdf_file = "Padre_Pio_Letters.pdf"
    doc = SimpleDocTemplate(pdf_file, pagesize=A4, topMargin=40, bottomMargin=40)

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontSize=18,
        spaceAfter=20,
        spaceBefore=20,
        alignment=1,  # center
    )

    header_style = ParagraphStyle(
        "Header",
        parent=styles["Heading2"],
        fontSize=12,
        spaceAfter=8,
        textColor="#444444",
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        spaceAfter=8,
        alignment=4,  # justified
    )

    story = []

    # ----------------------------------------------------------------------
    # Build the PDF
    # ----------------------------------------------------------------------
    for entry in data:
        # Page number as title
        story.append(Paragraph(f"Page {entry['page_number']}", title_style))
        story.append(Spacer(1, 6))

        # Metadata (date / recipient)
        if entry.get("metadata"):
            story.append(Paragraph(entry["metadata"], header_style))

        # Paragraphs
        for para in entry.get("paragraphs", []):
            story.append(Paragraph(para, body_style))

        # Force a page break after every entry
        story.append(PageBreak())

    # ----------------------------------------------------------------------
    # Write to disk
    # ----------------------------------------------------------------------
    doc.build(story)
    print(f"PDF created successfully: {pdf_file}")

if __name__ == "__main__":
    say_hello()
    createPdf()  # T