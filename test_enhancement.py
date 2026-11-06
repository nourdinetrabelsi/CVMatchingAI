from src.enhancement import analyze_cv, compare_to_offer, improvement_plan

def test_cv_analysis():
    out=analyze_cv('Compétences: Python et SQL. Expérience en analyse de données. Formation en informatique.')
    assert 'python' in out['skills'] and 'sql' in out['skills']

def test_no_invented_requirements():
    gap=compare_to_offer('Python et SQL','')
    assert not gap['available'] and gap['not_detected']==[]

def test_skill_gap():
    gap=compare_to_offer('Python et SQL','Python, Docker, SQL')
    assert gap['not_detected']==['docker']
    assert improvement_plan(gap['not_detected'])[0]['skill']=='docker'
