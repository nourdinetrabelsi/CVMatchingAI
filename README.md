# CVMatchingAI — AI-powered CV & Job Matching

[![Python tests](https://github.com/nourdinetrabelsi/CVMatchingAI/actions/workflows/tests.yml/badge.svg)](https://github.com/nourdinetrabelsi/CVMatchingAI/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)

A **Streamlit** application to analyze CVs, compare a candidate profile with job descriptions, identify skill gaps, and optionally generate tailored CV text and career guidance using the **Groq API**.

**[Explore the project on my portfolio](https://noureddine-portfolio-nine.vercel.app/projects/cvmatchingai)** · **[GitHub Actions test results](https://github.com/nourdinetrabelsi/CVMatchingAI/actions/workflows/tests.yml)**

## Features

- Import a CV as **PDF, DOCX, or TXT**, or paste its text directly.
- Extract and compare explicitly mentioned skills against a job description.
- Rank jobs with **TF-IDF + cosine similarity**, with optional multilingual sentence embeddings.
- Generate an editable, targeted CV and career guidance using Groq, **only after explicit consent**.
- Export generated text in supported formats and explore training suggestions.
- Run local analysis without a Groq API key.

> **Interpretation:** similarity scores measure indicative text relevance, **not hiring probabilities**. Missing job descriptions limit skill-gap analysis. A skill not detected in a CV is not proof that the candidate lacks it.

## Technology

Python · Streamlit · pandas · scikit-learn · TF-IDF · cosine similarity · optional Sentence-Transformers · PyMuPDF · python-docx · Groq API

## Quick start

Python 3.11 is recommended.

```bash
git clone https://github.com/nourdinetrabelsi/CVMatchingAI.git
cd CVMatchingAI
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Optional multilingual semantic matching:

```bash
python -m pip install sentence-transformers
```

## Try it without private data

Use a **synthetic** CV and job description to explore the app safely.

**Example CV:**

```text
Junior Data Analyst
Projects: Python and SQL data analysis; Power BI sales dashboard.
Skills: Python, SQL, Power BI, Git.
```

**Example job description:**

```text
Data Analyst internship. Required skills: Python, SQL, Power BI, Docker.
```

The baseline skill extractor should identify Python, SQL and Power BI in both texts, while Docker is not detected in the sample CV. This is a demonstration of keyword extraction, not a judgment of candidate competence.

## Groq configuration (optional)

Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and add **your own** API key. Never commit keys or real CVs. The app requests consent before transmitting CV/job text to Groq. The local matching mode does not require an API key.

## Data and privacy

The original project's `data/` CSV datasets are intentionally **excluded** because they may contain personal information. The dataset-selection feature requires a local `data/cv_clean.csv` with `cv_id` and `clean_text` columns; use file upload or pasted text for the public demo.

Only process CVs you have permission to use. Generated recommendations must be reviewed by a human and must not invent qualifications.

## Tests

```bash
python -m pytest -q
```

**Local review (6 November 2026):** 18 tests passed on the available project source. This does not establish model accuracy or guarantee that a hosted deployment will work. The badge above reflects the GitHub Actions workflow's status when GitHub makes it available.

## Repository layout

```text
CVMatchingAI/
├── app.py
├── requirements.txt
├── src/
│   ├── backend.py
│   ├── engine.py
│   ├── semantic.py
│   ├── llm.py
│   ├── training.py
│   └── export_cv.py
├── tests/
└── .streamlit/
    ├── config.toml
    └── secrets.toml.example
```

## Demo and screenshots

**[Project presentation](https://noureddine-portfolio-nine.vercel.app/projects/cvmatchingai)**

A publicly accessible Streamlit deployment is **not yet confirmed**. To produce genuine screenshots, run `streamlit run app.py` and capture the interface with synthetic CV data. Do not include API keys, real candidate CVs, or private information in screenshots.

## Limitations

- The project is a portfolio demonstration, **not a validated recruitment decision system**.
- TF-IDF and skill extraction are limited by the available text and vocabulary.
- Optional embeddings download a model on first use.
- Groq access depends on API key, quota and model availability.
- Real datasets and candidate documents are intentionally excluded from this public repository.

## Author

**Noureddine Trabelsi** — Final-year AI Engineering Student in Tunisia, seeking a 4–6 month PFE internship starting February 2027.

[Portfolio](https://noureddine-portfolio-nine.vercel.app/) · [LinkedIn](https://www.linkedin.com/in/noureddine-trabelsi-9143b2218/) · [GitHub](https://github.com/nourdinetrabelsi)
