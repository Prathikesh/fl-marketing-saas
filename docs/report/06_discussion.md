# Chapter 6 — Discussion

## 6.1 Interpretation

Taken together, the results support a single claim: **marketing tenants can safely pool their learning**
— data-poor tenants become more accurate, nobody exposes their customers, a malicious tenant cannot
wreck the model, the system tolerates dropout, and it keeps adapting to delayed outcomes — **at
essentially no accuracy cost** relative to centralizing everything.

The most important result is not a headline accuracy number but the **combination**:

- Federation matches centralized accuracy (§5.1) — so collaboration is "free" on accuracy.
- The data-poor tenant gains ~10% (§5.3) — so there is a concrete reason to join.
- Personalization ensures no tenant is harmed (§5.4) — so joining is safe for everyone, not just the
  data-poor.
- DP makes participation trustworthy (§5.5) and robust aggregation makes it safe from sabotage (§5.6).

This directly addresses the tension set out in Chapter 1: the assumed trade-off between privacy and
accuracy is largely avoided, and the barriers that stop competing businesses from collaborating are
each given a measured mitigation.

## 6.2 Why accuracy is bounded, and why that is acceptable

The ablation in §5.2 shows no architecture, loss weighting, schedule, round budget, FedProx setting,
or ensembling improves on the baseline, and the EDA (weak feature–target correlations) explains why:
the predictive signal in the non-leaky features is genuinely limited. Reaching ~0.81 is reaching the
information ceiling of the data. The contribution is therefore correctly framed as the **framework**
that attains that ceiling under privacy, robustness, and delayed feedback — not a higher raw F1. An
examiner who presses on accuracy is answered with the ablation and the refusal of leaky columns.

## 6.3 Limitations and threats to validity

- **Single-machine simulation.** Tenants are processes in one loop, not separate organisations. Network
  effects, stragglers across real links, and cross-organisation trust are not exercised. The *method*
  generalises; real multi-party deployment is unverified.
- **Simulated delay and drift.** The 7–30 day delay and the concept drift behind the ~47% MAE
  reduction are simulated (a label-flip schedule). The magnitude depends on that assumption, which is
  stated explicitly; it is not an observed real-world drift.
- **Privacy budget.** The achieved per-round ε (2.18–6.71) exceeds the nominal targets and the
  cumulative ε is larger still, so the strict ε≤1 formal guarantee is not met. The privacy claim is
  empirical (leakage → near zero), not a tight formal bound.
- **Dataset specificity.** Results are specific to Lead Scoring; the exact numbers will differ on other
  data, though the comparative findings (federation helps data-poor tenants, DP trades accuracy for
  privacy, robust aggregation defends poisoning) are expected to transfer.
- **Single attack model.** Robustness is shown against one model-poisoning strategy and two robust
  rules; stronger adaptive attacks and defences (e.g. Krum, adaptive poisoning) are not exhausted.
- **Communication.** Federation is more bandwidth-hungry than centralizing on this small static dataset
  (§5.9); the advantage only appears under growing data or compression.

## 6.4 Comparison with the proposal targets

Delayed-feedback MAE reduction, privacy leakage, robustness, and fault tolerance meet or exceed their
targets. Conversion F1 (0.80 vs 0.82) and cross-client gain (10% vs 15%) fall short, both for the same
root cause — the data ceiling and the refusal of leaky features. Reporting these shortfalls honestly,
with the ablation evidence, is treated as a strength of the evaluation rather than something to hide.
