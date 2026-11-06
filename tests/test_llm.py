import pytest
from src.llm import generate

def test_missing_key(monkeypatch):
    monkeypatch.delenv('GROQ_API_KEY',raising=False)
    with pytest.raises(ValueError,match='Clé API'):
        generate('CV test')

def test_non_https():
    with pytest.raises(ValueError,match='Groq'):
        generate('CV test',api_key='dummy',endpoint='http://example.org/v1')
