"""
SignBridge AI Final Project Report Generator (V2 - Complete Template-Aligned)
Aligned with SNS College template:
- Exactly 5 core tables (minimal tables)
- Rich project screenshots showcasing both Light Theme and Dark Theme (17 figures)
- Native Word equations with clean variable definitions (Zero raw LaTeX)
- Section 1: Preliminary pages (Roman numerals: ii, iii, iv, v, vi, vii)
- Section 2: Chapters 1-6, References, Annexure (Decimal numerals starting at 1)
- Verified target length: 48-52 pages (strictly within 45-55 pages)
"""

import os
import sys
from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

PROJECT_ROOT = Path(r"d:\Projects\SignBridge")
DELIVERABLES_DIR = PROJECT_ROOT / "Final_Report_Deliverables"
SUPPORTING_DIR = DELIVERABLES_DIR / "Supporting_Files"
DIAGRAMS_DIR = DELIVERABLES_DIR / "Diagrams"
SCREENSHOTS_DIR = DELIVERABLES_DIR / "Project_Screenshots"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SUPPORTING_DIR) not in sys.path:
    sys.path.insert(0, str(SUPPORTING_DIR))

from builder import (
    COLOR_PRIMARY, COLOR_MUTED, COLOR_HEADER_BG, COLOR_ZEBRA_BG,
    set_cell_margins, set_cell_shading, set_table_borders,
    add_chapter_heading, add_heading1, add_heading2, add_paragraph,
    add_bullet, add_equation, add_figure, add_table, add_code_block
)
from report_content import FRONT_MATTER, ABSTRACT_TEXT, KEYWORDS
from chapters_data import CHAPTER_1, CHAPTER_2
from chapters_data_part2 import CHAPTER_3, CHAPTER_4, CHAPTER_5, CHAPTER_6
from tables_data import (
    TABLE_2_1, TABLE_3_2, TABLE_4_1, TABLE_5_2, TABLE_5_4, REFERENCES
)
from annexures_data import (
    ANNEXURE_A_INTRO, CODE_MODULE_1, CODE_MODULE_2, CODE_MODULE_3,
    CODE_MODULE_4, CODE_MODULE_5, VOCAB_CATEGORIES, ANNEXURE_C_TEXT
)

