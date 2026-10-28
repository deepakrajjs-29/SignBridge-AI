"""
Find exact page numbers of figures and tables in the generated PDF.
"""

from pathlib import Path
import fitz

PDF_PATH = Path(r"d:\Projects\SignBridge\Final_Report_Deliverables\SignBridge_AI_Final_Project_Report.pdf")

def find_locations():
    doc = fitz.open(str(PDF_PATH))
    print(f"Total pages: {len(doc)}")

    targets = [
        "Figure 1.1", "Figure 3.1", "Figure 3.2",
        "Figure 5.1", "Figure 5.2", "Figure 5.3", "Figure 5.4", "Figure 5.5", "Figure 5.6",
        "Table 2.1", "Table 3.1", "Table 3.2",
        "Table 4.1", "Table 4.2", "Table 4.3",
        "Table 5.1", "Table 5.2", "Table 5.3", "Table 5.4", "Table 5.5", "Table 5.6",
        "Table B.1"
    ]

    found = {}
    for i, page in enumerate(doc):
        text = page.get_text()
        pg = i + 1
        for t in targets:
            if t in text and t not in found:
                # verify it's the caption not TOC
                if pg > 9:  # TOC is on pages 7-8, LOF/LOT on page 9
                    found[t] = pg

    for t in targets:
        print(f"{t:<15} -> Page {found.get(t, 'Not Found')}")

    doc.close()

if __name__ == "__main__":
    find_locations()
