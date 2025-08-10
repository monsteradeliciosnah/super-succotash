.PHONY: fmt lint test rag automations

fmt:
	black .
	ruff --fix . || true

lint:
	ruff .

test:
	pytest -q

rag:
	uvicorn rag.app:app --reload

automations:
	python automations/drive_clean_up_assistant/handler.py --dry-run
	python automations/file_summary_broadcast/handler.py --mock --out out.md
	python automations/personal_file_activity_digest/handler.py --period daily
