# Publish a live demo on Streamlit Community Cloud

This repository contains a Streamlit app. The public deployment has **not yet been created**.

1. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub.
2. Select **Create app** → **Deploy a public app from GitHub**.
3. Repository: `nourdinetrabelsi/CVMatchingAI`; branch: `main`; entrypoint: `app.py`.
4. Select a Python version compatible with `requirements.txt` (Python 3.11 recommended).
5. Deploy and test the application using **synthetic** CV and job descriptions.
6. For a public demo, keep Groq optional. If you choose to use a personal key, set it in Streamlit's **Secrets** interface; never commit `.streamlit/secrets.toml`.
7. After verifying the app works, add the exact public `https://…streamlit.app/` URL to `README.md`, your GitHub profile and your portfolio.

## Capture real screenshots

After launching the app locally or on Streamlit Cloud, take screenshots of:
- The landing screen with no personal information.
- A synthetic CV and job-description comparison.
- The explanation of skills detected and not detected.

Save the images in `docs/screenshots/`, commit them and reference them in `README.md`. Never use real candidates' CVs, private datasets, API keys or browser credentials in screenshots.

## Troubleshooting

- Check [GitHub Actions](https://github.com/nourdinetrabelsi/CVMatchingAI/actions/workflows/tests.yml) for Python test results.
- If the app reports a missing data file, use **Paste a CV** or **Import a file** instead of the private dataset mode.
- If multilingual embeddings fail to import, install the optional `sentence-transformers` dependency; the default local mode does not require it.
- Groq is optional; test the local features first.

**Do not advertise a public demo link until you have confirmed it works.**
