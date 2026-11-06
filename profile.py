"""Conservative, explainable extraction of a CV profile."""
import re
from .engine import extract_skills

HEADINGS = {
    'skills': ('compétences','competences','skills','technical skills'),
    'formation': ('formation','education','academic background','études','etudes'),
    'experience': ('expérience','experience','work history','employment'),
    'projects': ('projets','projects','portfolio'),
    'languages': ('langues','languages'),
    'summary': ('profil','profile','summary','résumé professionnel'),
}

def extract_profile(cv):
    text = str(cv or '')
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    sections = {}
    current = None
    for line in lines:
        key = line.lower().rstrip(':').strip()
        match = next((name for name, aliases in HEADINGS.items() if key in aliases), None)
        if match:
            current = match
            sections.setdefault(match, [])
        elif current:
            sections[current].append(line)
    return {
        'skills': extract_skills(text),
        'sections': {name: '\n'.join(values) for name, values in sections.items()},
        'email_detected': bool(re.search(r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b', text)),
        'language_hint': 'fr' if re.search(r'\b(formation|compétences|expérience|projets)\b', text, re.I) else 'indéterminée',
        'note': 'Extraction heuristique. Les compétences mentionnées et les sections ne sont pas des faits vérifiés.'
    }
