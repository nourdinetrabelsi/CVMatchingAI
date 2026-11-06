"""Conservative bilingual CV analysis and grounded enhancement suggestions."""
import re
from .engine import clean_input, extract_skills

HEADINGS = {
 'summary':r'\b(profile|profil|summary|résumé professionnel|professional summary|objective|objectif)\b',
 'experience':r'\b(expérience|experience|employment|work history|parcours professionnel)\b',
 'education':r'\b(education|éducation|formation|dipl[oô]me|degree|university|université)\b',
 'skills':r'\b(compétences|skills|technologies|technical skills|outils)\b',
 'projects':r'\b(projets|projects|portfolio|réalisations)\b',
}

def analyze_cv(text):
    text = str(text or '').strip()
    if not text:
        raise ValueError('CV vide')
    sections={name:bool(re.search(pattern,text,re.I)) for name,pattern in HEADINGS.items()}
    skills=extract_skills(text)
    suggestions=[]
    for name,label in [('summary','résumé professionnel'),('experience','expériences'),('education','formation'),('skills','compétences')]:
        if not sections[name]:
            suggestions.append(f'Vérifier et, si pertinent, ajouter une section « {label} » clairement identifiée.')
    if not sections['projects']:
        suggestions.append('Si vous avez des projets vérifiables, les présenter avec votre rôle et les résultats obtenus.')
    if len(text.split())<120:
        suggestions.append('CV court : détailler les expériences et réalisations réelles si elles existent.')
    if not re.search(r'\b\d+(?:[.,]\d+)?\s*(?:%|percent|pourcent|users|utilisateurs|clients|hours|heures)\b',text,re.I):
        suggestions.append('Ajouter des résultats chiffrés uniquement si vous disposez de chiffres vérifiables.')
    if not skills:
        suggestions.append('Préciser les outils et compétences effectivement utilisés : le dictionnaire actuel n’en a reconnu aucun.')
    return {'skills':skills,'sections':sections,'suggestions':suggestions,
            'clean_preview':clean_input(text),
            'note':'Diagnostic heuristique : une section non reconnue peut exister sous un autre intitulé.'}

def compare_to_offer(cv_text, job_description):
    """Unknown requirements are not considered missing skills."""
    if not str(job_description or '').strip():
        return {'available':False,'matched':[],'not_detected':[], 'note':'Description de poste absente : analyse des écarts indisponible.'}
    required=set(extract_skills(job_description))
    present=set(extract_skills(cv_text))
    return {'available':True,'matched':sorted(required & present),'not_detected':sorted(required-present),
            'note':'Non détecté dans le CV ne signifie pas non maîtrisé. Confirmer avec le candidat.'}

def improvement_plan(not_detected):
    return [{'skill':s,'actions':[f'Confirmer si vous maîtrisez déjà {s} : si oui, ajouter une preuve concrète au CV.',
                                   f'Sinon, suivre une formation et réaliser un projet pratique en {s} avant de le mentionner comme acquis.']} for s in not_detected]
