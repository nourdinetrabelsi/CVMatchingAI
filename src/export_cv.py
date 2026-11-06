"""Create an editable DOCX without silently adding unverified credentials."""
from io import BytesIO
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def make_docx(text: str, heading: str = 'CV — brouillon à vérifier') -> bytes:
    doc = Document()
    normal = doc.styles['Normal']
    normal.font.name = 'Aptos'
    normal.font.size = Pt(10.5)
    section = doc.sections[0]
    section.top_margin = Inches(.75)
    section.bottom_margin = Inches(.7)
    section.left_margin = Inches(.85)
    section.right_margin = Inches(.85)
    if heading.strip(): doc.add_heading(heading, 0)
    lines = [line.strip() for line in text.splitlines()]
    first = True
    for line in lines:
        if not line: continue
        is_bullet = line.startswith(('-', '•', '*'))
        is_header = (len(line) < 52 and line.upper() == line and any(c.isalpha() for c in line) and not is_bullet)
        if first:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(line)
            run.bold = True
            run.font.size = Pt(17)
            run.font.color.rgb = RGBColor(16, 40, 64)
            first = False
        elif is_header:
            p = doc.add_paragraph(style='Heading 2')
            p.add_run(line)
        elif is_bullet:
            doc.add_paragraph(line.lstrip('-•* '), style='List Bullet')
        else:
            doc.add_paragraph(line)
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.add_run('CVMatchingAI · Document à vérifier avant envoi').font.size = Pt(8)
    output = BytesIO()
    doc.save(output)
    return output.getvalue()
