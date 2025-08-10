# Superrepo: AI + Automation Monorepo

This monorepo showcases production-grade patterns across automation, RAG search, lightweight computer vision/ID matching, and a fast searchable Google Sheets front end.
Everything is runnable locally with mock data, and can be deployed to AWS as Lambdas or run as containers.

## Highlights

- **Automations (AWS Lambda-ready):** Three useful jobs with real logic and local mocks:
  - `drive_clean_up_assistant`: Finds large/duplicate files, proposes deletes, and optionally moves to an Archive.
  - `file_summary_broadcast`: Summarizes fresh files into rich Markdown and posts to Slack or email.
  - `personal_file_activity_digest`: Compiles a daily/weekly activity feed with anomaly hints.

- **RAG Service (FastAPI + FAISS):** Ingest PDFs/Markdown, chunk and embed, search semantically with graceful fallback if Sentence Transformers aren’t installed.

- **Computer Vision ID Match (OpenCV + Tesseract):** Extracts IDs from lab form images and sidecar labels, compares with simple heuristics and emits a confidence score.

- **Apps Script Front-End for Big Sheets:** A near-instant client-side search for large Sheets using indexed search and incremental loading.

## Quickstart

```bash
# Python environment
python3 -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -e ".[all]"  # see pyproject.toml extras

# Run RAG API
uvicorn rag.app:app --reload

# Try automations locally (mock mode)
python automations/drive_clean_up_assistant/handler.py --dry-run
python automations/file_summary_broadcast/handler.py --mock --out out.md
python automations/personal_file_activity_digest/handler.py --period daily

# Run CV matcher on sample images
python cv/id_matcher/run_match.py --form cv/id_matcher/sample/form_sample.png --label cv/id_matcher/sample/label_sample.png

# Apps Script
# See apps_script/README.md for steps to paste into Google Apps Script and bind to a Sheet.
```

## Deploy as AWS Lambdas

Each automation folder contains a `template.yaml` and `build.sh` for packaging. You can also use the included `Dockerfile.lambda` for reproducible builds.

## Dev Container

Open in VS Code with the included `.devcontainer/` to get Python, Tesseract, poppler-utils, and build tools pre-installed.

> This repo is intentionally modular and readable, with strong docstrings and type hints so reviewers can grok the architecture quickly.
