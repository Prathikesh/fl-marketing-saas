# Chapter 4 — Implementation

## 4.1 Technology stack

- **Python 3** with **PyTorch** for the model and training.
- **Opacus** for DP-SGD.
- **scikit-learn** for metrics (F1, ROC-AUC, confusion matrix) and the attack classifier.
- **FastAPI** + **Uvicorn** for the REST API.
- **React + Vite** for the dashboard.
- **pandas / NumPy** for the data pipeline; **matplotlib / seaborn** for the analysis notebook.

## 4.2 Package structure

The code is a `src/fl_marketing/` package with one area per layer:

```
src/fl_marketing/
  data/         ingest, features, loaders, tenant store, partitioning
  core/
    training/   local_trainer, losses
    privacy/    dp_engine (Opacus DP-SGD)
    federated/  client, server, aggregator, strategy, attacks, personalization
    adaptation/ delayed-label buffer, matcher, adapter
  models/       conversion_net (the MLP), registry
  evaluation/   metrics, privacy_attack
  api/          FastAPI app, routes (predict, feedback, audit, results)
```

Experiments are driven by scripts (`scripts/run_*.py`) and exposed as `make` targets; the React app
lives in `ui/`. Code comments are kept minimal by design — the explanation load is carried by the
documentation in `docs/`.

## 4.3 Key components

**Federated loop.** `FederatedServer.run()` holds the global state and, each round, selects
participating clients (applying dropout if configured), collects `ModelUpdate`s from
`FederatedClient.train_round()`, enforces a minimum-client quorum, and aggregates with a pluggable
aggregator (FedAvg by default). Every round is recorded in an audit log.

**Privacy.** When a client is given a privacy config, it trains through `dp_engine.dp_local_train`,
which wraps the model/optimizer/loader in an Opacus `PrivacyEngine`, trains with gradient clipping and
noise, and reports the spent ε.

**Robustness.** `aggregator.py` provides `coordinate_median` and `trimmed_mean` alongside `fedavg`;
`attacks.py` provides a `PoisoningClient` that returns negated, scaled weights to model an attacker.
The server's aggregator is a constructor parameter, so swapping the defence is a one-line change.

**Personalization.** `personalization.personalize_head` loads the shared global model, freezes all but
the final layer, and fine-tunes that layer on a tenant's own training data.

**Delayed feedback.** The `DelayedLabelBuffer` registers each prediction with an expected label-arrival
day; when real outcomes arrive they are matched by campaign id, and once enough accumulate the
adapter retrains incrementally at a low learning rate.

## 4.4 Serving

The FastAPI app loads the persisted global model (`models/global_model.pt`: weights, tuned threshold,
feature dimension) and exposes:

- `POST /predict` — encodes a lead, returns a calibrated probability and decision, and registers the
  lead in the delayed buffer.
- `POST /feedback` — supplies a real outcome, matched back in the buffer.
- `GET /audit` — federated rounds, DP status, pending predictions.
- `GET /results` — the measured benchmark results consumed by the dashboard.

The React dashboard (`ui/`) has three tabs — a live predictor, a research-results view, and an
ablation/overview view — fetching results live from `/results` with an embedded fallback.

## 4.5 MLOps and reproducibility

- **Reproducibility.** A single seed fixes Python, NumPy, and PyTorch RNGs; every experiment is
  config-driven (`config/default.yaml`, `config/experiment/`, `config/privacy/`).
- **Experiment tracking.** Each experiment is a `make` target with deterministic output; each
  federated run writes an audit log, and benchmark numbers are consolidated in
  `experiments/results/results.json`.
- **Model persistence.** The served artifact is saved and reloaded; the notebook verifies a reloaded
  model produces identical predictions.
- **Testing.** A unit-test suite (14 tests) covers aggregation (including the robust rules), dropout
  strategy, the DP engine, the buffer, delay logic, partitioning, and the local trainer.
- **Lifecycle.** Data → federated training → evaluation → persistence → serving → monitoring
  (delayed labels) → continuous adaptation → next training round, documented and diagrammed in the
  analysis notebook.

## 4.6 The analysis notebook

`notebooks/fl_marketing_complete.ipynb` is the end-to-end executable record: EDA, preprocessing, the
model and an architecture diagram, centralized vs federated training with confusion matrix and ROC,
every experiment, the MLOps lifecycle diagram, a summary table, and a conclusion — 54 cells, executed
with outputs embedded. It is regenerated with `make notebook`.
