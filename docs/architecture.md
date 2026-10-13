# Architecture

The framework is organised into six layers plus a REST service interface. Each layer has a
single responsibility and a defined interface, so a change in one layer does not break the others.

## Layer map

| # | Layer | Package path | Key files | Responsibility |
|---|-------|--------------|-----------|----------------|
| 1 | Tenant Data Layer | `src/fl_marketing/data/` | `tenant.py`, `partition.py` | Isolate each tenant's data; prepare training batches. No raw data crosses the tenant boundary. |
| 2 | Local Training Module | `src/fl_marketing/core/training/` | `local_trainer.py` | Train the model on one tenant's data; output model updates only. |
| 3 | Privacy Enforcement Layer | `src/fl_marketing/core/privacy/` | `dp_engine.py`, `accountant.py` | Add calibrated noise to updates (DP-SGD); track the privacy budget. |
| 4 | Federated Aggregation Server | `src/fl_marketing/core/federated/` | `server.py`, `aggregator.py`, `strategy.py` | Combine tenant updates with FedAvg; tolerate dropout. |
| 5 | Delayed Label Buffer | `src/fl_marketing/core/adaptation/` | `buffer.py`, `matcher.py` | Register predictions; match real conversion results when they arrive. |
| 6 | Continuous Adaptation Layer | `src/fl_marketing/core/adaptation/` | `adapter.py` | Incrementally retrain from newly arrived results without forgetting. |
| - | Service Interface (REST) | `src/fl_marketing/api/` | `main.py`, `routes/` | Prediction, result submission, and audit endpoints. |

Supporting modules: `models/` (the neural network), `baselines/` (the two comparison systems),
`evaluation/` (metrics and the privacy attack), `audit/` (round logging), `persistence/`
(SQLite for the buffer and audit log), and `utils/` (seeding, logging, the simulated clock).

## The model

A single feedforward neural network (`models/conversion_net.py`) is used everywhere: inside each
tenant, inside the global model, in both baselines, and in the privacy shadow models. It predicts
conversion from the tabular lead features. Architecture: input -> 128 -> 64 -> 1, ReLU with
dropout, trained with `BCEWithLogitsLoss`.

Local training lives in `core/training/local_trainer.py`: `local_train` runs the per-tenant
optimisation loop and returns a `ModelUpdate` (state dict + sample count + tenant id);
`predict_proba` returns probabilities and targets for evaluation. `scripts/sanity_check.py`
trains centrally on the pooled tenants to confirm the data has learnable signal before federation
and privacy are added.

## Data flow

```
data/raw
  -> ingest -> harmonize -> features -> labels -> delay -> partition
  -> data/processed (one dataset per tenant)
  -> federated client: local_trainer -> privacy/dp_engine
  -> aggregator (FedAvg) -> global model
  -> api/predict -> delayed label buffer (waits in simulated time)
  -> api/feedback -> buffer/matcher -> adaptation/adapter -> next round
  -> evaluation/metrics + privacy_attack -> experiments/results
```

## Design rules

- All tunable values live in `config/`, never hard-coded.
- `scripts/` only parse arguments and call the package; they contain no logic.
- Raw data never enters version control; only the data dictionary and the pipeline code do.
- Every core module has a matching test under `tests/`.
