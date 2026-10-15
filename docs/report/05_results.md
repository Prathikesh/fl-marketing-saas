# Chapter 5 — Results and evaluation

All numbers below are measured and reproducible via the stated `make` target. Figures are generated in
the analysis notebook.

## 5.1 Accuracy: federated vs centralized

The centralized model (all data pooled — the upper bound) and the federated model were trained on the
same splits.

| Model | Pooled test F1 | ROC-AUC |
|-------|---------------:|--------:|
| Centralized (upper bound) | ~0.77–0.80 | ~0.90 |
| Federated (FedAvg) | **0.7872** | — |

Over five seeds the federated model scores **0.788 ± 0.003**. The federated model is within a few
points of — and in some seeds matches — the centralized model, i.e. federation costs very little
accuracy while removing all data sharing. `make train`.

## 5.2 The accuracy ceiling is data-bound (model-strengthening ablation)

Every attempt to strengthen the model was measured against the baseline on the pooled test set. None
beat it.

| Change | Pooled F1 | Verdict |
|--------|----------:|---------|
| **Baseline model (kept)** | **0.7872** | best |
| Class-weighted loss | 0.7665 | worse |
| LayerNorm architecture | 0.7692 | worse |
| Cosine LR schedule | 0.7584 | worse |
| 25 rounds | 0.7829 | worse |
| 40 rounds | 0.7798 | worse |
| FedProx μ = 0.1 | 0.7851 | worse |
| 5-seed ensemble | 0.7892 | flat |

The seed-to-seed spread (0.783–0.791) is larger than any change above. This is direct evidence that
accuracy is **bounded by the data, not the model** — the central honesty argument of the thesis. The
MLP is kept as-is; FedProx is retained only as a configurable ablation (default μ=0, plain FedAvg).

## 5.3 Cross-client gain

Each tenant's federated F1 is compared with an isolated single-tenant model trained only on its own
data. `make evaluate`.

The **data-poor tenant (Direct Traffic)** gains roughly **+10%** F1 from federation (e.g. 0.648
isolated → 0.713 federated), confirming that collaboration helps most the tenant that most needs it.
Well-resourced or easy tenants benefit little or not at all — itself a finding about *when*
cross-tenant learning helps. The aspirational +15% target was not reached; the honest measured gain is
~10%.

## 5.4 Personalization removes negative transfer

A shared federated backbone with a per-tenant fine-tuned head. `make personalize`.

| Tenant | Isolated | Shared federated | Personalized |
|--------|---------:|-----------------:|-------------:|
| Google | 0.7848 | 0.8063 | 0.8078 |
| Direct Traffic (data-poor) | 0.6476 | 0.7126 | 0.7048 |
| Olark Chat | 0.7126 | **0.6961** | **0.7225** |
| Organic Search | 0.7528 | 0.7692 | 0.7676 |
| Reference | 0.9608 | 0.9608 | 0.9608 |

Under the shared model, Olark Chat is *worse* than training alone (0.696 < 0.713) — negative transfer.
Personalization recovers it (0.7225), so **every tenant ends at least as good as its isolated model**,
while the data-poor tenant keeps its large gain. (Its personalized score is marginally below shared
because fine-tuning a head on only ~50 capped leads slightly overfits — an honest, explainable
nuance.)

## 5.5 Privacy vs accuracy (ε sweep)

DP-SGD at several noise levels, with the membership-inference advantage measured by the same
shadow-model attack. `make epsilon` / `make privacy`.

| Setting | Noise mult. | ε / round | Federated F1 | MI advantage |
|---------|------------:|----------:|-------------:|-------------:|
| Non-private | — | ∞ | 0.7872 | +4.0% |
| Strong | 1.6 | 2.18 | 0.7249 | −0.3% |
| Medium | 1.1 | 3.83 | 0.7252 | +0.1% |
| Weak | 0.8 | 6.71 | 0.7331 | +0.3% |

