# Chapter 2 — Background and related work

## 2.1 Federated learning and FedAvg

Federated learning trains a shared model across decentralised clients that never exchange raw data.
The canonical algorithm, **Federated Averaging (FedAvg)** (McMahan et al., 2017), runs in rounds: the
server broadcasts the current global model; each client trains locally for a few epochs on its own
data; the server collects the updated weights and averages them, weighted by each client's number of
samples. Only model parameters cross the network, never the data.

FedAvg assumes clients are reasonably similar. When clients are **non-IID** — different data
distributions — local updates pull in different directions and the averaged model can be worse than
any single client's, a phenomenon called *client drift* or *negative transfer*. Marketing tenants
split by lead source are strongly non-IID (conversion rates from 26% to 92% in this dataset), so the
non-IID case is central here, not incidental.

## 2.2 Mitigating heterogeneity: FedProx and personalization

**FedProx** (Li et al., 2020) adds a proximal term to each client's loss that penalises drifting too
far from the global model, trading some local fit for stability. It helps when clients are mildly
heterogeneous but, as shown in Chapter 5, does not help — and can hurt — when tenants genuinely
differ, because constraining them removes useful specialisation.

**Personalization** attacks heterogeneity from the opposite direction: keep a shared representation
but let each client adapt a small part of the model to itself. **FedPer** (Arivazhagan et al., 2019)
shares the lower layers (the representation) and keeps a per-client "head" (the final layers). This
component uses a FedPer-style approach — a shared federated backbone with a per-tenant fine-tuned
final layer — to recover tenants that plain FedAvg harms.

## 2.3 Differential privacy and DP-SGD

Sharing only weights is not sufficient privacy: model updates can leak information about the training
data. **Differential privacy (DP)** gives a formal guarantee that the presence or absence of any
single record has a bounded effect on the output, parameterised by a privacy budget ε (smaller = more
private). **DP-SGD** (Abadi et al., 2016) enforces DP during training by clipping each per-sample
gradient to a maximum norm and adding calibrated Gaussian noise before the optimiser step. The
implementation here uses **Opacus** (Yousefpour et al., 2021), PyTorch's DP-SGD library.

A practical note exploited in the design: DP-SGD requires *per-sample* gradients, which is
incompatible with BatchNorm (it mixes samples across a batch). LayerNorm or no normalisation is the
DP-correct choice — relevant to the model-architecture ablation in Chapter 5.

## 2.4 Measuring privacy: membership-inference attacks

A **membership-inference attack** (Shokri et al., 2017) tries to determine whether a particular
record was in the model's training set, exploiting the fact that models are more confident on data
they have seen. Attack success above the 50% random baseline is the *advantage*; a smaller advantage
means better privacy. This component uses a shadow-model membership-inference attack as the empirical
privacy metric, measured with and without DP.

## 2.5 Byzantine-robust aggregation

FedAvg trusts every client. A single **malicious (Byzantine) client** can send corrupted updates
that, once averaged, wreck the global model — a *model-poisoning* attack. Robust aggregation rules
replace the mean with a statistic that tolerates outliers. Two common rules, used here, are the
**coordinate-wise median** and the **trimmed mean** (Yin et al., 2018), which aggregate each parameter
coordinate independently and discard extreme values; **Krum** (Blanchard et al., 2017) is a related
approach that selects the update closest to its neighbours. These give the framework a defence against
a malicious participant, complementing DP's defence against a curious observer.

## 2.6 Delayed feedback and concept drift

In marketing, a prediction is made at lead capture but the true label (did the lead convert?) arrives
only after a 7–30 day window. During that window, customer behaviour and campaign conditions can
change — **concept drift** — so a static model goes stale. Handling delayed labels requires buffering
predictions until their outcome is known and then adapting the model incrementally. This is modelled
here with a delayed-label buffer and a continuous-adaptation layer, evaluated under a simulated
time-increasing label-flip drift schedule.

## 2.7 Positioning

Each technique above is individually established. The contribution of this component is not a new
algorithm but the **integration and honest empirical evaluation** of federated learning, differential
privacy, robust aggregation, personalization, and delayed-feedback adaptation on a single realistic
marketing task — and the demonstration of where the combined system succeeds and where it is bounded
by the data.
