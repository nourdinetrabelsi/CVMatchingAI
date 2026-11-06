import pandas as pd
from src.engine import extract_skills,clean_input,rank_jobs,feedback

def test_skills_bilingual():
    assert {'python','machine learning','sql'} <= set(extract_skills('Python, SQL et apprentissage automatique'))

def test_clean_email():
    assert 'john@example.com' not in clean_input('john@example.com')

def test_title_only_is_not_compatibility():
    df=pd.DataFrame([{'title':'Python Developer','company':'A','job_description':''},{'title':'Accountant','company':'B','job_description':''}])
    r=rank_jobs('Python developer',df)
    assert r.iloc[0]['title']=='Python Developer'
    assert 'indicative' in r.iloc[0]['score_type']
    assert not feedback('Python',r.iloc[0])['skills_missing']
