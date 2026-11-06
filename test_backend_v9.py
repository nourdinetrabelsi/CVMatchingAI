from src.backend import analyze
from src.training import recommend

def test_matching_and_training():
    report=analyze('Python SQL','Python SQL Docker')
    assert 'docker' in report['not_detected_skills']
    assert any(row[0]=='docker' for row in report['training'])

def test_no_invented_skills():
    report=analyze('Python', 'Python')
    assert report['not_detected_skills']==[]
    assert recommend([])==[]
