# CVMatchingAI — AI-Powered CV–Job Matching

A Streamlit application exploring how **NLP and semantic similarity** can support CV–job matching, skills-gap analysis and CV improvement recommendations.

## Features

- Compare a CV with a job description using TF-IDF and cosine similarity
- Optional multilingual semantic embeddings
- Identify skill gaps and generate recommendations
- Streamlit interface for interactive exploration
- Optional Groq-powered LLM assistance (requires your own API key)

## Technology

Python · Streamlit · scikit-learn · NLP · Sentence Transformers · Groq (optional)

## Local setup

1. Clone this repository.
2. Install Python dependencies: `pip install -r requirements.txt`
3. Start the app: `streamlit run app.py`

The core Streamlit application, matching modules, and automated tests are included. The original private CV datasets are intentionally not published. The optional Groq integration requires a personal API key.

## Data and privacy

The original CV datasets and any real candidate information are intentionally excluded from the public version. Use manually entered text or uploaded files in the app instead of the private dataset mode. Do not commit `.streamlit/secrets.toml`, API keys, uploaded CVs or private datasets. Use `.streamlit/secrets.toml.example` as a template when the configuration files are available.

## Author

**Noureddine Trabelsi** — Final-year AI Engineering Student, looking for a PFE internship starting February 2027.

[Portfolio](https://noureddine-portfolio-nine.vercel.app/) · [LinkedIn](https://www.linkedin.com/in/noureddine-trabelsi-9143b2218/)
