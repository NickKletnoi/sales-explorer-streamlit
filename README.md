# Sales Explorer (Streamlit)

A small Streamlit dashboard with sidebar filters, summary metrics,
a line chart, a data table, and CSV download. It generates its own
sample data, so it runs with no setup beyond installing dependencies.

## Run locally

    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    streamlit run app.py

Opens at http://localhost:8501

## Deploy

**Streamlit Community Cloud (free):** push this repo to GitHub, sign in at
https://share.streamlit.io, click "Create app", pick this repo and `app.py`,
then Deploy.

**Docker:**

    docker build -t sales-explorer .
    docker run -p 8501:8501 sales-explorer

The image works on Cloud Run, AWS App Runner/ECS, Azure Container Apps,
Fly.io, Render, Railway, or any VM with Docker. Make sure WebSocket
support is enabled on your host.

## Secrets

Put API keys in `.streamlit/secrets.toml` locally (already git-ignored)
or in your platform's secrets/environment settings. Never commit them.