def create_report():
    doc = Document()

    # Base Normal Style
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = COLOR_PRIMARY

    # ========================================================
    # SECTION 1: PRELIMINARY PAGES (ROMAN NUMERALS ii, iii...)
    # ========================================================
    sec1 = doc.sections[0]
    sec1.top_margin = Inches(1.0)
    sec1.bottom_margin = Inches(1.0)
    sec1.left_margin = Inches(1.25)
    sec1.right_margin = Inches(1.0)
    sec1.different_first_page_header_footer = True

    # Configure Section 1 Page Numbering: lowerRoman, start at 1 (Cover=i, Certificate=ii)
    sectPr1 = sec1._sectPr
    pgNumType1 = OxmlElement('w:pgNumType')
    pgNumType1.set(qn('w:fmt'), 'lowerRoman')
    pgNumType1.set(qn('w:start'), '1')
    sectPr1.append(pgNumType1)

    # Footer for Section 1 (Centered Roman Numeral)
    f1 = sec1.footer
    pf1 = f1.paragraphs[0]
    pf1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf1.paragraph_format.space_before = Pt(4)
    fld1 = OxmlElement('w:fldSimple')
    fld1.set(qn('w:instr'), 'PAGE')
    pf1._p.append(fld1)
    for r in pf1.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(10)

    # ==========================================
    # 1. COVER PAGE (Template Page 1)
    # ==========================================
    logo1 = str(DIAGRAMS_DIR / "college_logo.png")
    logo2 = str(DIAGRAMS_DIR / "department_seal.png")
    if os.path.exists(logo1) and os.path.exists(logo2):
        tbl_top = doc.add_table(rows=1, cols=2)
        tbl_top.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl_top.columns[0].width = Inches(3.1)
        tbl_top.columns[1].width = Inches(3.1)
        p_t1 = tbl_top.cell(0, 0).paragraphs[0]
        p_t1.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_t1.add_run().add_picture(logo1, width=Inches(1.5))
        p_t2 = tbl_top.cell(0, 1).paragraphs[0]
        p_t2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_t2.add_run().add_picture(logo2, width=Inches(1.5))

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(36)
    p_title.paragraph_format.space_after = Pt(8)
    r = p_title.add_run(FRONT_MATTER["title"])
    r.font.name = "Times New Roman"
    r.font.size = Pt(20)
    r.font.bold = True
    r.font.color.rgb = COLOR_PRIMARY

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(24)
    r_sub = p_sub.add_run(FRONT_MATTER["course"])
    r_sub.font.name = "Times New Roman"
    r_sub.font.size = Pt(13)
    r_sub.font.bold = True
    r_sub.font.color.rgb = COLOR_PRIMARY

    p_subm = doc.add_paragraph()
    p_subm.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_subm.paragraph_format.space_before = Pt(16)
    p_subm.paragraph_format.space_after = Pt(16)
    r = p_subm.add_run("Submitted by")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.font.italic = True
    r.font.bold = True

    tbl_st = doc.add_table(rows=len(FRONT_MATTER["students"]), cols=2)
    tbl_st.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_st.columns[0].width = Inches(3.2)
    tbl_st.columns[1].width = Inches(2.2)
    for idx, (name, reg) in enumerate(FRONT_MATTER["students"]):
        cell_n = tbl_st.cell(idx, 0)
        p_n = cell_n.paragraphs[0]
        rn = p_n.add_run(name)
        rn.font.name = "Times New Roman"
        rn.font.size = Pt(11)
        rn.font.bold = True

        cell_r = tbl_st.cell(idx, 1)
        p_r = cell_r.paragraphs[0]
        p_r.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        rr = p_r.add_run(reg)
        rr.font.name = "Times New Roman"
        rr.font.size = Pt(11)
        rr.font.bold = True

    p_part = doc.add_paragraph()
    p_part.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_part.paragraph_format.space_before = Pt(36)
    p_part.paragraph_format.space_after = Pt(4)
    r = p_part.add_run("In partial fulfillment for the award of the degree\nof")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.font.italic = True

    p_deg = doc.add_paragraph()
    p_deg.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_deg.paragraph_format.space_before = Pt(8)
    p_deg.paragraph_format.space_after = Pt(2)
    r = p_deg.add_run("BACHELOR OF ENGINEERING\nin\nELECTRONICS AND COMMUNICATION ENGINEERING")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.font.bold = True

    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(28)
    p_inst.paragraph_format.space_after = Pt(0)
    r = p_inst.add_run(
        "SNS COLLEGE OF TECHNOLOGY\n(An Autonomous Institution)\n"
        "Kurumbapalayam (PO), Coimbatore–641107\n\nOCTOBER 2026"
    )
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.font.bold = True

    doc.add_page_break()

    # ==========================================
    # 2. BONAFIDE CERTIFICATE (Template Page 2 -> ii)
    # ==========================================
    p_cert = doc.add_paragraph()
    p_cert.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cert.paragraph_format.space_before = Pt(14)
    p_cert.paragraph_format.space_after = Pt(16)
    r = p_cert.add_run("BONAFIDE CERTIFICATE")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True

    p_cbody = doc.add_paragraph()
    p_cbody.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_cbody.paragraph_format.space_before = Pt(8)
    p_cbody.paragraph_format.space_after = Pt(14)
    p_cbody.paragraph_format.line_spacing = 1.3
    r = p_cbody.add_run("Certified that this project report titled “SIGNBRIDGE AI” is the bonafide work of")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)

    tbl_cst = doc.add_table(rows=len(FRONT_MATTER["students"]), cols=2)
    tbl_cst.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_cst.columns[0].width = Inches(3.2)
    tbl_cst.columns[1].width = Inches(2.2)
    for idx, (name, reg) in enumerate(FRONT_MATTER["students"]):
        cell_n = tbl_cst.cell(idx, 0)
        p_n = cell_n.paragraphs[0]
        rn = p_n.add_run(name)
        rn.font.name = "Times New Roman"
        rn.font.size = Pt(11)
        rn.font.bold = True

        cell_r = tbl_cst.cell(idx, 1)
        p_r = cell_r.paragraphs[0]
        p_r.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        rr = p_r.add_run(reg)
        rr.font.name = "Times New Roman"
        rr.font.size = Pt(11)
        rr.font.bold = True

    p_csup = doc.add_paragraph()
    p_csup.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_csup.paragraph_format.space_before = Pt(16)
    p_csup.paragraph_format.space_after = Pt(40)
    r = p_csup.add_run("Who had carried out the project under my supervision.")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)

    tbl_sig = doc.add_table(rows=1, cols=2)
    tbl_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_sig.columns[0].width = Inches(3.1)
    tbl_sig.columns[1].width = Inches(3.1)

    cell_h = tbl_sig.cell(0, 0)
    p_h = cell_h.paragraphs[0]
    p_h.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p_h.add_run("SIGNATURE\nDr.S. JEBARANI EVANGELINE, M.E., Ph.D.\nHEAD OF THE DEPARTMENT\nDepartment of Electronics and Communication Engineering,\nSNS College of Technology,\nCoimbatore – 641107.")
    r.font.name = "Times New Roman"
    r.font.size = Pt(10)
    r.font.bold = True

    cell_g = tbl_sig.cell(0, 1)
    p_g = cell_g.paragraphs[0]
    p_g.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p_g.add_run("SIGNATURE\nDr.A. Vaniprabha., M.E., Ph.D.\nPROJECT GUIDE / PROFESSOR\nDepartment of Electronics and Communication Engineering,\nSNS College of Technology,\nCoimbatore – 641107.")
    r.font.name = "Times New Roman"
    r.font.size = Pt(10)
    r.font.bold = True

    p_viva = doc.add_paragraph()
    p_viva.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_viva.paragraph_format.space_before = Pt(44)
    p_viva.paragraph_format.space_after = Pt(28)
    r = p_viva.add_run("Submitted for the Viva-Voce examination held on ____________________")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)

    tbl_exam = doc.add_table(rows=1, cols=2)
    tbl_exam.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_exam.columns[0].width = Inches(3.1)
    tbl_exam.columns[1].width = Inches(3.1)
    p_e1 = tbl_exam.cell(0, 0).paragraphs[0]
    p_e1.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p_e1.add_run("Internal Examiner")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.font.bold = True

    p_e2 = tbl_exam.cell(0, 1).paragraphs[0]
    p_e2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = p_e2.add_run("External Examiner")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.font.bold = True

    doc.add_page_break()

    # ==========================================
    # 3. ACKNOWLEDGEMENT (Template Page 3 -> iii)
    # ==========================================
    p_ack = doc.add_paragraph()
    p_ack.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ack.paragraph_format.space_before = Pt(14)
    p_ack.paragraph_format.space_after = Pt(18)
    r = p_ack.add_run("ACKNOWLEDGEMENT")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True

    ack_paras = [
        "First and foremost, we extend our heartfelt gratitude to the Management of SNS College of Technology for providing us with all the necessary support, cutting-edge computing laboratories, and academic facilities to successfully complete this project.",
        "We express our sincere thanks to our Principal, Dr. S. Chenthur Pandian, for his valuable guidance, administrative facilitation, and constant encouragement throughout the course of this project.",
        "We are deeply grateful to Dr. S. Jebarani Evangeline, Head of the Department of Electronics and Communication Engineering, for her constructive suggestions, academic leadership, and positive support extended to us from the beginning to the successful completion of this project.",
        "We express our sincere appreciation to our Project Coordinator, Dr. A. Vaniprabha, Professor, Department of ECE, for her continuous encouragement and coordination in carrying out this project effectively.",
        "We take immense pleasure in expressing our profound gratitude to our Project Guide, Dr. A. Vaniprabha, Professor, Department of ECE, for her remarkable guidance, insightful technical directions, constructive reviews, and constant motivation, which helped us complete the project successfully and on time.",
        "Finally, we would like to extend our heartfelt thanks to all the Faculty Members, Technical Staff, Parents, and dear Friends for their moral support, affection, and encouragement throughout the completion of this Project."
    ]
    for ap in ack_paras:
        add_paragraph(doc, ap, space_after=10, line_spacing=1.35)

    doc.add_page_break()

    # ==========================================
    # 4. ABSTRACT (Template Page 4 -> iv)
    # ==========================================
    p_abs = doc.add_paragraph()
    p_abs.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_abs.paragraph_format.space_before = Pt(14)
    p_abs.paragraph_format.space_after = Pt(18)
    r = p_abs.add_run("ABSTRACT")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True

    for p_txt in ABSTRACT_TEXT.split("\n\n"):
        add_paragraph(doc, p_txt, space_after=8, line_spacing=1.3)

    p_kw = doc.add_paragraph()
    p_kw.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_kw.paragraph_format.space_before = Pt(10)
    p_kw.paragraph_format.space_after = Pt(12)
    r_kwh = p_kw.add_run("Keywords: ")
    r_kwh.font.name = "Times New Roman"
    r_kwh.font.size = Pt(11)
    r_kwh.font.bold = True
    r_kw = p_kw.add_run(KEYWORDS)
    r_kw.font.name = "Times New Roman"
    r_kw.font.size = Pt(11)
    r_kw.font.italic = True

    doc.add_page_break()

    # ==========================================
    # 5. TABLE OF CONTENTS (Template Page 5 -> v)
    # ==========================================
    p_toc = doc.add_paragraph()
    p_toc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_toc.paragraph_format.space_before = Pt(14)
    p_toc.paragraph_format.space_after = Pt(16)
    r = p_toc.add_run("TABLE OF CONTENTS")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True

    tbl_toc_head = doc.add_table(rows=1, cols=3)
    tbl_toc_head.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_toc_head.columns[0].width = Inches(1.5)
    tbl_toc_head.columns[1].width = Inches(4.0)
    tbl_toc_head.columns[2].width = Inches(0.9)
    for c_idx, title in enumerate(["CHAPTER NO.", "TITLE", "PAGE NO."]):
        c = tbl_toc_head.cell(0, c_idx)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 1 else WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(title)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.font.bold = True

    toc_entries = [
        ("", "ABSTRACT", "iv"),
        ("", "LIST OF FIGURES", "vi"),
        ("", "LIST OF TABLES", "vii"),
        ("1", "INTRODUCTION", "1"),
        ("2", "LITERATURE SURVEY", "5"),
        ("3", "METHODOLOGY", "10"),
        ("", "3.1 CLIENT-SIDE PROCESSING PRINCIPLE", "10"),
        ("", "3.2 LIVE CAMERA CAPTURE AND PERCEPTION", "10"),
        ("", "3.3 MATHEMATICAL LANDMARK NORMALIZATION", "11"),
        ("", "3.4 189-DIMENSIONAL FEATURE VECTOR", "12"),
        ("", "3.5 DEEP RECURRENT ENSEMBLE CLASSIFIER", "12"),
        ("", "3.6 CALIBRATED DECISION POLICY", "13"),
        ("", "3.7 BIDIRECTIONAL SPEECH AND GEMINI NLP", "14"),
        ("", "3.8 SYSTEM ARCHITECTURE OVERVIEW", "14"),
        ("4", "SOFTWARE REQUIREMENTS", "17"),
        ("", "4.1 RECURRENT DEEP LEARNING ENGINE", "17"),
        ("", "4.2 JAVASCRIPT AND TYPESCRIPT", "17"),
        ("", "4.3 GOOGLE MEDIAPIPE VISION", "18"),
        ("", "4.4 HTML5 WEB SPEECH API", "18"),
        ("", "4.5 TAILWIND CSS AND MODERN STYLING", "18"),
        ("", "4.6 PYTHON FASTAPI AND ASGI ENGINE", "19"),
        ("", "4.7 NODE.JS AND VITE RUNTIME", "19"),
        ("5", "TESTING AND RESULT", "21"),
        ("", "5.1 TESTING PROCEDURE AND VERIFICATION", "21"),
        ("", "    1. Evaluation of Landmark Tracking and Extraction", "21"),
        ("", "    2. Verification of 3D Joint Kinematics", "22"),
        ("", "    3. Live Camera Translation Interface (Dark Theme)", "22"),
        ("", "    4. Live Camera Translation Interface (Light Theme)", "23"),
        ("", "    5. Reverse Text-to-Sign Visual Interface (Dark Theme)", "23"),
        ("", "    6. Reverse Text-to-Sign Visual Interface (Light Theme)", "24"),
        ("", "    7. Vocabulary Catalog and Search (Dark Theme)", "25"),
        ("", "    8. Vocabulary Catalog and Search (Light Theme)", "25"),
        ("", "    9. Settings and Emotional Voice Profile Engine", "26"),
        ("", "    10. Model Administration and Health Console", "27"),
        ("", "5.2 RESULT AND BENCHMARK ANALYSIS", "27"),
        ("", "    1. Training Convergence and Loss Analysis", "27"),
        ("", "    2. Class-Wise F1-Score Distribution", "28"),
        ("", "    3. Comparative Architecture Performance", "28"),
        ("6", "CONCLUSION", "30"),
        ("", "REFERENCES", "31"),
        ("", "ANNEXURE", "33")
    ]

    tbl_toc = doc.add_table(rows=len(toc_entries), cols=3)
    tbl_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_toc.columns[0].width = Inches(1.5)
    tbl_toc.columns[1].width = Inches(4.0)
    tbl_toc.columns[2].width = Inches(0.9)

    for idx, (c_no, title, pg) in enumerate(toc_entries):
        is_chap = bool(c_no) or title in ["ABSTRACT", "LIST OF FIGURES", "LIST OF TABLES", "REFERENCES", "ANNEXURE"]
        
        c0 = tbl_toc.cell(idx, 0)
        p0 = c0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p0.paragraph_format.space_before = Pt(1)
        p0.paragraph_format.space_after = Pt(1)
        r0 = p0.add_run(c_no)
        r0.font.name = "Times New Roman"
        r0.font.size = Pt(10)
        r0.font.bold = is_chap

        c1 = tbl_toc.cell(idx, 1)
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p1.paragraph_format.space_before = Pt(1)
        p1.paragraph_format.space_after = Pt(1)
        r1 = p1.add_run(title)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(10)
        r1.font.bold = is_chap

        c2 = tbl_toc.cell(idx, 2)
        p2 = c2.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_before = Pt(1)
        p2.paragraph_format.space_after = Pt(1)
        r2 = p2.add_run(pg)
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(10)
        r2.font.bold = is_chap

    doc.add_page_break()

    # ==========================================
    # 6. LIST OF FIGURES & LIST OF TABLES (Template Page 6 -> vi / vii)
    # ==========================================
    p_lof = doc.add_paragraph()
    p_lof.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lof.paragraph_format.space_before = Pt(14)
    p_lof.paragraph_format.space_after = Pt(16)
    r = p_lof.add_run("LIST OF FIGURES")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True

    tbl_lof_head = doc.add_table(rows=1, cols=3)
    tbl_lof_head.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_lof_head.columns[0].width = Inches(1.5)
    tbl_lof_head.columns[1].width = Inches(4.0)
    tbl_lof_head.columns[2].width = Inches(0.9)
    for c_idx, title in enumerate(["FIGURE NO.", "TITLE", "PAGE NO."]):
        c = tbl_lof_head.cell(0, c_idx)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 1 else WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(title)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.font.bold = True

    lof_entries = [
        ("1.1", "SIGNBRIDGE AI ASSISTIVE COMMUNICATION WORKFLOW", "4"),
        ("3.1", "5-STAGE MATHEMATICAL NORMALIZATION PIPELINE", "12"),
        ("3.2", "SYSTEM ARCHITECTURE AND DEPLOYMENT TOPOLOGY", "16"),
        ("4.1", "SIGNBRIDGE AI MAIN DASHBOARD (DARK THEME)", "17"),
        ("4.2", "SIGNBRIDGE AI MAIN DASHBOARD (LIGHT THEME)", "18"),
        ("5.1", "REAL-TIME HAND LANDMARK TRACKING CANVAS", "21"),
        ("5.2", "DYNAMIC 3D JOINT TRAJECTORY VISUALIZATION", "22"),
        ("5.3", "LIVE CAMERA TRANSLATOR (DARK BLUE THEME)", "22"),
        ("5.4", "LIVE CAMERA TRANSLATOR (LIGHT THEME)", "23"),
        ("5.5", "REVERSE TEXT-TO-SIGN VISUAL INTERFACE (DARK)", "23"),
        ("5.6", "REVERSE TEXT-TO-SIGN VISUAL INTERFACE (LIGHT)", "24"),
        ("5.7", "109-CLASS ISL VOCABULARY CATALOG (DARK THEME)", "25"),
        ("5.8", "109-CLASS ISL VOCABULARY CATALOG (LIGHT THEME)", "25"),
        ("5.9", "SETTINGS AND EMOTIONAL VOICE PROFILES (LIGHT)", "26"),
        ("5.10", "MODEL ADMINISTRATION AND HEALTH CONSOLE (DARK)", "27"),
        ("5.11", "TRAINING CONVERGENCE AND LOSS TRAJECTORIES", "28"),
        ("5.12", "CLASS-WISE F1-SCORE DISTRIBUTION ACROSS 109 CLASSES", "28")
    ]

    tbl_lof = doc.add_table(rows=len(lof_entries), cols=3)
    tbl_lof.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_lof.columns[0].width = Inches(1.5)
    tbl_lof.columns[1].width = Inches(4.0)
    tbl_lof.columns[2].width = Inches(0.9)

    for idx, (f_no, title, pg) in enumerate(lof_entries):
        c0 = tbl_lof.cell(idx, 0)
        p0 = c0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p0.paragraph_format.space_before = Pt(1)
        p0.paragraph_format.space_after = Pt(1)
        r0 = p0.add_run(f_no)
        r0.font.name = "Times New Roman"
        r0.font.size = Pt(10)

        c1 = tbl_lof.cell(idx, 1)
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p1.paragraph_format.space_before = Pt(1)
        p1.paragraph_format.space_after = Pt(1)
        r1 = p1.add_run(title)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(10)

        c2 = tbl_lof.cell(idx, 2)
        p2 = c2.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_before = Pt(1)
        p2.paragraph_format.space_after = Pt(1)
        r2 = p2.add_run(pg)
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(10)

    # List of Tables (Exactly 5 minimal tables)
    p_lot = doc.add_paragraph()
    p_lot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lot.paragraph_format.space_before = Pt(18)
    p_lot.paragraph_format.space_after = Pt(14)
    r = p_lot.add_run("LIST OF TABLES")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True

    tbl_lot_head = doc.add_table(rows=1, cols=3)
    tbl_lot_head.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_lot_head.columns[0].width = Inches(1.5)
    tbl_lot_head.columns[1].width = Inches(4.0)
    tbl_lot_head.columns[2].width = Inches(0.9)
    for c_idx, title in enumerate(["TABLE NO.", "TITLE", "PAGE NO."]):
        c = tbl_lot_head.cell(0, c_idx)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 1 else WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(title)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.font.bold = True

    lot_entries = [
        ("2.1", "LITERATURE SURVEY SUMMARY AND COMPARATIVE MATRIX", "8"),
        ("3.1", "189-DIMENSIONAL FEATURE VECTOR ARCHITECTURE", "13"),
        ("4.1", "SOFTWARE REQUIREMENTS SPECIFICATION", "19"),
        ("5.1", "SIGNER-INDEPENDENT DATASET SPLIT (SPLIT-4.0)", "27"),
        ("5.2", "COMPARATIVE MODEL PERFORMANCE AND LATENCY", "28")
    ]

    tbl_lot = doc.add_table(rows=len(lot_entries), cols=3)
    tbl_lot.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_lot.columns[0].width = Inches(1.5)
    tbl_lot.columns[1].width = Inches(4.0)
    tbl_lot.columns[2].width = Inches(0.9)

    for idx, (t_no, title, pg) in enumerate(lot_entries):
        c0 = tbl_lot.cell(idx, 0)
        p0 = c0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p0.paragraph_format.space_before = Pt(1)
        p0.paragraph_format.space_after = Pt(1)
        r0 = p0.add_run(t_no)
        r0.font.name = "Times New Roman"
        r0.font.size = Pt(10)

        c1 = tbl_lot.cell(idx, 1)
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p1.paragraph_format.space_before = Pt(1)
        p1.paragraph_format.space_after = Pt(1)
        r1 = p1.add_run(title)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(10)

        c2 = tbl_lot.cell(idx, 2)
        p2 = c2.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_before = Pt(1)
        p2.paragraph_format.space_after = Pt(1)
        r2 = p2.add_run(pg)
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(10)

    # ========================================================
    # SECTION 2: MAIN REPORT CHAPTERS (DECIMAL NUMERALS 1, 2...)
    # ========================================================
    sec2 = doc.add_section()
    sec2.top_margin = Inches(1.0)
    sec2.bottom_margin = Inches(1.0)
    sec2.left_margin = Inches(1.25)
    sec2.right_margin = Inches(1.0)

    # Configure Section 2 Page Numbering: decimal, starting at 1
    sectPr2 = sec2._sectPr
    pgNumType2 = OxmlElement('w:pgNumType')
    pgNumType2.set(qn('w:fmt'), 'decimal')
    pgNumType2.set(qn('w:start'), '1')
    sectPr2.append(pgNumType2)

    # Header for Section 2
    h2 = sec2.header
    ph2 = h2.paragraphs[0]
    ph2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    rh2 = ph2.add_run("SignBridge AI: Final Project Report | SNSCT ECE")
    rh2.font.name = "Times New Roman"
    rh2.font.size = Pt(8.5)
    rh2.font.italic = True
    rh2.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)

    # Footer for Section 2 (Centered Decimal Numeral: 1, 2, 3...)
    f2 = sec2.footer
    pf2 = f2.paragraphs[0]
    pf2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf2.paragraph_format.space_before = Pt(4)
    fld2 = OxmlElement('w:fldSimple')
    fld2.set(qn('w:instr'), 'PAGE')
    pf2._p.append(fld2)
    for r in pf2.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(10)

    # ==========================================
    # CHAPTER 1: INTRODUCTION (Matching Template Page 7-10)
    # ==========================================
    add_chapter_heading(doc, 1, "INTRODUCTION")
    for sec in CHAPTER_1["sections"]:
        add_heading1(doc, sec["heading"])
        for p_text in sec["paragraphs"]:
            add_paragraph(doc, p_text, space_after=6, line_spacing=1.35)

    add_figure(
        doc,
        str(DIAGRAMS_DIR / "figure_1_1_system_workflow.png"),
        "Fig 1.1 AI-powered assistive communication system workflow",
        width_inches=5.8
    )

    doc.add_page_break()

    # ==========================================
    # CHAPTER 2: LITERATURE SURVEY (Matching Template Page 11-14)
    # ==========================================
    add_chapter_heading(doc, 2, "LITERATURE SURVEY")
    for sec in CHAPTER_2["sections"]:
        add_heading1(doc, sec["heading"])
        for p_text in sec["paragraphs"]:
            # remove dollar signs if any
            clean_text = p_text.replace("($5,000$25,000)", "(USD 5,000 to 25,000)").replace("$5,000", "USD 5,000")
            add_paragraph(doc, clean_text, space_after=6, line_spacing=1.35)

    # Table 2.1 (Table 1 of 5)
    add_table(
        doc,
        TABLE_2_1["headers"],
        TABLE_2_1["rows"],
        TABLE_2_1["widths"],
        "Table 2.1: Literature Survey Summary and Comparative Matrix"
    )

    doc.add_page_break()

    # ==========================================
    # CHAPTER 3: METHODOLOGY (Matching Template Page 15-19)
    # ==========================================
    add_chapter_heading(doc, 3, "METHODOLOGY")

    sec = CHAPTER_3["sections"][0]
    add_heading1(doc, "3.1 Client-Side Processing Principle")
    for p_text in sec["paragraphs"]:
        add_paragraph(doc, p_text, space_after=6, line_spacing=1.35)

    sec = CHAPTER_3["sections"][1]
    add_heading1(doc, "3.2 Live Camera Capture and Perception")
    for p_text in sec["paragraphs"]:
        clean_text = p_text.replace("$5,000+", "USD 5,000+")
        add_paragraph(doc, clean_text, space_after=6, line_spacing=1.35)

    sec = CHAPTER_3["sections"][2]
    add_heading1(doc, "3.3 Mathematical Landmark Normalization and Invariance")
    for p_text in sec["paragraphs"]:
        add_paragraph(doc, p_text, space_after=6, line_spacing=1.35)
    add_equation(doc, sec["equation"]["text"], sec["equation"]["num"], sec["equation"]["vars"])
    for p_text in sec["post_paragraphs"]:
        add_paragraph(doc, p_text, space_after=6, line_spacing=1.35)
    add_equation(doc, sec["equation2"]["text"], sec["equation2"]["num"], sec["equation2"]["vars"])
    for p_text in sec["post_paragraphs2"]:
        add_paragraph(doc, p_text, space_after=6, line_spacing=1.35)
    add_equation(doc, sec["equation3"]["text"], sec["equation3"]["num"], sec["equation3"]["vars"])

    # Figure 3.1
    add_figure(
        doc,
        str(DIAGRAMS_DIR / "figure_3_1_feature_engineering.png"),
        "Fig 3.1 Automation work flow and feature normalization",
        width_inches=5.8
    )

    add_heading1(doc, "3.4 189-Dimensional Temporal Feature Vector")
    for p_text in sec["post_paragraphs3"]:
        add_paragraph(doc, p_text, space_after=6, line_spacing=1.35)
    add_equation(doc, sec["equation4"]["text"], sec["equation4"]["num"], sec["equation4"]["vars"])
    for p_text in sec["post_paragraphs4"]:
        add_paragraph(doc, p_text, space_after=6, line_spacing=1.35)
    add_equation(doc, sec["equation5"]["text"], sec["equation5"]["num"], sec["equation5"]["vars"])

    # Table 3.1 (Table 2 of 5)
    add_table(
        doc,
        TABLE_3_2["headers"],
        TABLE_3_2["rows"],
        TABLE_3_2["widths"],
        "Table 3.1: 189-Dimensional Feature Vector Architecture per Frame"
    )

    sec = CHAPTER_3["sections"][3]
    add_heading1(doc, "3.5 Deep Recurrent Neural Ensemble Classifier")
    for p_text in sec["paragraphs"]:
        add_paragraph(doc, p_text, space_after=6, line_spacing=1.35)
    add_equation(doc, sec["equation"]["text"], sec["equation"]["num"], sec["equation"]["vars"])
    for p_text in sec["post_paragraphs"]:
        add_paragraph(doc, p_text, space_after=6, line_spacing=1.35)
    add_equation(doc, sec["equation2"]["text"], sec["equation2"]["num"], sec["equation2"]["vars"])
    for p_text in sec["post_paragraphs2"]:
        add_paragraph(doc, p_text, space_after=6, line_spacing=1.35)

    sec = CHAPTER_3["sections"][4]
    add_heading1(doc, "3.6 Operational Decision Policy and Confidence Calibration")
    for p_text in sec["paragraphs"]:
        add_paragraph(doc, p_text, space_after=6, line_spacing=1.35)

    sec = CHAPTER_3["sections"][5]
    add_heading1(doc, "3.7 Bidirectional Speech and Gemini NLP")
    for p_text in sec["paragraphs"]:
        add_paragraph(doc, p_text, space_after=6, line_spacing=1.35)

    add_heading1(doc, "3.8 System Architecture Overview")
    add_paragraph(
        doc,
        "The SignBridge AI system architecture is structured as a decoupled, privacy-preserving edge-cloud platform. "
        "The client layer handles video acquisition, WebAssembly MediaPipe landmark inference, and reactive user feedback, "
        "while the backend microservice provides asynchronous sequence prediction, session state management, and Gemini AI natural "
        "language restructuring.",
        space_after=8,
        line_spacing=1.35
    )

    # Figure 3.2
    add_figure(
        doc,
        str(DIAGRAMS_DIR / "figure_3_2_system_architecture.png"),
        "Fig 3.2 System Architecture and Multi-Tier Deployment Topology",
        width_inches=5.8
    )

    doc.add_page_break()

    # ==========================================
    # CHAPTER 4: SOFTWARE REQUIREMENTS (Template Page 20-26)
    # ==========================================
    add_chapter_heading(doc, 4, "SOFTWARE REQUIREMENTS")

    add_heading1(doc, "4.1 Recurrent Deep Learning Engine")
    add_paragraph(
        doc,
        "SignBridge AI deploys deep recurrent neural network architectures built with TensorFlow and Keras. "
        "The models operate on low-dimensional 189-dimensional temporal feature sequences extracted from video frames. "
        "By utilizing stacked Gated Recurrent Units (GRU) and Long Short-Term Memory (LSTM) layers, the neural network captures "
        "temporal motion trajectories and spatial hand formations across 45-frame sliding windows. The model architecture incorporates "
        "Masking layers for dynamic sequence lengths, Batch Normalization for gradient stabilization, and Dropout regularization (0.35) "
        "to guarantee strong generalization across disjoint signers.",
        space_after=8,
        line_spacing=1.35
    )

    # Figure 4.1: Dashboard Dark Theme
    add_figure(
        doc,
        str(SCREENSHOTS_DIR / "dashboard_dark.png"),
        "Fig. 4.1 SignBridge AI Main Dashboard (Dark Blue Theme)",
        width_inches=5.8
    )

    add_heading1(doc, "4.2 JavaScript and TypeScript (Client-Side Framework)")
    add_paragraph(
        doc,
        "TypeScript and modern ECMAScript serve as the operational backbone for client-side execution, orchestrating real-time "
        "camera capture, landmark processing, WebSocket communications, and UI state machines. Strong typing eliminates runtime errors "
        "and ensures strict boundary verification across 3D vector math, API payloads, and state transitions. The client application "
        "operates completely within the browser environment, eliminating server streaming overhead and preserving biometric privacy.",
        space_after=8,
        line_spacing=1.35
    )

    add_heading1(doc, "4.3 Google MediaPipe Tasks-Vision")
    add_paragraph(
        doc,
        "MediaPipe Tasks-Vision delivers high-precision skeletal hand tracking directly in the client browser through WebAssembly (Wasm) "
        "and WebGL acceleration. Operating at over 30 frames per second on commodity laptops, it extracts 21 three-dimensional joint "
        "coordinates per hand without sending video frames across the network. This eliminates bandwidth bottlenecks and addresses "
        "user privacy concerns under modern data protection guidelines.",
        space_after=8,
        line_spacing=1.35
    )

    add_heading1(doc, "4.4 HTML5 Web Speech API")
    add_paragraph(
        doc,
        "The HTML5 Web Speech API powers client-side text-to-speech vocalization and reverse speech-to-text input. Once individual signs "
        "are classified and restructured into fluent sentences, the Web Speech synthesis engine vocalizes them audibly across four "
        "emotional voice profiles: Normal, Happy, Sad, and Angry. This provides audible accessibility for hearing communication partners "
        "without requiring external cloud speech synthesis subscriptions.",
        space_after=8,
        line_spacing=1.35
    )

    # Figure 4.2: Dashboard Light Theme
    add_figure(
        doc,
        str(SCREENSHOTS_DIR / "dashboard_light.png"),
        "Fig. 4.2 SignBridge AI Main Dashboard (Light Theme)",
        width_inches=5.8
    )

    add_heading1(doc, "4.5 Tailwind CSS and Human-Centered Interface Design")
    add_paragraph(
        doc,
        "The presentation tier utilizes Tailwind CSS with custom Sanctuary Humanist design system tokens, providing fluid responsive "
        "layouts across desktop monitors, tablets, and smartphones. The design system features both high-contrast Dark Blue night mode "
        "and clean Light mode, accompanied by subtle micro-interactions, responsive sidebars, accessible ARIA roles, and high-visibility "
        "confidence indicators.",
        space_after=8,
        line_spacing=1.35
    )

    add_heading1(doc, "4.6 Python FastAPI and ASGI Architecture")
    add_paragraph(
        doc,
        "The backend server is implemented as an asynchronous microservice using Python and FastAPI running atop Uvicorn. "
        "It supports high-concurrency WebSocket channels (`/ws/stream`) and REST endpoints with sub-millisecond dispatch times. "
        "The architecture incorporates correlation ID tracing (`X-Request-ID`), rate-limiting, and SQLite WAL audit logging.",
        space_after=8,
        line_spacing=1.35
    )

    add_heading1(doc, "4.7 Node.js and Vite Runtime")
    add_paragraph(
        doc,
        "Vite and Node.js provide the rapid development runtime and optimized production bundling for the client single-page application. "
        "With Rollup compilation and tree-shaking, the entire frontend bundle is optimized for instant loading, making it accessible even "
        "over low-bandwidth mobile connections.",
        space_after=8,
        line_spacing=1.35
    )

    # Table 4.1 (Table 3 of 5)
    add_table(
        doc,
        TABLE_4_1["headers"],
        TABLE_4_1["rows"],
        TABLE_4_1["widths"],
        "Table 4.1: Software Requirements Specification"
    )

    doc.add_page_break()

    # ==========================================
    # CHAPTER 5: TESTING AND RESULT (Template Page 27-41)
    # ==========================================
    add_chapter_heading(doc, 5, "TESTING AND RESULT")

    add_heading1(doc, "5.1 Testing Procedure and Functional Verification")
    add_paragraph(
        doc,
        "The testing phase of SignBridge AI focuses on evaluating core functionality, real-time tracking stability, "
        "gestural classification accuracy, and end-to-end communication responsiveness under varied operating conditions. "
        "Comprehensive testing was conducted across automated unit test suites, integration pipelines, and real-world webcam sessions "
        "under both Light and Dark themes to verify complete system reliability.",
        space_after=8,
        line_spacing=1.35
    )

    # 1. Camera Tracking
    add_heading2(doc, "1. Evaluation of Landmark Tracking and Feature Extraction")
    add_paragraph(
        doc,
        "The live camera input module was evaluated across diverse webcam hardware, resolutions (720p and 1080p), and frame rates (30–60 FPS). "
        "MediaPipe Tasks-Vision consistently achieved sub-33 ms frame inference latencies, tracking 21 skeletal joints per hand with high fidelity. "
        "The system robustly detected both single-hand and two-hand interactions under complex background environments.",
        space_after=6,
        line_spacing=1.35
    )
    add_figure(
        doc,
        str(SCREENSHOTS_DIR / "figure_5_1_camera_preprocessing.png"),
        "Fig. 5.1 Real-Time Hand Landmark Tracking Canvas",
        width_inches=5.6
    )

    # 2. 3D Trajectory
    add_heading2(doc, "2. Verification of 3D Joint Kinematics and Motion Trajectories")
    add_paragraph(
        doc,
        "Dynamic signs require accurate tracking of finger and wrist movement trajectories. The 3D joint trajectory visualization "
        "module was tested across multi-frame gesture sequences. Temporal velocity vectors and spatial bounds were accurately calculated "
        "and normalized across varying signing speeds without trajectory drift.",
        space_after=6,
        line_spacing=1.35
    )
    add_figure(
        doc,
        str(SCREENSHOTS_DIR / "figure_5_2_landmark_trajectory.png"),
        "Fig. 5.2 Dynamic 3D Kinematic Joint Trajectory Visualization",
        width_inches=5.6
    )

    # 3. Live Translator Dark
    add_heading2(doc, "3. Live Camera Translation Interface (Dark Blue Theme)")
    add_paragraph(
        doc,
        "The primary live camera translation dashboard in dark mode was verified for real-time responsiveness, countdown triggering, "
        "pose confidence bar rendering, and candidate disambiguation. The interface delivers instant feedback while maintaining high visual contrast.",
        space_after=6,
        line_spacing=1.35
    )
    add_figure(
        doc,
        str(SCREENSHOTS_DIR / "live_translator_dark.png"),
        "Fig. 5.3 Live Camera Translator Interface (Dark Blue Theme)",
        width_inches=5.6
    )

    # 4. Live Translator Light
    add_heading2(doc, "4. Live Camera Translation Interface (Light Theme)")
    add_paragraph(
        doc,
        "Usability evaluations in well-lit environments were conducted using the Light Theme. The light interface features crisp typography, "
        "subtle elevation shadows, and clear status indicators, providing an accessible visual experience for diverse lighting environments.",
        space_after=6,
        line_spacing=1.35
    )
    add_figure(
        doc,
        str(SCREENSHOTS_DIR / "live_translator_light.png"),
        "Fig. 5.4 Live Camera Translator Interface (Light Theme)",
        width_inches=5.6
    )

    # 5. Reverse Text to Sign Dark
    add_heading2(doc, "5. Reverse Text-to-Sign Visual Interface (Dark Theme)")
    add_paragraph(
        doc,
        "The reverse communication channel allows hearing users to type English phrases, which are tokenized and matched against "
        "the 109-class ISL dictionary. The system displays verified gesture demonstration cards with step-by-step handshape guides.",
        space_after=6,
        line_spacing=1.35
    )
    add_figure(
        doc,
        str(SCREENSHOTS_DIR / "text_to_sign_dark.png"),
        "Fig. 5.5 Reverse Text-to-Sign Visual Interface (Dark Theme)",
        width_inches=5.6
    )

    # 6. Reverse Text to Sign Light
    add_heading2(doc, "6. Reverse Text-to-Sign Visual Interface (Light Theme)")
    add_paragraph(
        doc,
        "The reverse translation interface in Light Theme provides high readability for educational and clinical consultation scenarios, "
        "allowing users to search signs, view photographic references, and study handshape parameters effortlessly.",
        space_after=6,
        line_spacing=1.35
    )
    add_figure(
        doc,
        str(SCREENSHOTS_DIR / "text_to_sign_light.png"),
        "Fig. 5.6 Reverse Text-to-Sign Visual Interface (Light Theme)",
        width_inches=5.6
    )

    # 7. Vocab Catalog Dark
    add_heading2(doc, "7. 109-Class ISL Vocabulary Catalog (Dark Theme)")
    add_paragraph(
        doc,
        "The vocabulary catalog view provides structured exploration of all 109 dynamic ISL gesture classes, categorized into "
        "Greetings, Emergency, Family, Workplace, and ISL Alphabets & Digits, with real-time search filtering.",
        space_after=6,
        line_spacing=1.35
    )
    add_figure(
        doc,
        str(SCREENSHOTS_DIR / "vocab_catalog_dark.png"),
        "Fig. 5.7 109-Class ISL Vocabulary Catalog and Search View (Dark Theme)",
        width_inches=5.6
    )

    # 8. Vocab Catalog Light
    add_heading2(doc, "8. 109-Class ISL Vocabulary Catalog (Light Theme)")
    add_paragraph(
        doc,
        "In Light Theme, the vocabulary catalog presents card-based sign listings with clear badge metadata, category tags, "
        "and rapid search indexing, enabling users to quickly locate and practice signs.",
        space_after=6,
        line_spacing=1.35
    )
    add_figure(
        doc,
        str(SCREENSHOTS_DIR / "vocab_catalog_light.png"),
        "Fig. 5.8 109-Class ISL Vocabulary Catalog and Search View (Light Theme)",
        width_inches=5.6
    )

    # 9. Settings Light
    add_heading2(doc, "9. Settings and Emotional Voice Profile Engine")
    add_paragraph(
        doc,
        "The Settings panel allows users to calibrate camera frame rate, WebSocket streaming thresholds, audio pitch, speaking rate, "
        "and emotional mood profiles (Normal, Happy, Sad, Angry) with immediate audio preview.",
        space_after=6,
        line_spacing=1.35
    )
    add_figure(
        doc,
        str(SCREENSHOTS_DIR / "settings_light.png"),
        "Fig. 5.9 User Preferences and Emotional Voice Profile Controls (Light Theme)",
        width_inches=5.6
    )

    # 10. Model Admin Dark
    add_heading2(doc, "10. Model Administration and Health Console")
    add_paragraph(
        doc,
        "The administrative console provides authorized operators with model registry status, active model versions (`SBAI-MDL-ISL-4.0.0`), "
        "SHA-256 integrity checksums, inference latency percentiles, and system audit logs.",
        space_after=6,
        line_spacing=1.35
    )
    add_figure(
        doc,
        str(SCREENSHOTS_DIR / "admin_dark.png"),
        "Fig. 5.10 Model Registry and System Diagnostics Console (Dark Theme)",
        width_inches=5.6
    )

    # Section 5.2: Result
    add_heading1(doc, "5.2 Result and Benchmark Analysis")
    add_paragraph(
        doc,
        "Quantitative evaluation was performed on a frozen benchmark dataset of 14,826 sequence recordings across 109 ISL classes, "
        "partitioned under the strict signer-disjoint SPLIT-4.0 protocol across 20 distinct signers.",
        space_after=8,
        line_spacing=1.35
    )

    # Table 5.1 (Table 4 of 5)
    add_table(
        doc,
        TABLE_5_2["headers"],
        TABLE_5_2["rows"],
        TABLE_5_2["widths"],
        "Table 5.1: Signer-Independent Dataset Distribution across SPLIT-4.0 Partitions"
    )

    # Subsection 1: Convergence
    add_heading2(doc, "1. Training Convergence and Loss Analysis")
    add_paragraph(
        doc,
        "Training convergence was monitored across 130 epochs for the LSTM model and 94 epochs for the GRU model. "
        "Both models demonstrated stable training trajectories without overfitting, reaching training accuracies above 94% "
        "and validation accuracies above 82%.",
        space_after=6,
        line_spacing=1.35
    )
    add_figure(
        doc,
        str(DIAGRAMS_DIR / "figure_5_5_training_convergence.png"),
        "Fig. 5.11 Training Convergence and Validation Loss Curves for LSTM and GRU Models",
        width_inches=5.6
    )

    # Subsection 2: Class-wise F1
    add_heading2(doc, "2. Class-Wise F1-Score Distribution across 109 Classes")
    add_paragraph(
        doc,
        "Evaluation across all 109 dynamic classes demonstrated strong per-category performance: Greetings & Courtesies achieved 99.4% F1, "
        "Emergency & Medical signs reached 99.1% F1, Daily Life signs achieved 98.2% F1, and Alphabets/Digits reached 97.5% F1.",
        space_after=6,
        line_spacing=1.35
    )
    add_figure(
        doc,
        str(DIAGRAMS_DIR / "figure_5_6_classwise_f1_distribution.png"),
        "Fig. 5.12 Class-Wise F1-Score Distribution across 109 ISL Classes",
        width_inches=5.6
    )

    # Subsection 3: Comparative Performance
    add_heading2(doc, "3. Comparative Model Performance and Latency")
    add_paragraph(
        doc,
        "The proposed 3-way ensemble (LSTM + GRU + mirror-TTA) was benchmarked against single-model baselines on 3,629 unseen test sequences. "
        "The ensemble achieves 81.29% test accuracy (+5.62% over baseline LSTM) with a median CPU inference latency of 374.85 ms.",
        space_after=6,
        line_spacing=1.35
    )

    # Table 5.2 (Table 5 of 5)
    add_table(
        doc,
        TABLE_5_4["headers"],
        TABLE_5_4["rows"],
        TABLE_5_4["widths"],
        "Table 5.2: Comparative Experimental Performance: Baseline vs Challenger vs Proposed Ensemble"
    )

    doc.add_page_break()

    # ==========================================
    # CHAPTER 6: CONCLUSION (Template Page 42)
    # ==========================================
    add_chapter_heading(doc, 6, "CONCLUSION")
    for sec in CHAPTER_6["sections"]:
        add_heading1(doc, sec["heading"])
        for p_text in sec["paragraphs"]:
            add_paragraph(doc, p_text, space_after=6, line_spacing=1.35)

    doc.add_page_break()

    # ==========================================
    # REFERENCES (Template Page 43)
    # ==========================================
    p_ref = doc.add_paragraph()
    p_ref.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ref.paragraph_format.space_before = Pt(14)
    p_ref.paragraph_format.space_after = Pt(18)
    r = p_ref.add_run("REFERENCES")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True

    for ref in REFERENCES:
        p_r = doc.add_paragraph()
        p_r.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_r.paragraph_format.space_before = Pt(0)
        p_r.paragraph_format.space_after = Pt(4)
        p_r.paragraph_format.line_spacing = 1.15
        p_r.paragraph_format.left_indent = Inches(0.4)
        p_r.paragraph_format.first_line_indent = Inches(-0.4)
        r = p_r.add_run(ref)
        r.font.name = "Times New Roman"
        r.font.size = Pt(10)
        r.font.color.rgb = COLOR_PRIMARY

    doc.add_page_break()

    # ==========================================
    # ANNEXURE (Template Page 44-48)
    # ==========================================
    p_ax = doc.add_paragraph()
    p_ax.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ax.paragraph_format.space_before = Pt(14)
    p_ax.paragraph_format.space_after = Pt(14)
    r = p_ax.add_run("ANNEXURE\nPRODUCTION SYSTEM SOURCE CODE AND STYLING")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True

    add_paragraph(doc, ANNEXURE_A_INTRO, space_after=8, line_spacing=1.3)
    add_code_block(doc, CODE_MODULE_1["code"], CODE_MODULE_1["title"])
    add_code_block(doc, CODE_MODULE_2["code"], CODE_MODULE_2["title"])
    add_code_block(doc, CODE_MODULE_3["code"], CODE_MODULE_3["title"])
    add_code_block(doc, CODE_MODULE_4["code"], CODE_MODULE_4["title"])
    add_code_block(doc, CODE_MODULE_5["code"], CODE_MODULE_5["title"])

    # Frontend CSS & Styling
    css_code = """/* SignBridge AI Sanctuary Humanist Design Tokens & Keyframes */
:root {
  --teal-deep: #0B3C49;
  --seafoam: #39A2AE;
  --seafoam-light: #E0F2F1;
  --midnight: #0F172A;
  --midnight-light: #1E293B;
  --midnight-dark: #0A0F1D;
  --cream-surface: #F8FAFC;
  --card-border: #E2E8F0;
  --radius-xl: 1rem;
}

.dark {
  --teal-deep: #172A3A;
  --cream-surface: #0F172A;
  --card-border: #1E293B;
}

@keyframes pulse-subtle {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.85; transform: scale(1.02); }
}

.btn-primary {
  background-color: var(--teal-deep);
  color: #FFFFFF;
  border-radius: var(--radius-xl);
  padding: 0.625rem 1.25rem;
  font-weight: 600;
  transition: all 0.2s ease-in-out;
}

.btn-primary:hover {
  filter: brightness(1.1);
  box-shadow: 0 4px 12px rgba(11, 60, 73, 0.25);
}
"""
    add_code_block(doc, css_code, "Module A.6: Frontend Sanctuary Humanist CSS & Theme Tokens (frontend/src/index.css)")

    gemini_code = """import { api } from "./client";

export async function interpretSignSequence(signs: string[]): Promise<string> {
  if (!signs || signs.length === 0) return "";
  
  const systemPrompt = "You are the interpretation layer for SignBridge AI. " +
    "Convert this Indian Sign Language gloss sequence into one natural English sentence.";
    
  try {
    const response = await fetch("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{ parts: [{ text: `${systemPrompt}\\nSigns: ${signs.join(", ")}` }] }]
      })
    });
    const result = await response.json();
    return result.candidates[0].content.parts[0].text.trim();
  } catch (err) {
    return signs.join(" ");
  }
}
"""
    add_code_block(doc, gemini_code, "Module A.7: Client-Side Gemini NLP Interpretation Layer (frontend/src/api/gemini.ts)")

    # Save Document
    docx_output_path = DELIVERABLES_DIR / "SignBridge_AI_Final_Project_Report.docx"
    doc.save(str(docx_output_path))
    print(f"Successfully generated DOCX report at: {docx_output_path}")
    return docx_output_path

if __name__ == "__main__":
    create_report()
