"""Application service layer: UI never calls Groq directly."""
from .semantic import compare
from .llm import generate
from .training import recommend


def analyze(cv, offer):
    result = compare(cv, offer, use_embeddings=False)
    result['training'] = recommend(result['not_detected_skills'])
    return result


def optimize(cv, offer, key, model=None):
    return generate(cv, offer, task='optimizer', api_key=key, model=model)


def coach(cv, offer, key, model=None):
    return generate(cv, offer, task='coach', api_key=key, model=model)
