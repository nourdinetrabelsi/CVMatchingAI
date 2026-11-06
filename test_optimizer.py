from unittest.mock import patch, Mock
from src.llm import generate

def test_optimizer_prompt_and_groq_endpoint():
    response=Mock(status_code=200)
    response.json.return_value={'choices':[{'message':{'content':'PROFIL\nPython'}}]}
    with patch('src.llm.requests.post',return_value=response) as post:
        result=generate('Python','Offre: Python et Docker',task='optimizer',api_key='test-key')
    assert 'PROFIL' in result
    data=post.call_args.kwargs['json']
    assert 'Do not add missing skills' in data['messages'][1]['content']
    assert post.call_args.args[0]=='https://api.groq.com/openai/v1/chat/completions'

def test_optimizer_requires_key():
    with patch.dict('os.environ',{'GROQ_API_KEY':''}):
        try: generate('CV','Offre',task='optimizer')
        except ValueError as error: assert 'Clé API' in str(error)
        else: assert False
