from src.semantic import compare
from src.export_cv import make_docx

def test_skill_gap_without_model():
    result=compare('Python et SQL', 'Python SQL Docker',use_embeddings=False)
    assert 'docker' in result['not_detected_skills']
    assert result['skill_coverage'] == 2/3

def test_missing_text():
    import pytest
    with pytest.raises(ValueError):compare('', 'Python',False)

def test_docx_export():
    assert make_docx('Profil\nPython').startswith(b'PK')
