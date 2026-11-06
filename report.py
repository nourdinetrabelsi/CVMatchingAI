"""DOCX matching report, based only on observed results."""
from io import BytesIO
from docx import Document

def matching_docx(title, matched, missing, coverage, note):
    d=Document()
    d.add_heading('CVMatchingAI — Rapport de correspondance',0)
    d.add_paragraph('Poste : '+str(title or 'Non précisé'))
    d.add_paragraph('Couverture des compétences détectées : '+(f'{coverage:.0%}' if coverage is not None else 'Non calculable'))
    d.add_heading('Compétences communes',level=2)
    d.add_paragraph(', '.join(matched) if matched else 'Aucune détectée')
    d.add_heading('Compétences non détectées dans le CV',level=2)
    d.add_paragraph(', '.join(missing) if missing else 'Aucune détectée')
    d.add_paragraph(note)
    d.add_paragraph('Ce rapport ne constitue pas une décision de recrutement.')
    output=BytesIO();d.save(output);return output.getvalue()
