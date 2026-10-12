# FL Marketing SaaS — Privacy-Preserving Continuous Learning Framework

A federated learning backend for a multi-tenant AI marketing platform. Multiple marketing
clients ("tenants") collectively train one shared conversion-prediction model **without sharing
any raw data**, with differential privacy on every update and a mechanism that handles the
weeks-long delay before marketing conversion results are known.

Everything runs **simulated on a single machine** using real public marketing datasets adapted
into multiple tenants. There are no real users and no live integrations in this component.

## What this component does

- Trains a conversion-prediction model locally inside each tenant's isolated partition.
- Protects each model update with differential privacy (DP-SGD) before it leaves the tenant.
- Combines all tenant updates into one global model using federated averaging (FedAvg).
- Buffers each prediction and waits 7-30 days for the real conversion result to arrive.
- Incrementally retrains the model when enough real results are collected.
- Exposes the model through a REST API for the rest of the platform.

## Repository layout

| Path | Purpose |
|------|---------|
| `config/` | All tunable settings (tenants, privacy budget, rounds, thresholds). Nothing is hard-coded. |
| `data/` | Raw, interim, and processed datasets (git-ignored) plus the data dictionary. |
| `src/fl_marketing/` | The installable package. One folder per architecture layer. |
| `scripts/` | Thin command-line entrypoints. All logic lives in the package. |
| `experiments/` | Results, plots, and exploration notebooks. |
| `tests/` | Unit, integration, and API tests. |
| `docs/` | Architecture, data pipeline, API spec, and experiment guide. Read these first. |

See [docs/architecture.md](docs/architecture.md) for how the six layers map onto the folders.

## Setup

```
make dev        # install everything in editable mode (dev tools included)
```

Or manually:

```
pip install -r requirements-dev.txt
pip install -e .
```

## Typical workflow

```
make prepare    # build per-tenant datasets from the raw data
make train      # run the full federated framework
make baseline   # run a baseline for comparison
make evaluate   # produce the comparison metrics and tables
make privacy    # run the membership inference privacy test
make serve      # launch the REST API
make test       # run the test suite
```

## Documentation

- [docs/architecture.md](docs/architecture.md) — the six layers and the data flow.
- [docs/data_pipeline.md](docs/data_pipeline.md) — how raw data becomes per-tenant datasets.
- [docs/api_spec.md](docs/api_spec.md) — the REST contract used by other platform components.
- [docs/experiment_guide.md](docs/experiment_guide.md) — how to reproduce every result.
- [data/README.md](data/README.md) — datasets, sources, and field definitions.

## Status

Scaffold stage. The folder structure, configuration, and documentation are in place. Module
bodies are stubs to be implemented stage by stage (see the experiment guide for the build order).
