"""
Export DOCX to PDF using Word COM automation and verify the exact page count with PyMuPDF.
"""

import sys
import os
from pathlib import Path
import win32com.client
import fitz

DELIVERABLES_DIR = Path(r"d:\Projects\SignBridge\Final_Report_Deliverables")
DOCX_PATH = DELIVERABLES_DIR / "SignBridge_AI_Final_Project_Report.docx"
PDF_PATH = DELIVERABLES_DIR / "SignBridge_AI_Final_Project_Report.pdf"

def export_pdf():
    print(f"Opening Word document: {DOCX_PATH}")
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0

    try:
        doc = word.Documents.Open(str(DOCX_PATH.resolve()))
        print("Document opened successfully.")

        # Update all fields (TOC, page numbers, etc.)
        print("Updating fields...")
        doc.Fields.Update()
        for s in doc.Sections:
            s.Headers(1).Range.Fields.Update()
            s.Footers(1).Range.Fields.Update()

        print(f"Exporting to PDF: {PDF_PATH}")
        # 17 = wdExportFormatPDF
        doc.ExportAsFixedFormat(
            OutputFileName=str(PDF_PATH.resolve()),
            ExportFormat=17,
            OpenAfterExport=False,
            OptimizeFor=0, # wdExportOptimizeForPrint
            CreateBookmarks=1, # wdExportCreateHeadingBookmarks
            DocStructureTags=True
        )
        print("Export completed.")
        doc.Close(False)
    except Exception as e:
        print(f"Error during Word export: {e}")
        word.Quit()
        raise e
    finally:
        word.Quit()

    # Verify PDF using PyMuPDF
    if PDF_PATH.exists():
        pdf_doc = fitz.open(str(PDF_PATH))
        page_count = len(pdf_doc)
        print("=" * 60)
        print(f"PDF VERIFICATION: TOTAL PAGE COUNT = {page_count} PAGES")
        print("=" * 60)
        pdf_doc.close()
        return page_count
    else:
        print("PDF export failed, file does not exist.")
        return 0

if __name__ == "__main__":
    count = export_pdf()
    print(f"Result: {count} pages")
    sys.exit(0 if 45 <= count <= 55 else 1)
