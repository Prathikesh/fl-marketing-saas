.PHONY: install dev prepare train baseline evaluate personalize delayed privacy epsilon faults robust commcost notebook serve ui-install ui test lint format

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

faults:
	python scripts/run_fault_tolerance.py

robust:
	python scripts/run_robustness.py

commcost:
	python scripts/run_comm_cost.py

notebook:
	jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=400 notebooks/fl_marketing_complete.ipynb

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
