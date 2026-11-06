from src.profile import extract_profile
from src.history import save_analysis, list_analyses, clear_analyses
from src.report import matching_docx

def test_profile_sections():
    p=extract_profile('Formation\nLicence informatique\nCompétences\nPython SQL\nProjets\nAnalyse de données')
    assert 'python' in p['skills'] and 'sql' in p['skills']
    assert p['sections']['formation']=='Licence informatique'
    assert 'Analyse' in p['sections']['projects']

def test_history(tmp_path):
    path=tmp_path/'history.sqlite3'
    save_analysis(path,'CV-demo','Data Scientist',['python'],['docker'],0.5)
    rows=list_analyses(path)
    assert len(rows)==1 and rows[0]['poste']=='Data Scientist'
    clear_analyses(path)
    assert not list_analyses(path)

def test_docx_report():
    data=matching_docx('Analyste',['python'],['sql'],0.5,'Test')
    assert data[:2]==b'PK'
