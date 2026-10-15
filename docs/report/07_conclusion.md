# Chapter 7 — Conclusion and future work

## 7.1 Summary

This component designed, implemented, and evaluated a privacy-preserving, continuously-learning
federated framework for multi-tenant marketing lead-conversion prediction. Five naturally
heterogeneous tenants jointly train one model without sharing raw data; the model is protected by
differential privacy against a curious server and by robust aggregation against a malicious tenant; it
tolerates tenant dropout; and it keeps learning from conversion outcomes that arrive weeks late. The
whole framework is served through a REST API and demonstrated in a dashboard, and every claim is backed
by a measured, reproducible experiment.

## 7.2 Objectives revisited

All seven objectives from Chapter 1 were met:

1. Federated training loop over heterogeneous tenants, with a FedProx ablation. ✓
2. Differential-privacy layer with a membership-inference-based privacy–accuracy characterisation. ✓
3. Delayed-label buffer and continuous-adaptation layer under simulated drift. ✓
4. Personalization layer and a demonstrated cross-client gain for the data-poor tenant. ✓
5. Byzantine-robust aggregation against a poisoning tenant, plus dropout fault tolerance. ✓
6. Deployable REST API and demonstrator dashboard. ✓
7. Honest, reproducible evaluation of every claim. ✓

## 7.3 Contributions

The integrated framework shows, on a single realistic marketing task, that the usually-assumed
trade-off between privacy and accuracy can be largely avoided: federation matches centralized accuracy
at the data ceiling, data-poor tenants gain, personalization ensures no tenant is harmed, differential
privacy nearly eliminates measured leakage, and robust aggregation neutralises a poisoning attack. The
honest model-strengthening ablation — establishing that accuracy is data-bound — reframes the modest
raw F1 as a finding and strengthens rather than weakens the thesis.

## 7.4 Future work

- **Real multi-party deployment** across separate processes or machines to exercise network effects,
  stragglers, and cross-organisation trust.
- **Real delayed-outcome validation** using actual conversion timestamps instead of simulated delay
  and drift.
- **Tighter privacy** via privacy accounting across rounds and tuned noise to reach a formal small-ε
  guarantee, and secure aggregation so the server never sees individual updates.
- **Stronger adversarial study** with adaptive poisoning attacks and additional defences (e.g. Krum,
  norm-bounding).
- **Communication efficiency** via update compression/quantization, which would also flip the
  bandwidth comparison in federation's favour.
- **Personalization depth** beyond a single fine-tuned head (e.g. adapters, multi-layer personalization).

## 7.5 Closing remark

The component delivers a working, defensible demonstration that competing marketing businesses can
collaborate on a shared model without surrendering their data or exposing themselves to a malicious
participant — with the costs and limits of doing so measured and reported honestly.

## References

- McMahan, B. et al. (2017). *Communication-Efficient Learning of Deep Networks from Decentralized
  Data* (FedAvg). AISTATS.
- Li, T. et al. (2020). *Federated Optimization in Heterogeneous Networks* (FedProx). MLSys.
- Arivazhagan, M. G. et al. (2019). *Federated Learning with Personalization Layers* (FedPer).
- Abadi, M. et al. (2016). *Deep Learning with Differential Privacy* (DP-SGD). ACM CCS.
- Yousefpour, A. et al. (2021). *Opacus: User-Friendly Differential Privacy Library in PyTorch*.
- Shokri, R. et al. (2017). *Membership Inference Attacks Against Machine Learning Models*. IEEE S&P.
- Yin, D. et al. (2018). *Byzantine-Robust Distributed Learning: Towards Optimal Statistical Rates*
  (coordinate median, trimmed mean). ICML.
- Blanchard, P. et al. (2017). *Machine Learning with Adversaries: Byzantine Tolerant Gradient Descent*
  (Krum). NeurIPS.
