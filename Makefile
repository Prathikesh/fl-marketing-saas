.PHONY: install dev prepare train baseline evaluate privacy serve test lint format

install:
	pip install -r requirements.txt && pip install -e .

dev:
	pip install -r requirements-dev.txt && pip install -e .

prepare:
	python scripts/prepare_data.py

train:
	python scripts/run_federated.py

baseline:
	python scripts/run_baseline.py

evaluate:
	python scripts/run_evaluation.py

privacy:
	python scripts/run_privacy_attack.py

serve:
	python scripts/serve_api.py

test:
	pytest

lint:
	ruff check src tests scripts

format:
	black src tests scripts
