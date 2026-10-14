.PHONY: install dev prepare train baseline evaluate personalize delayed privacy epsilon serve ui-install ui test lint format

export PYTHONPATH := src

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

personalize:
	python scripts/run_personalization.py

delayed:
	python scripts/run_delayed_feedback.py

privacy:
	python scripts/run_privacy_attack.py

epsilon:
	python scripts/run_epsilon_sweep.py

serve:
	python scripts/serve_api.py

ui-install:
	cd ui && npm install

ui:
	cd ui && npm run dev

test:
	pytest

lint:
	ruff check src tests scripts

format:
	black src tests scripts