Differential privacy costs ~5–6 F1 points and in exchange collapses membership-inference advantage
from +4.0% to within ±0.3% — comfortably inside the ≤5% target — at every DP level.

**Honest caveat on ε.** The `config/privacy/` names (0.5/1.0/2.0) are *design targets*; the measured
per-round ε is higher (2.18/3.83/6.71) and the cumulative ε over all rounds higher still. The strict
ε≤1 guarantee is therefore **not** met at this noise/round budget. The defensible claim is the
empirical one — DP drives measured leakage to near zero at a quantified accuracy cost — not a formal
small-ε guarantee.

## 5.6 Robustness to a poisoning tenant

One tenant is made malicious (sends negated, scaled weights); the aggregation rule is varied.
`make robust`.

| Scenario | Aggregator | Federated F1 |
|----------|------------|-------------:|
| No attack | FedAvg | 0.7872 |
| 1 poisoning tenant | FedAvg | **0.5436** |
| 1 poisoning tenant | Coordinate median | 0.7572 |
| 1 poisoning tenant | Trimmed mean | **0.7742** |

One attacker collapses plain FedAvg (0.79 → 0.54). Robust aggregation, which combines each coordinate
independently and discards outliers, filters the attacker out and restores accuracy to ~0.77. This
gives the framework a **two-sided threat model**: DP against a curious server, robust aggregation
against a malicious tenant.

## 5.7 Fault tolerance

A fixed number of tenants drop out at random each round; min-client quorum is 3 of 5. `make faults`.

| Dropped / round | % offline | Avg tenants / round | Federated F1 |
|-----------------|----------:|--------------------:|-------------:|
| 0 | 0% | 5.0 | 0.7872 |
| 1 | 20% | 4.0 | 0.7875 |
| 2 | 40% | 3.0 | 0.7824 |
| 3 | 60% | quorum lost | aborted |

The model tolerates losing up to 40% of tenants per round (beyond the one-third target) with
negligible F1 change, and safely aborts below quorum rather than aggregating too few updates — graceful
degradation plus a hard safety floor.

## 5.8 Delayed feedback and adaptation

Under a simulated time-increasing label-flip concept-drift schedule, a static no-delay model goes
stale while the delayed-label buffer + continuous-adaptation system retrains as labels arrive. The
conversion-rate **MAE reduction is ~47%** under strong drift (`make delayed`). The magnitude scales
with the amount of drift (a configurable assumption); with no drift there is no benefit, which is the
expected behaviour and the reason the drift assumption is stated explicitly.

## 5.9 Communication cost

Model update size is 72.5 KB; federation sends it each round, versus a one-time raw-data upload for
centralization. `make commcost`.

| Quantity | Value |
|----------|-------|
| Federated traffic over 15 rounds | 10.6 MB |
| Centralized one-time upload | 1.3 MB |
| Ratio | 7.9× |

Honest finding: with a small model and a static dataset, federation moves *more* bytes than
centralizing once (break-even under two rounds). The benefit of federation here is **privacy and data
locality, not bandwidth**; the picture flips when data is large or continuously growing, cannot legally
move, or when update compression is applied (future work).

## 5.10 Summary against targets

| Metric | Target | Achieved |
|--------|--------|----------|
| Conversion F1 (federated) | ≥ 0.80 | 0.788 (centralized ~0.77–0.80) |
| Cross-client gain (data-poor) | ≥ 15% | ~+10% |
| Personalization | no tenant worse than alone | achieved (Olark recovered) |
| Delayed-feedback MAE reduction | ≥ 20% | ~47% |
| Privacy leakage (DP) | ≤ 5% | +0.3% |
| Robustness | defend FedAvg collapse | 0.544 → 0.774 |
| Fault tolerance | survive one-third dropout | 40% dropout tolerated |

Some metrics fall short of the aspirational targets (F1, cross-client gain); delayed-feedback MAE,
privacy, robustness, and fault tolerance meet or exceed them. The shortfalls are explained by the data
ceiling and reported transparently.
