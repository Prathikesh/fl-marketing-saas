# Chapter 3 — Methodology and design

## 3.1 Dataset and rationale

The primary dataset is **Lead Scoring.csv** (9,240 leads, 37 raw columns, binary `Converted` label).
It was chosen after empirically rejecting alternatives: a 200k-row marketing-campaign dataset and
several brand datasets were tested and found to have feature-to-outcome correlations near zero — no
model could learn from them. Lead Scoring has genuine, if modest, predictive signal.

A deliberate decision was to **refuse leaky columns** (Tags, Lead Quality) that effectively encode the
answer. Using them inflates F1 toward 0.9+, but an examiner would correctly discount it. On the clean,
non-leaky feature set the accuracy ceiling is ~0.81 F1 across all model families — a property of the
data, established empirically in Chapter 5.

## 3.2 Tenant partitioning

Tenants are formed by splitting on **Lead Source**, giving five naturally heterogeneous clients:

| Tenant | Source | Rows | Conversion rate |
|--------|--------|-----:|----------------:|
| 0 | Google | 2,868 | 0.40 |
| 1 | Direct Traffic | 811 | 0.32 |
| 2 | Olark Chat | 1,755 | 0.26 |
| 3 | Organic Search | 1,154 | 0.38 |
| 4 | Reference | 534 | 0.92 |

This split is non-IID (conversion 26%→92%) and size-imbalanced (2,868 vs 534) with no synthetic skew.
To study cross-client gain, Direct Traffic is made **data-poor** by capping its training set to ~50
leads, simulating a new business. Each tenant is split train/validation/test (70/10/20).

## 3.3 Model and why it must be a neural network

The model is a feed-forward **multi-layer perceptron (MLP)**: input (79 encoded features) →
Linear(128) → ReLU → Dropout → Linear(64) → ReLU → Dropout → Linear(1), trained with
binary cross-entropy. The decision threshold is tuned on validation for F1 rather than fixed at 0.5.

Gradient-boosted trees usually outperform MLPs on tabular data, but the **framework requires a
differentiable, weight-based model**: FedAvg averages weights, DP-SGD perturbs gradients, and
continuous adaptation performs incremental gradient updates — none of which trees support. The MLP is
therefore a justified design constraint, not an oversight.

## 3.4 System architecture

The framework is organised as layers, each mapping to a proposal objective:

1. **Data pipeline** — ingest, clean, encode features, partition into tenants.
2. **Local training** — per-tenant model training.
3. **Federated aggregation server** — FedAvg (and robust variants), dropout tolerance, audit log.
4. **Privacy layer** — DP-SGD via Opacus.
5. **Delayed-label buffer** — registers predictions, matches real outcomes when they arrive.
6. **Continuous-adaptation layer** — incremental retraining on arrived labels.
7. **Personalization** — per-tenant head fine-tuning on the shared backbone.
8. **Serving** — FastAPI REST API and a React dashboard.

## 3.5 Experimental design

Each claim is tested by comparing the proposed system against a baseline, holding everything else
fixed:

| Claim | Comparison | Metric |
|-------|------------|--------|
| Accuracy at ceiling | federated vs centralized | F1 on pooled test |
| Cross-client gain | federated vs single-tenant isolated | per-tenant F1 |
| Personalization | personalized vs shared vs isolated | per-tenant F1 |
| Privacy | DP vs non-private | membership-inference advantage |
| Robustness | robust aggregation vs FedAvg under attack | F1 under poisoning |
| Fault tolerance | increasing tenant dropout | F1 vs dropout rate |
| Delayed feedback | adaptation vs static under drift | conversion-rate MAE |

Runs are seeded for reproducibility, and headline numbers are reported as mean ± standard deviation
over five seeds to account for training variance. Conversion-rate MAE is computed on the aggregate
conversion rate per tenant over the delay window, since the dataset has no native conversion-rate
column.

## 3.6 Honesty principle

Where results fall below the aspirational targets (F1 0.80 vs 0.82, cross-client gain 10% vs 15%),
they are reported as measured, with the reason. The thesis is defended on the comparative results and
the transparent treatment of assumptions (especially the concept-drift assumption behind the
delayed-feedback result and the measured-vs-nominal ε gap), not on inflated numbers.
