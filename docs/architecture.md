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

## Federation

`core/federated/` runs the federated loop (`scripts/run_federated.py`). Each round: the server
sends the current global weights to every `FederatedClient`, each client runs `local_train` on its
tenant's data and returns a `ModelUpdate`, and the server combines them with `fedavg` (weighted by
each tenant's sample count). `strategy.py` handles client selection and dropout tolerance.

Observed behaviour: the federated model reaches about 0.77-0.78 F1 on the pooled test set, a few
points below the centralized ceiling (~0.80). This gap is the expected non-IID penalty: the tenants
have very different conversion rates (26% to 92%), which is the data-heterogeneity challenge of
federated averaging. The data-poor, high-converting Reference tenant benefits most from the shared
model, which is the effect the cross-client-gain evaluation measures.

FedProx: `local_train` supports a proximal term (controlled by `federated.mu`) as an optional
mitigation for client drift. It was evaluated here and did not improve pooled accuracy (mu=0 was
best; larger mu lowered F1), because the tenants genuinely differ and constraining them toward the
global model removes useful specialisation. It is kept as a configurable ablation; the default is
`mu: 0.0` (plain FedAvg).

## Privacy (DP-SGD)

`core/privacy/dp_engine.py` provides `dp_local_train`, which wraps local training with Opacus so
each tenant's update is produced under differential privacy (gradient clipping + Gaussian noise).
A client uses this path when `run_federated.py` is run with `--private`; the noise multiplier,
clipping norm and delta come from the `privacy` config.

Observed cost: with the default noise, the global pooled F1 falls from about 0.77 to about 0.73,
and the hardest small tenant (Olark Chat) drops the most. This is the expected privacy-accuracy
trade-off.

Epsilon accounting: `dp_local_train` reports the epsilon for a single round's local training (a
fresh accountant per round). The cumulative budget across all rounds is higher, so a strict total
epsilon <= 1.0 over full training is only reachable with much more noise (and lower F1). The
privacy-accuracy trade-off is characterised properly in the epsilon sweep (evaluation stage), and
the operational privacy guarantee is validated empirically by the membership inference attack.

## Delayed label buffer

`core/adaptation/buffer.py` holds the `DelayedLabelBuffer`. When a prediction is made it is
registered with the campaign id, the day it was made and the day its real label is expected to
arrive (`launch_day + 7..30`). A simulated clock advances; `due(current_day)` returns predictions
whose label has arrived. When the real outcome comes in, `matcher.match_label` calls `fulfill`,
which records the true label. `fulfilled_count` tracks how many real labels a tenant has
accumulated; once that reaches the adaptation threshold, `drain_fulfilled` hands them to the
Continuous Adaptation Layer and marks them consumed. Each lead carries a stable `campaign_id`
(added by the data pipeline) so labels match back to the right prediction.

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
