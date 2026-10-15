# Chapter 1 — Introduction

## 1.1 Background and problem

Marketing-technology platforms increasingly serve many client businesses (*tenants*) from one shared
system. Each tenant accumulates its own lead and conversion data, and each would benefit from a
machine-learning model that predicts which leads will convert. The obvious approach — pool every
tenant's data centrally and train one model — is attractive statistically but unacceptable in
practice: customer records are commercially sensitive and legally protected, and no tenant wants its
leads exposed to competitors or to the platform operator. At the same time, a tenant with little data
(a new or small business) cannot train a good model alone.

This produces a genuine tension. Collaboration improves the model, especially for data-poor tenants,
but collaboration conventionally requires sharing raw data, which tenants will not do. The challenge
this component addresses is: **can multiple marketing tenants train a shared, accurate lead-conversion
model without sharing their raw data, while keeping that model private, robust to malicious
participants, and able to keep learning as real outcomes arrive weeks later?**

## 1.2 Motivation

Three properties make marketing lead data a realistic and demanding setting for federated learning:

- **Heterogeneity.** Different lead sources convert at very different rates and have different
  behavioural patterns, so tenants are naturally non-IID.
- **Imbalance.** Tenants differ greatly in size; a data-poor tenant is the one that most needs help.
- **Delayed ground truth.** A lead's true outcome (converted or not) is only known after a 7–30 day
  window, so the model must cope with labels that arrive late and with behaviour that drifts.

A framework that handles all three, with privacy and security guarantees, is directly useful to a
multi-tenant marketing platform and is the research contribution of this component.

## 1.3 Aim

To design, implement, and empirically evaluate a privacy-preserving, continuously-learning federated
framework that lets heterogeneous marketing tenants jointly train a lead-conversion model without
sharing raw data, and to characterise honestly what such a framework can and cannot achieve on real
data.

## 1.4 Objectives

1. Partition a real lead dataset into heterogeneous tenants and build a federated training loop
   (FedAvg), with a FedProx variant for the non-IID case.
2. Add a differential-privacy layer (DP-SGD) and quantify the privacy–accuracy trade-off against a
   membership-inference attack.
3. Handle delayed conversion outcomes with a delayed-label buffer and a continuous-adaptation layer.
4. Improve per-tenant performance with a personalization layer and demonstrate cross-client gain.
5. Make the framework robust to a malicious tenant (Byzantine-robust aggregation) and tolerant of
   tenant dropout.
6. Expose the framework as a deployable service (REST API) with a demonstrator dashboard.
7. Evaluate every claim with measured, reproducible experiments and report results honestly.

## 1.5 Scope

The framework is simulated on a single machine: tenants are processes within one training loop rather
than separate physical organisations, and the 7–30 day delay and concept drift are simulated on top
of the dataset. This is standard for federated-learning research and is stated as an explicit
assumption throughout. The broader multi-component SaaS platform (other team members' work) is out of
scope; this document covers the individual Lead-Intelligence component only.

## 1.6 Contributions

- A complete federated lead-conversion framework over five naturally heterogeneous tenants, reaching
  the dataset's clean accuracy ceiling without centralising data.
- An empirical privacy–accuracy–leakage characterisation showing differential privacy drives
  membership-inference advantage from +4.0% to within ±0.3%.
- A personalization layer that removes negative transfer, so **every** tenant ends at least as good
  as training alone — including the divergent tenant that plain federation harmed.
- A robust-aggregation defence that recovers accuracy after a model-poisoning attack collapses plain
  FedAvg, giving the framework a two-sided threat model (privacy *and* security).
- An honest model-strengthening ablation establishing that accuracy is data-bound, which reframes the
  modest raw F1 as a finding rather than a shortfall.

## 1.7 Document structure

Chapter 2 reviews the techniques used. Chapter 3 describes the methodology and design decisions.
Chapter 4 covers the implementation. Chapter 5 presents the measured results for each objective.
Chapter 6 discusses interpretation and limitations. Chapter 7 concludes and lists future work.
