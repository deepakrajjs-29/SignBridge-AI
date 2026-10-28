"""
SignBridge AI Final Project Report Generator
Constructs a complete 45-55 page academic project report following the institutional
template of SNS College of Technology (23ECP401 PROJECT IV) and IEEE style.
"""

import os
import sys
from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

# Add parent directory of backend to sys.path so deps can be imported
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
    COLOR_PRIMARY, COLOR_MUTED, COLOR_HEADER_BG, COLOR_ZEBRA_BG, COLOR_BORDER,
    set_cell_margins, set_cell_shading, set_table_borders,
    add_chapter_heading, add_heading1, add_heading2, add_paragraph,
    add_bullet, add_equation, add_figure, add_table, add_code_block
)
from report_content import FRONT_MATTER, ABSTRACT_TEXT, KEYWORDS
from chapters_data import CHAPTER_1, CHAPTER_2
from chapters_data_part2 import CHAPTER_3, CHAPTER_4, CHAPTER_5, CHAPTER_6
from tables_data import (
    TABLE_2_1, TABLE_3_1, TABLE_3_2, TABLE_4_1, TABLE_4_2, TABLE_4_3,
    TABLE_5_1, TABLE_5_2, TABLE_5_3, TABLE_5_4, TABLE_5_5, TABLE_5_6,
    REFERENCES
)
from annexures_data import (
    ANNEXURE_A_INTRO, CODE_MODULE_1, CODE_MODULE_2, CODE_MODULE_3,
    CODE_MODULE_4, CODE_MODULE_5, VOCAB_CATEGORIES, ANNEXURE_C_TEXT
)

