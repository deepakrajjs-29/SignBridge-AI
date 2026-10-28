import docx
from docx.oxml import parse_xml
import win32com.client
import os

doc = docx.Document()
p = doc.add_paragraph("Equation 3.1:")
xml_snippet = '<m:oMathPara xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"><m:oMath><m:r><m:t>p′_k = p_k - p_wrist</m:t></m:r></m:oMath></m:oMathPara>'
p._p.append(parse_xml(xml_snippet))

test_docx = os.path.abspath("Final_Report_Deliverables/Supporting_Files/test_math.docx")
test_pdf = os.path.abspath("Final_Report_Deliverables/Supporting_Files/test_math.pdf")
doc.save(test_docx)

word = win32com.client.Dispatch("Word.Application")
word.Visible = False
try:
    d = word.Documents.Open(test_docx)
    d.ExportAsFixedFormat(test_pdf, 17)
    d.Close(False)
    print("Word converted OMML to PDF successfully! PDF size:", os.path.getsize(test_pdf))
finally:
    word.Quit()
