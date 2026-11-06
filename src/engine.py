"""CVMatchingAI: transparent bilingual baseline; no invented job requirements."""
import ast
import re
import unicodedata
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SKILLS = {
 'python':['python'], 'sql':['sql','postgresql','mysql'], 'excel':['excel'],
 'power bi':['power bi','powerbi'], 'tableau':['tableau'],
 'java':['java'], 'javascript':['javascript','js'], 'typescript':['typescript'],
 'react':['react','reactjs'], 'angular':['angular'], 'node.js':['node.js','nodejs'],
 'django':['django'], 'flask':['flask'], 'fastapi':['fastapi'],
 'machine learning':['machine learning','apprentissage automatique'],
 'deep learning':['deep learning','apprentissage profond'],
 'nlp':['nlp','traitement automatique du langage'], 'pytorch':['pytorch'],
 'tensorflow':['tensorflow'], 'docker':['docker'], 'kubernetes':['kubernetes'],
 'aws':['aws'], 'azure':['azure'], 'git':['git'], 'linux':['linux'],
 'communication':['communication'], 'project management':['project management','gestion de projet'],
 'marketing':['marketing'], 'sales':['sales','vente','ventes'],
 'accounting':['accounting','comptabilite','comptabilité'],
 'finance':['finance'], 'recruitment':['recruitment','recrutement'],
 'customer service':['customer service','service client'],
 'data analysis':['data analysis','analyse de données','analyse des donnees']
}

def norm(text):
    return unicodedata.normalize('NFKC', str(text or '')).lower()

def extract_skills(text):
    t=norm(text)
    return sorted({key for key, variants in SKILLS.items() if any(re.search(r'(?<!\w)'+re.escape(v)+r'(?!\w)',t) for v in variants)})

def clean_input(text):
    text=re.sub(r'\b[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}\b','[EMAIL]',str(text))
    text=re.sub(r'(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)','[PHONE]',text)
    return re.sub(r'\s+',' ',text).strip()

def load_jobs(path):
    df=pd.read_csv(path,low_memory=False).fillna('')
    required={'title','company','job_description'}
    if not required.issubset(df.columns):
        raise ValueError('Colonnes jobs manquantes: '+str(required-set(df.columns)))
    return df

def rank_jobs(cv_text,jobs,limit=10,model='tfidf'):
    """If descriptions are absent, score is a title relevance proxy, NOT CV-job compatibility."""
    if not cv_text or not cv_text.strip():
        raise ValueError('CV vide')
    jobs=jobs.copy()
    has_desc=jobs['job_description'].astype(str).str.strip().ne('')
    full=bool(has_desc.all())
    corpus=(jobs['title'].fillna('')+' '+jobs['job_description'].fillna('')).tolist()
    if model=='embeddings':
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError('Installer sentence-transformers pour les embeddings') from exc
        encoder=SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        vec=encoder.encode([cv_text]+corpus,normalize_embeddings=True,show_progress_bar=False)
        scores=vec[1:]@vec[0]
    else:
        vect=TfidfVectorizer(ngram_range=(1,2),max_features=35000,sublinear_tf=True,strip_accents='unicode')
        matrix=vect.fit_transform([cv_text]+corpus)
        scores=cosine_similarity(matrix[0],matrix[1:]).ravel()
    jobs['relevance_score']=scores.round(4)
    jobs['score_type']='similarité CV–offre' if full else 'pertinence textuelle indicative (descriptions manquantes)'
    return jobs.nlargest(limit,'relevance_score')

def feedback(cv_text,job_row):
    present=set(extract_skills(cv_text))
    desc=str(job_row.get('job_description','') or '')
    required=set(extract_skills(desc)) if desc.strip() else set()
    if not required:
        return {'skills_detected':sorted(present),'skills_matched':[], 'skills_missing':[], 'note':'Exigences non disponibles : impossible de conclure sur les compétences manquantes.'}
    return {'skills_detected':sorted(present),'skills_matched':sorted(required & present),'skills_missing':sorted(required-present),'note':'Suggestions fondées uniquement sur les compétences explicitement détectées dans la description.'}
