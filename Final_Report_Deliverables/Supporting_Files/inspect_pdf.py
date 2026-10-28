"""
Inspect rendered PDF:
- Search for raw LaTeX strings ($)
- Extract chapter and section start page numbers
- Check for blank pages
- Generate thumbnail images of key pages for visual quality assurance
"""

import os
from pathlib import Path
import fitz

PDF_PATH = Path(r"d:\Projects\SignBridge\Final_Report_Deliverables\SignBridge_AI_Final_Project_Report.pdf")
OUTPUT_DIR = Path(r"d:\Projects\SignBridge\Final_Report_Deliverables\Supporting_Files\pdf_page_inspection")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def inspect():
    doc = fitz.open(str(PDF_PATH))
    total_pages = len(doc)
    print(f"Total Pages in PDF: {total_pages}")

    latex_matches = []
    chapter_pages = {}
    blank_pages = []

    for i in range(total_pages):
        page = doc[i]
        text = page.get_text()
        page_num = i + 1

        if len(text.strip()) == 0:
            blank_pages.append(page_num)

        # Check for unrendered LaTeX markers
        if "$" in text:
            # Report lines containing $
            for line in text.split("\n"):
                if "$" in line:
                    latex_matches.append((page_num, line.strip()))

        # Detect chapter headings
        for line in text.split("\n"):
            line_str = line.strip()
            if line_str.startswith("CHAPTER ") or line_str in [
                "BONAFIDE CERTIFICATE", "DECLARATION", "ACKNOWLEDGEMENT",
                "ABSTRACT", "TABLE OF CONTENTS", "LIST OF FIGURES",
                "LIST OF TABLES", "REFERENCES", "ANNEXURE A",
                "ANNEXURE B", "ANNEXURE C"
            ]:
                if line_str not in chapter_pages:
                    chapter_pages[line_str] = page_num

    print("\n--- Key Landmarks and Chapters in PDF ---")
    for heading, pg in chapter_pages.items():
        print(f"{heading:<40} -> Page {pg}")

    print("\n--- Blank Pages ---")
    if blank_pages:
        print(f"Warning: Blank pages detected at: {blank_pages}")
    else:
        print("Zero blank pages detected.")

    print("\n--- LaTeX Syntax Leakage Check ---")
    if latex_matches:
        print(f"Warning: {len(latex_matches)} instances of raw '$' found:")
        for pg, l in latex_matches[:10]:
            print(f"  Page {pg}: {l}")
    else:
        print("Clean! Zero raw '$' symbols found in the entire document.")

    # Render a few representative pages as PNG for visual QA
    sample_pages = [1, 2, 5, 6, 7, 13, 14, 16, 31, 35, 45, 47, 50, 54]
    for p_no in sample_pages:
        if p_no <= total_pages:
            page = doc[p_no - 1]
            pix = page.get_pixmap(dpi=150)
            img_path = OUTPUT_DIR / f"page_{p_no:02d}.png"
            pix.save(str(img_path))
            print(f"Rendered sample page {p_no} -> {img_path.name}")

    doc.close()

if __name__ == "__main__":
    inspect()