def create_document():
    doc = Document()

    # Configure Margins: Left 1.25", Right 1.0", Top 1.0", Bottom 1.0"
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.25)
        section.right_margin = Inches(1.0)
        section.different_first_page_header_footer = True
        
        # Configure Header and Footer
        header = section.header
        p_head = header.paragraphs[0]
        p_head.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_head.paragraph_format.space_after = Pt(0)
        r_head = p_head.add_run("SignBridge AI: Final Project Report | SNSCT ECE")
        r_head.font.name = "Times New Roman"
        r_head.font.size = Pt(8.5)
        r_head.font.italic = True
        r_head.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)

        footer = section.footer
        p_foot = footer.paragraphs[0]
        p_foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_foot.paragraph_format.space_before = Pt(4)
        # Add dynamic page number field in footer
        fldSimple = OxmlElement('w:fldSimple')
        fldSimple.set(qn('w:instr'), 'PAGE')
        p_foot._p.append(fldSimple)
        for r in p_foot.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(10)
            r.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    # Base Normal Style
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = COLOR_PRIMARY

    # ==========================================
    # 1. COVER PAGE / TITLE PAGE
    # ==========================================
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(FRONT_MATTER["title"] + "\n")
    r.font.name = "Times New Roman"
    r.font.size = Pt(20)
    r.font.bold = True
    r.font.color.rgb = COLOR_PRIMARY

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(12)
    r_sub = p_sub.add_run(FRONT_MATTER["subtitle"])
    r_sub.font.name = "Times New Roman"
    r_sub.font.size = Pt(12)
    r_sub.font.bold = True
    r_sub.font.color.rgb = COLOR_MUTED

    # Logos side by side
    logo1 = str(DIAGRAMS_DIR / "college_logo.png")
    logo2 = str(DIAGRAMS_DIR / "department_seal.png")
    if os.path.exists(logo1) and os.path.exists(logo2):
        tbl_logo = doc.add_table(rows=1, cols=2)
        tbl_logo.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl_logo.columns[0].width = Inches(3.1)
        tbl_logo.columns[1].width = Inches(3.1)
        p_l1 = tbl_logo.cell(0, 0).paragraphs[0]
        p_l1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_l1.add_run().add_picture(logo1, width=Inches(1.8))
        p_l2 = tbl_logo.cell(0, 1).paragraphs[0]
        p_l2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_l2.add_run().add_picture(logo2, width=Inches(1.8))
    elif os.path.exists(logo1):
        p_l = doc.add_paragraph()
        p_l.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_l.add_run().add_picture(logo1, width=Inches(2.0))

    p_proj = doc.add_paragraph()
    p_proj.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_proj.paragraph_format.space_before = Pt(14)
    p_proj.paragraph_format.space_after = Pt(2)
    r = p_proj.add_run("A PROJECT REPORT\nSUBMITTED IN PARTIAL FULFILLMENT OF THE REQUIREMENTS\nFOR THE AWARD OF THE DEGREE OF\n")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.font.bold = True

    r_deg = p_proj.add_run(FRONT_MATTER["degree"] + "\nIN\n" + FRONT_MATTER["department"] + "\n")
    r_deg.font.name = "Times New Roman"
    r_deg.font.size = Pt(12)
    r_deg.font.bold = True

    p_subm = doc.add_paragraph()
    p_subm.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_subm.paragraph_format.space_before = Pt(8)
    p_subm.paragraph_format.space_after = Pt(2)
    r = p_subm.add_run("Submitted by:\n")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.font.bold = True

    for name, reg in FRONT_MATTER["students"]:
        p_st = doc.add_paragraph()
        p_st.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_st.paragraph_format.space_before = Pt(0)
        p_st.paragraph_format.space_after = Pt(1)
        r_name = p_st.add_run(f"{name}  ({reg})")
        r_name.font.name = "Times New Roman"
        r_name.font.size = Pt(11)
        r_name.font.bold = True

    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(16)
    p_inst.paragraph_format.space_after = Pt(0)
    r_inst = p_inst.add_run(
        f"{FRONT_MATTER['institution']}\n{FRONT_MATTER['institution_sub']}\n"
        f"{FRONT_MATTER['location']}\n\n{FRONT_MATTER['date']}"
    )
    r_inst.font.name = "Times New Roman"
    r_inst.font.size = Pt(12)
    r_inst.font.bold = True

    doc.add_page_break()

    # ==========================================
    # 2. BONAFIDE CERTIFICATE
    # ==========================================
    p_cert = doc.add_paragraph()
    p_cert.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cert.paragraph_format.space_before = Pt(12)
    p_cert.paragraph_format.space_after = Pt(16)
    r = p_cert.add_run("BONAFIDE CERTIFICATE")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True

    p_cbody = doc.add_paragraph()
    p_cbody.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_cbody.paragraph_format.space_before = Pt(6)
    p_cbody.paragraph_format.space_after = Pt(12)
    p_cbody.paragraph_format.line_spacing = 1.35
    r = p_cbody.add_run(
        "Certified that this project report titled \"SIGNBRIDGE AI: AI-POWERED REAL-TIME SIGN LANGUAGE "
        "TRANSLATION FOR SEAMLESS TWO-WAY COMMUNICATION\" is the bonafide work of "
        "AKILAN S (713323EC003), ARUTHRA SM (713323EC005), DEEPAK RAJ JS (713323EC008), and "
        "GOWTHAMAN KL (713323EC017) who carried out the project work under my supervision."
    )
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)

    p_cbody2 = doc.add_paragraph()
    p_cbody2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_cbody2.paragraph_format.space_before = Pt(6)
    p_cbody2.paragraph_format.space_after = Pt(36)
    p_cbody2.paragraph_format.line_spacing = 1.35
    r = p_cbody2.add_run(
        "Certified further that to the best of my knowledge, the work reported herein does not form part of "
        "any other thesis or dissertation on the basis of which a degree or award was conferred on an earlier "
        "occasion on this or any other candidate."
    )
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)

    tbl_sig = doc.add_table(rows=1, cols=2)
    tbl_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_sig.columns[0].width = Inches(3.1)
    tbl_sig.columns[1].width = Inches(3.1)

    cell_g = tbl_sig.cell(0, 0)
    p_g = cell_g.paragraphs[0]
    p_g.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p_g.add_run("SIGNATURE\n\n\n\nPROJECT GUIDE\nAssistant Professor,\nDepartment of ECE,\nSNS College of Technology.")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.font.bold = True

    cell_h = tbl_sig.cell(0, 1)
    p_h = cell_h.paragraphs[0]
    p_h.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = p_h.add_run("SIGNATURE\n\n\n\nHEAD OF THE DEPARTMENT\nProfessor & Head,\nDepartment of ECE,\nSNS College of Technology.")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.font.bold = True

    p_viva = doc.add_paragraph()
    p_viva.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_viva.paragraph_format.space_before = Pt(36)
    p_viva.paragraph_format.space_after = Pt(28)
    r = p_viva.add_run("Submitted for the Project Viva-Voce examination held on ............................................")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)

    tbl_exam = doc.add_table(rows=1, cols=2)
    tbl_exam.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_exam.columns[0].width = Inches(3.1)
    tbl_exam.columns[1].width = Inches(3.1)
    p_e1 = tbl_exam.cell(0, 0).paragraphs[0]
    p_e1.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p_e1.add_run("INTERNAL EXAMINER")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.font.bold = True

    p_e2 = tbl_exam.cell(0, 1).paragraphs[0]
    p_e2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = p_e2.add_run("EXTERNAL EXAMINER")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.font.bold = True

    doc.add_page_break()

    # ==========================================
    # 3. DECLARATION
    # ==========================================
    p_dec = doc.add_paragraph()
    p_dec.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dec.paragraph_format.space_before = Pt(12)
    p_dec.paragraph_format.space_after = Pt(16)
    r = p_dec.add_run("DECLARATION")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True

    p_dbody = doc.add_paragraph()
    p_dbody.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_dbody.paragraph_format.space_before = Pt(6)
    p_dbody.paragraph_format.space_after = Pt(24)
    p_dbody.paragraph_format.line_spacing = 1.35
    r = p_dbody.add_run(
        "We, AKILAN S (713323EC003), ARUTHRA SM (713323EC005), DEEPAK RAJ JS (713323EC008), and "
        "GOWTHAMAN KL (713323EC017), hereby declare that the project work titled \"SIGNBRIDGE AI: "
        "AI-POWERED REAL-TIME SIGN LANGUAGE TRANSLATION FOR SEAMLESS TWO-WAY COMMUNICATION\" is an original "
        "work carried out by us under the guidance of our Project Guide, Department of Electronics and "
        "Communication Engineering, SNS College of Technology, Coimbatore. The work has not formed the basis "
        "for the award of any degree, diploma, associate-ship, fellowship or any other similar title to any "
        "candidate of any university."
    )
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)

    p_loc = doc.add_paragraph()
    p_loc.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_loc.paragraph_format.space_before = Pt(12)
    p_loc.paragraph_format.space_after = Pt(24)
    r = p_loc.add_run("Place: Coimbatore\nDate: 25-10-2026")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)

    for name, reg in FRONT_MATTER["students"]:
        p_dsig = doc.add_paragraph()
        p_dsig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_dsig.paragraph_format.space_before = Pt(4)
        p_dsig.paragraph_format.space_after = Pt(2)
        r = p_dsig.add_run(f"...........................................................\n{name} ({reg})")
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.font.bold = True

    doc.add_page_break()

    # ==========================================
    # 4. ACKNOWLEDGEMENT
    # ==========================================
    p_ack = doc.add_paragraph()
    p_ack.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ack.paragraph_format.space_before = Pt(12)
    p_ack.paragraph_format.space_after = Pt(16)
    r = p_ack.add_run("ACKNOWLEDGEMENT")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True

    ack_texts = [
        "First and foremost, we express our profound gratitude to the Almighty for bestowing upon us the perseverance, intellectual clarity, and good health required to accomplish this major project successfully.",
        "We express our sincere thanks and heartfelt gratitude to our respected Chairman, Dr. S. N. Subbramanian, and our esteemed Correspondent, Dr. S. Rajalakshmi, for establishing an institution with exceptional academic standards and state-of-the-art technological infrastructure.",
        "We articulate our earnest appreciation to our respected Principal, Dr. S. Chenthur Pandian, for his visionary leadership, continuous administrative support, and scholastic guidance throughout our course of study.",
        "We convey our heartfelt thanks to our esteemed Head of the Department, Department of Electronics and Communication Engineering, for providing invaluable laboratory facilities, academic advice, and institutional encouragement during every phase of this project.",
        "We are profoundly indebted to our revered Project Guide, for insightful technical direction, constructive critiques, rigorous academic mentoring, and enduring patience, which served as the guiding beacon in shaping this work from conception to experimental validation.",
        "We also convey our sincere thanks to all the faculty members and technical supporting staff of the Department of Electronics and Communication Engineering for their cooperation, critical feedback, and technical assistance.",
        "Finally, we express our deepest, everlasting gratitude to our beloved parents, family members, and friends for their unconditional affection, moral support, and endless sacrifices that continue to inspire all our academic endeavors."
    ]
    for txt in ack_texts:
        add_paragraph(doc, txt, space_after=8, line_spacing=1.3)

    doc.add_page_break()

    # ==========================================
    # 5. ABSTRACT & KEYWORDS
    # ==========================================
    p_abs = doc.add_paragraph()
    p_abs.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_abs.paragraph_format.space_before = Pt(12)
    p_abs.paragraph_format.space_after = Pt(16)
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
    # 6. TABLE OF CONTENTS
    # ==========================================
    p_toc = doc.add_paragraph()
    p_toc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_toc.paragraph_format.space_before = Pt(12)
    p_toc.paragraph_format.space_after = Pt(16)
    r = p_toc.add_run("TABLE OF CONTENTS")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True

    toc_items = [
        ("BONAFIDE CERTIFICATE", "ii"),
        ("DECLARATION", "iii"),
        ("ACKNOWLEDGEMENT", "iv"),
        ("ABSTRACT", "v"),
        ("LIST OF FIGURES", "ix"),
        ("LIST OF TABLES", "ix"),
        ("CHAPTER 1: INTRODUCTION", "10"),
        ("    1.1 Motivation and Societal Background", "10"),
        ("    1.2 Problem Statement", "11"),
        ("    1.3 Objectives and Scope", "11"),
        ("    1.4 Existing Systems and Baseline Study", "12"),
        ("    1.5 Research Gap and Key Innovations", "12"),
        ("CHAPTER 2: LITERATURE SURVEY", "14"),
        ("    2.1 Historical Evolution of Sign Language Recognition", "14"),
        ("    2.2 Sensor-Based vs. Vision-Based Paradigms", "14"),
        ("    2.3 Skeletal Landmark Estimation and Tracking Frameworks", "15"),
        ("    2.4 Deep Learning Sequence Modeling Architectures", "15"),
        ("    2.5 Critical Analysis of Contemporary Literature", "16"),
        ("CHAPTER 3: SYSTEM ARCHITECTURE AND METHODOLOGY", "18"),
        ("    3.1 System Architecture and Structural Overview", "18"),
        ("    3.2 Video Acquisition and Landmark Perception", "19"),
        ("    3.3 Feature Engineering, Normalization, and Canonicalization", "20"),
        ("    3.4 Deep Recurrent Neural Network Recognition Models", "21"),
        ("    3.5 Operational Decision Policy and Confidence Calibration", "23"),
        ("    3.6 Bidirectional Communication Engine", "24"),
        ("CHAPTER 4: SOFTWARE AND HARDWARE REQUIREMENTS", "25"),
        ("    4.1 Software Architecture and Technology Stack", "25"),
        ("    4.2 Software Requirements Specification", "25"),
        ("    4.3 Hardware Requirements Specification", "26"),
        ("    4.4 Requirements Traceability Matrix (RTM)", "27"),
        ("CHAPTER 5: TESTING, RESULTS, AND DISCUSSION", "29"),
        ("    5.1 Verification and Testing Strategy", "29"),
        ("    5.2 Experimental Dataset and Partitioning Methodology", "31"),
        ("    5.3 Experimental Results and Model Performance", "31"),
        ("    5.4 Comparative Experimental Performance", "33"),
        ("    5.5 Comparison with Base System and Engineering Advantages", "35"),
        ("    5.6 Limitations and Future Scope", "36"),
        ("CHAPTER 6: CONCLUSION", "38"),
        ("    6.1 Summary of Technical Achievements", "38"),
        ("    6.2 Concluding Remarks", "38"),
        ("REFERENCES", "39"),
        ("ANNEXURE A: PRODUCTION SYSTEM SOURCE CODE", "41"),
        ("ANNEXURE B: COMPLETE 109-CLASS ISL VOCABULARY CATALOG", "46"),
        ("ANNEXURE C: SYSTEM DEPLOYMENT RUNBOOK AND CONFIGURATION", "54")
    ]

    for title, pg in toc_items:
        p_item = doc.add_paragraph()
        p_item.paragraph_format.space_before = Pt(0)
        p_item.paragraph_format.space_after = Pt(2)
        p_item.paragraph_format.line_spacing = 1.15
        
        is_main = title.startswith("CHAPTER") or title in ["BONAFIDE CERTIFICATE", "DECLARATION", "ACKNOWLEDGEMENT", "ABSTRACT", "LIST OF FIGURES", "LIST OF TABLES", "REFERENCES"] or title.startswith("ANNEXURE")
        
        r_t = p_item.add_run(title)
        r_t.font.name = "Times New Roman"
        r_t.font.size = Pt(11)
        r_t.font.bold = is_main
        r_t.font.color.rgb = COLOR_PRIMARY
        
        # Add dotted leader
        dots_len = max(5, 75 - len(title))
        r_dots = p_item.add_run(" " + "." * dots_len + " ")
        r_dots.font.name = "Times New Roman"
        r_dots.font.size = Pt(10)
        r_dots.font.color.rgb = COLOR_MUTED
        
        r_p = p_item.add_run(pg)
        r_p.font.name = "Times New Roman"
        r_p.font.size = Pt(11)
        r_p.font.bold = is_main
        r_p.font.color.rgb = COLOR_PRIMARY

    doc.add_page_break()

    # ==========================================
    # 7. LIST OF FIGURES & LIST OF TABLES
    # ==========================================
    p_lof = doc.add_paragraph()
    p_lof.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lof.paragraph_format.space_before = Pt(12)
    p_lof.paragraph_format.space_after = Pt(16)
    r = p_lof.add_run("LIST OF FIGURES")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True

    figures_list = [
        ("Figure 1.1: End-to-End System Architecture and Interaction Workflow", "13"),
        ("Figure 3.1: 5-Stage Mathematical Normalization & Feature Pipeline", "19"),
        ("Figure 3.2: High-Level System Architecture and Multi-Tier Topology", "22"),
        ("Figure 5.1: Real-Time Hand Landmark Tracking & Skeleton Extraction Canvas", "30"),
        ("Figure 5.2: Dynamic 3D Trajectory Visualization of Multi-Joint Gestures", "30"),
        ("Figure 5.3: Real-Time Sign Recognition Interface with Top-K Alternatives", "33"),
        ("Figure 5.4: Bidirectional Speech Synthesis and Text-to-Sign Visual Interface", "33"),
        ("Figure 5.5: Training Convergence and Loss Trajectories for LSTM and GRU", "32"),
        ("Figure 5.6: Class-Wise F1-Score Distribution across 109 ISL Classes", "32")
    ]
    for fig_title, pg in figures_list:
        p_f = doc.add_paragraph()
        p_f.paragraph_format.space_before = Pt(0)
        p_f.paragraph_format.space_after = Pt(3)
        r_ft = p_f.add_run(fig_title)
        r_ft.font.name = "Times New Roman"
        r_ft.font.size = Pt(11)
        dots_len = max(5, 75 - len(fig_title))
        r_fd = p_f.add_run(" " + "." * dots_len + " ")
        r_fd.font.name = "Times New Roman"
        r_fd.font.color.rgb = COLOR_MUTED
        r_fp = p_f.add_run(pg)
        r_fp.font.name = "Times New Roman"
        r_fp.font.size = Pt(11)

    p_lot = doc.add_paragraph()
    p_lot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lot.paragraph_format.space_before = Pt(20)
    p_lot.paragraph_format.space_after = Pt(16)
    r = p_lot.add_run("LIST OF TABLES")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True

    tables_list = [
        ("Table 2.1: Comprehensive Literature Survey Summary & Comparative Matrix", "17"),
        ("Table 3.1: MediaPipe 21 Hand Landmarks Reference Specification", "19"),
        ("Table 3.2: 189-Dimensional Feature Vector Architecture per Frame", "21"),
        ("Table 4.1: Software Requirements Specification", "25"),
        ("Table 4.2: Hardware Requirements Specification", "26"),
        ("Table 4.3: Requirements Traceability Matrix (RTM)", "27"),
        ("Table 5.1: Automated Test Suite Execution Results", "29"),
        ("Table 5.2: Signer-Independent Dataset Distribution across SPLIT-4.0", "31"),
        ("Table 5.3: Category-Wise Performance Breakdown across 109 ISL Classes", "32"),
        ("Table 5.4: Comparative Experimental Performance: Baseline vs Ensemble", "34"),
        ("Table 5.5: Real-World Webcam-Domain Empirical Evaluation Results", "34"),
        ("Table 5.6: Comprehensive Architectural Comparison: Shenoy et al. vs SignBridge AI", "35"),
        ("Table B.1: Complete 109-Class ISL Vocabulary Catalog", "46")
    ]
    for tbl_title, pg in tables_list:
        p_t = doc.add_paragraph()
        p_t.paragraph_format.space_before = Pt(0)
        p_t.paragraph_format.space_after = Pt(3)
        r_tt = p_t.add_run(tbl_title)
        r_tt.font.name = "Times New Roman"
        r_tt.font.size = Pt(11)
        dots_len = max(5, 75 - len(tbl_title))
        r_td = p_t.add_run(" " + "." * dots_len + " ")
        r_td.font.name = "Times New Roman"
        r_td.font.color.rgb = COLOR_MUTED
        r_tp = p_t.add_run(pg)
        r_tp.font.name = "Times New Roman"
        r_tp.font.size = Pt(11)

    doc.add_page_break()

    # ==========================================
    # CHAPTER 1: INTRODUCTION
    # ==========================================
    add_chapter_heading(doc, 1, CHAPTER_1["title"])
    for sec in CHAPTER_1["sections"]:
        add_heading1(doc, sec["heading"])
        for p_text in sec["paragraphs"]:
            add_paragraph(doc, p_text)
    
    # Figure 1.1
    add_figure(
        doc,
        str(DIAGRAMS_DIR / "figure_1_1_system_workflow.png"),
        "Figure 1.1: End-to-End System Architecture and Interaction Workflow of SignBridge AI",
        width_inches=5.8
    )

    doc.add_page_break()

    # ==========================================
    # CHAPTER 2: LITERATURE SURVEY
    # ==========================================
    add_chapter_heading(doc, 2, CHAPTER_2["title"])
    for sec in CHAPTER_2["sections"]:
        add_heading1(doc, sec["heading"])
        for p_text in sec["paragraphs"]:
            add_paragraph(doc, p_text)

    # Table 2.1
    add_table(
        doc,
        TABLE_2_1["headers"],
        TABLE_2_1["rows"],
        TABLE_2_1["widths"],
        TABLE_2_1["caption"]
    )

    doc.add_page_break()

    # ==========================================
    # CHAPTER 3: SYSTEM ARCHITECTURE AND METHODOLOGY
    # ==========================================
    add_chapter_heading(doc, 3, CHAPTER_3["title"])
    
    # 3.1
    sec = CHAPTER_3["sections"][0]
    add_heading1(doc, sec["heading"])
    for p_text in sec["paragraphs"]:
        add_paragraph(doc, p_text)
    add_figure(
        doc,
        str(DIAGRAMS_DIR / "figure_3_1_feature_engineering.png"),
        "Figure 3.1: Complete 5-Stage Mathematical Normalization and Feature Engineering Pipeline",
        width_inches=5.8
    )

    # 3.2
    sec = CHAPTER_3["sections"][1]
    add_heading1(doc, sec["heading"])
    for p_text in sec["paragraphs"]:
        add_paragraph(doc, p_text)
    add_table(
        doc,
        TABLE_3_1["headers"],
        TABLE_3_1["rows"],
        TABLE_3_1["widths"],
        TABLE_3_1["caption"]
    )

    # 3.3
    sec = CHAPTER_3["sections"][2]
    add_heading1(doc, sec["heading"])
    for p_text in sec["paragraphs"]:
        add_paragraph(doc, p_text)
    add_equation(doc, sec["equation"]["text"], sec["equation"]["num"], sec["equation"]["vars"])
    for p_text in sec["post_paragraphs"]:
        add_paragraph(doc, p_text)
    add_equation(doc, sec["equation2"]["text"], sec["equation2"]["num"], sec["equation2"]["vars"])
    for p_text in sec["post_paragraphs2"]:
        add_paragraph(doc, p_text)
    add_equation(doc, sec["equation3"]["text"], sec["equation3"]["num"], sec["equation3"]["vars"])
    for p_text in sec["post_paragraphs3"]:
        add_paragraph(doc, p_text)
    add_equation(doc, sec["equation4"]["text"], sec["equation4"]["num"], sec["equation4"]["vars"])
    for p_text in sec["post_paragraphs4"]:
        add_paragraph(doc, p_text)
    add_equation(doc, sec["equation5"]["text"], sec["equation5"]["num"], sec["equation5"]["vars"])
    add_table(
        doc,
        TABLE_3_2["headers"],
        TABLE_3_2["rows"],
        TABLE_3_2["widths"],
        TABLE_3_2["caption"]
    )

    # 3.4
    sec = CHAPTER_3["sections"][3]
    add_heading1(doc, sec["heading"])
    for p_text in sec["paragraphs"]:
        add_paragraph(doc, p_text)
    add_figure(
        doc,
        str(DIAGRAMS_DIR / "figure_3_2_system_architecture.png"),
        "Figure 3.2: High-Level System Architecture and Multi-Tier Deployment Topology",
        width_inches=5.8
    )
    add_equation(doc, sec["equation"]["text"], sec["equation"]["num"], sec["equation"]["vars"])
    for p_text in sec["post_paragraphs"]:
        add_paragraph(doc, p_text)
    add_equation(doc, sec["equation2"]["text"], sec["equation2"]["num"], sec["equation2"]["vars"])
    for p_text in sec["post_paragraphs2"]:
        add_paragraph(doc, p_text)

    # 3.5
    sec = CHAPTER_3["sections"][4]
    add_heading1(doc, sec["heading"])
    for p_text in sec["paragraphs"]:
        add_paragraph(doc, p_text)

    # 3.6
    sec = CHAPTER_3["sections"][5]
    add_heading1(doc, sec["heading"])
    for p_text in sec["paragraphs"]:
        add_paragraph(doc, p_text)

    doc.add_page_break()

    # ==========================================
    # CHAPTER 4: SOFTWARE AND HARDWARE REQUIREMENTS
    # ==========================================
    add_chapter_heading(doc, 4, CHAPTER_4["title"])
    for idx, sec in enumerate(CHAPTER_4["sections"]):
        add_heading1(doc, sec["heading"])
        for p_text in sec["paragraphs"]:
            add_paragraph(doc, p_text)
        if idx == 1:
            add_table(doc, TABLE_4_1["headers"], TABLE_4_1["rows"], TABLE_4_1["widths"], TABLE_4_1["caption"])
        elif idx == 2:
            add_table(doc, TABLE_4_2["headers"], TABLE_4_2["rows"], TABLE_4_2["widths"], TABLE_4_2["caption"])
        elif idx == 3:
            add_table(doc, TABLE_4_3["headers"], TABLE_4_3["rows"], TABLE_4_3["widths"], TABLE_4_3["caption"])

    doc.add_page_break()

    # ==========================================
    # CHAPTER 5: TESTING, RESULTS, AND DISCUSSION
    # ==========================================
    add_chapter_heading(doc, 5, CHAPTER_5["title"])
    
    # 5.1
    sec = CHAPTER_5["sections"][0]
    add_heading1(doc, sec["heading"])
    for p_text in sec["paragraphs"]:
        add_paragraph(doc, p_text)
    add_table(doc, TABLE_5_1["headers"], TABLE_5_1["rows"], TABLE_5_1["widths"], TABLE_5_1["caption"])
    add_figure(
        doc,
        str(SCREENSHOTS_DIR / "figure_5_1_camera_preprocessing.png"),
        "Figure 5.1: Real-Time Hand Landmark Tracking and Skeleton Extraction Canvas",
        width_inches=5.6
    )
    add_figure(
        doc,
        str(SCREENSHOTS_DIR / "figure_5_2_landmark_trajectory.png"),
        "Figure 5.2: Dynamic 3D Trajectory Visualization of Multi-Joint ISL Gestures",
        width_inches=5.6
    )

    # 5.2
    sec = CHAPTER_5["sections"][1]
    add_heading1(doc, sec["heading"])
    for p_text in sec["paragraphs"]:
        add_paragraph(doc, p_text)
    add_table(doc, TABLE_5_2["headers"], TABLE_5_2["rows"], TABLE_5_2["widths"], TABLE_5_2["caption"])

    # 5.3
    sec = CHAPTER_5["sections"][2]
    add_heading1(doc, sec["heading"])
    for p_text in sec["paragraphs"]:
        add_paragraph(doc, p_text)
    
    # Equations 5.1 to 5.4
    add_equation(doc, "Accuracy = (∑_{c=1}^{C} TP_c) / N × 100%", "5.1", [
        ("TP_c", "True positive classifications for class c"),
        ("N", "Total number of test sequences evaluated (N = 3,629)")
    ])
    add_equation(doc, "Macro Precision = (1 / C) ∑_{c=1}^{C} (TP_c / (TP_c + FP_c))", "5.2", [
        ("FP_c", "False positive classifications for class c"),
        ("C", "Total number of recognized vocabulary classes (C = 109)")
    ])
    add_equation(doc, "Macro Recall = (1 / C) ∑_{c=1}^{C} (TP_c / (TP_c + FN_c))", "5.3", [
        ("FN_c", "False negative misclassifications for class c")
    ])
    add_equation(doc, "Macro F1 = (1 / C) ∑_{c=1}^{C} [ 2 · (P_c · R_c) / (P_c + R_c) ]", "5.4", [
        ("P_c, R_c", "Class-specific precision and recall for category c")
    ])

    add_table(doc, TABLE_5_3["headers"], TABLE_5_3["rows"], TABLE_5_3["widths"], TABLE_5_3["caption"])

    add_figure(
        doc,
        str(SCREENSHOTS_DIR / "figure_5_3_sign_recognition_ui.png"),
        "Figure 5.3: Real-Time Sign Recognition Interface with Confidence and Top-K Alternatives",
        width_inches=5.6
    )
    add_figure(
        doc,
        str(SCREENSHOTS_DIR / "figure_5_4_twoway_speech_workflow.png"),
        "Figure 5.4: Bidirectional Speech Synthesis and Text-to-Sign Visual Demonstration Interface",
        width_inches=5.6
    )
    add_figure(
        doc,
        str(DIAGRAMS_DIR / "figure_5_5_training_convergence.png"),
        "Figure 5.5: Training Convergence and Validation Loss Curves for LSTM and GRU Models",
        width_inches=5.6
    )
    add_figure(
        doc,
        str(DIAGRAMS_DIR / "figure_5_6_classwise_f1_distribution.png"),
        "Figure 5.6: Class-Wise F1-Score Distribution across 109 ISL Classes",
        width_inches=5.6
    )

    # 5.4
    sec = CHAPTER_5["sections"][3]
    add_heading1(doc, sec["heading"])
    for p_text in sec["paragraphs"]:
        add_paragraph(doc, p_text)
    add_table(doc, TABLE_5_4["headers"], TABLE_5_4["rows"], TABLE_5_4["widths"], TABLE_5_4["caption"])
    add_table(doc, TABLE_5_5["headers"], TABLE_5_5["rows"], TABLE_5_5["widths"], TABLE_5_5["caption"])

    # 5.5
    sec = CHAPTER_5["sections"][4]
    add_heading1(doc, sec["heading"])
    for p_text in sec["paragraphs"]:
        add_paragraph(doc, p_text)
    add_table(doc, TABLE_5_6["headers"], TABLE_5_6["rows"], TABLE_5_6["widths"], TABLE_5_6["caption"])

    # 5.6
    sec = CHAPTER_5["sections"][5]
    add_heading1(doc, sec["heading"])
    for p_text in sec["paragraphs"]:
        add_paragraph(doc, p_text)

    doc.add_page_break()

    # ==========================================
    # CHAPTER 6: CONCLUSION
    # ==========================================
    add_chapter_heading(doc, 6, CHAPTER_6["title"])
    for sec in CHAPTER_6["sections"]:
        add_heading1(doc, sec["heading"])
        for p_text in sec["paragraphs"]:
            add_paragraph(doc, p_text)

    doc.add_page_break()

    # ==========================================
    # REFERENCES
    # ==========================================
    p_ref = doc.add_paragraph()
    p_ref.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ref.paragraph_format.space_before = Pt(14)
    p_ref.paragraph_format.space_after = Pt(16)
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
    # ANNEXURE A: PRODUCTION SOURCE CODE
    # ==========================================
    p_ax = doc.add_paragraph()
    p_ax.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ax.paragraph_format.space_before = Pt(14)
    p_ax.paragraph_format.space_after = Pt(12)
    r = p_ax.add_run("ANNEXURE A\nPRODUCTION SYSTEM SOURCE CODE")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True

    add_paragraph(doc, ANNEXURE_A_INTRO, space_after=8)
    add_code_block(doc, CODE_MODULE_1["code"], CODE_MODULE_1["title"])
    add_code_block(doc, CODE_MODULE_2["code"], CODE_MODULE_2["title"])
    add_code_block(doc, CODE_MODULE_3["code"], CODE_MODULE_3["title"])
    add_code_block(doc, CODE_MODULE_4["code"], CODE_MODULE_4["title"])
    add_code_block(doc, CODE_MODULE_5["code"], CODE_MODULE_5["title"])

    doc.add_page_break()

    # ==========================================
    # ANNEXURE B: 109-CLASS VOCABULARY CATALOG
    # ==========================================
    p_bx = doc.add_paragraph()
    p_bx.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_bx.paragraph_format.space_before = Pt(14)
    p_bx.paragraph_format.space_after = Pt(12)
    r = p_bx.add_run("ANNEXURE B\nCOMPLETE 109-CLASS ISL VOCABULARY CATALOG")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True

    add_paragraph(
        doc,
        "Table B.1 enumerates the complete vocabulary of 109 dynamic Indian Sign Language gesture classes "
        "supported by the deployed SignBridge AI ensemble model (`SBAI-MDL-ISL-4.0.0`). The catalog covers five "
        "core conversational domains: Greetings & Courtesies, Emergency & Medical, Daily Life & Family, "
        "Education & Workplace, and ISL Alphabets & Numerical Digits.",
        space_after=8
    )

    vocab_headers = ["Class ID", "Sign Label / Gloss", "Semantic Domain", "Dominant Kinematic Motion", "Clinical / Practical Utility"]
    vocab_widths = [0.9, 1.3, 1.4, 1.6, 1.25]
    add_table(doc, vocab_headers, VOCAB_CATEGORIES, vocab_widths, "Table B.1: Complete 109-Class ISL Vocabulary Catalog")

    doc.add_page_break()

    # ==========================================
    # ANNEXURE C: DEPLOYMENT RUNBOOK
    # ==========================================
    p_cx = doc.add_paragraph()
    p_cx.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cx.paragraph_format.space_before = Pt(14)
    p_cx.paragraph_format.space_after = Pt(12)
    r = p_cx.add_run("ANNEXURE C\nSYSTEM DEPLOYMENT RUNBOOK AND CONFIGURATION")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True

    for p_line in ANNEXURE_C_TEXT.strip().split("\n\n"):
        if p_line.startswith("C."):
            add_heading2(doc, p_line.split("\n")[0])
            for sub_p in p_line.split("\n")[1:]:
                add_paragraph(doc, sub_p, space_after=4)
        else:
            add_paragraph(doc, p_line, space_after=6)

    # Save Document
    docx_output_path = DELIVERABLES_DIR / "SignBridge_AI_Final_Project_Report.docx"
    doc.save(str(docx_output_path))
    print(f"Successfully generated DOCX report at: {docx_output_path}")
    return docx_output_path

if __name__ == "__main__":
    create_document()
