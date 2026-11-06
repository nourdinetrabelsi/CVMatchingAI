"""Multilingual CV–job matching with explicit data-quality safeguards."""
from functools import lru_cache
import numpy as np
from .engine import extract_skills

MODEL = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'

@lru_cache(maxsize=1)
def get_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(MODEL)

def compare(cv_text: str, offer_text: str, use_embeddings: bool = True):
    if not cv_text.strip() or not offer_text.strip():
        raise ValueError('Le CV et la description de poste sont obligatoires.')
    cv_skills, offer_skills = set(extract_skills(cv_text)), set(extract_skills(offer_text))
    common = sorted(cv_skills & offer_skills)
    absent = sorted(offer_skills - cv_skills)
    coverage = len(common) / len(offer_skills) if offer_skills else None
    similarity = None
    if use_embeddings:
        vectors = get_model().encode([cv_text[:12000], offer_text[:12000]], normalize_embeddings=True, show_progress_bar=False)
        similarity = float(np.clip(np.dot(vectors[0], vectors[1]), -1, 1))
    return {'semantic_similarity': similarity, 'skill_coverage': coverage,
            'matched_skills': common, 'not_detected_skills': absent,
            'offer_skills': sorted(offer_skills),
            'warning': 'La similarité n’est pas une probabilité d’embauche. Non détecté ne signifie pas non maîtrisé.'}
