// Measured benchmark results, reproduced via the make targets noted on each card.
// These are the real numbers from the experiment scripts, not placeholders.

export const PERSONALIZATION = {
  reproduce: "make personalize",
  tenants: [
    { name: "Google", isolated: 0.7848, shared: 0.8063, personalized: 0.8078 },
    { name: "Direct Traffic", isolated: 0.6476, shared: 0.7126, personalized: 0.7048 },
    { name: "Olark Chat", isolated: 0.7126, shared: 0.6961, personalized: 0.7225 },
    { name: "Organic Search", isolated: 0.7528, shared: 0.7692, personalized: 0.7676 },
    { name: "Reference", isolated: 0.9608, shared: 0.9608, personalized: 0.9608 },
  ],
};

export const PRIVACY = {
  reproduce: "make epsilon",
  rows: [
    { setting: "Non-private", noise: "—", eps: "∞", f1: 0.7872, advantage: 4.0 },
    { setting: "Strong", noise: "1.6", eps: "2.18", f1: 0.7249, advantage: -0.3 },
    { setting: "Medium", noise: "1.1", eps: "3.83", f1: 0.7252, advantage: 0.1 },
    { setting: "Weak", noise: "0.8", eps: "6.71", f1: 0.7331, advantage: 0.3 },
  ],
};

export const FAULTS = {
  reproduce: "make faults",
  rows: [
    { label: "0% offline", f1: 0.7872, ok: true },
    { label: "20% offline", f1: 0.7875, ok: true },
    { label: "40% offline", f1: 0.7824, ok: true },
    { label: "60% offline", f1: null, ok: false },
  ],
};

export const ROBUSTNESS = {
  reproduce: "make robust",
  rows: [
    { label: "No attack · FedAvg", f1: 0.7872, status: "good" },
    { label: "Poisoned · FedAvg", f1: 0.5436, status: "critical" },
    { label: "Poisoned · Median", f1: 0.7572, status: "good" },
    { label: "Poisoned · Trimmed mean", f1: 0.7742, status: "good" },
  ],
};

export const ABLATION = {
  model: [
    { change: "Baseline model (kept)", f1: 0.7872, verdict: "best" },
    { change: "Class-weighted loss", f1: 0.7665, verdict: "worse" },
    { change: "LayerNorm architecture", f1: 0.7692, verdict: "worse" },
    { change: "Cosine LR schedule", f1: 0.7584, verdict: "worse" },
    { change: "25 rounds", f1: 0.7829, verdict: "worse" },
    { change: "40 rounds", f1: 0.7798, verdict: "worse" },
    { change: "FedProx μ = 0.1", f1: 0.7851, verdict: "worse" },
    { change: "5-seed ensemble", f1: 0.7892, verdict: "flat" },
  ],
};

export const COMM = {
  reproduce: "make commcost",
  updateSize: "72.5 KB",
  rows: [
    { label: "Federated (15 rounds)", mb: 10.6 },
    { label: "Centralized (one-time)", mb: 1.3 },
  ],
};
