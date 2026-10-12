# Data Pipeline

This describes how the raw data becomes clean, per-tenant training data with a simulated
conversion delay. All steps live in `src/fl_marketing/data/` and are run through
`scripts/prepare_data.py` (`make prepare`).

## Primary dataset

The primary dataset is `Lead Scoring.csv` (9,240 rows, 37 columns, binary `Converted` label).

It was chosen because it has **real predictive signal** — unlike the other datasets that were
tested (the 200k `marketing_campaign_dataset` and the brand campaign files), whose features have
no relationship to conversion (correlations near zero), making them unlearnable. On Lead Scoring a
model can realistically reach the F1 >= 0.82 target.

The task is **lead-level conversion prediction**: given a lead's origin, behaviour and profile,
predict whether it converts. This fits the Lead Intelligence role of the component.

## Tenants

Tenants are formed by splitting on **Lead Source**. Each source has a genuinely different
conversion rate and a different size, so heterogeneity is real and no synthetic skew is needed.

| Tenant | Source | Rows | Conversion rate |
|--------|--------|------|-----------------|
| 0 | Google | 2,868 | 0.40 |
| 1 | Direct Traffic | 2,543 | 0.32 |
| 2 | Olark Chat | 1,755 | 0.26 |
| 3 | Organic Search | 1,154 | 0.38 |
| 4 | Reference | 534 | 0.92 |

Tenant 4 (Reference) is the **data-poor** tenant: far fewer rows and a very different conversion
pattern. It is the clearest case for showing that federated learning helps a weak tenant.

Sources with fewer than `min_tenant_rows` (default 150) are dropped (e.g. Welingak Website,
Facebook, typo variants). The threshold is set in `config/default.yaml`.

## Pipeline steps

| Step | Module | What it does |
|------|--------|--------------|
| 1. Ingest | `ingest.py` | Load the CSV; treat `Select` placeholders as missing. |
| 2. Harmonize | `harmonize.py` | Keep and rename useful columns; drop identifiers and leaky columns (Tags, Lead Quality, Last Notable Activity). |
| 3. Labels | `labels.py` | Cast `Converted` to the integer `converted` target. |
| 4. Features | `features.py` | Encode binaries, impute + standardize numerics, one-hot encode categoricals. |
| 5. Delay | `delay.py` | Assign each lead a `launch_day` and `label_arrival_day = launch_day + delay(7-30)`. |
| 6. Partition | `partition.py` | Map Lead Source to `tenant_id`, drop small sources, add train/val/test splits. |

## Feature set

- Binary: `do_not_email`, `free_copy`.
- Numeric (imputed + standardized): `total_visits`, `time_on_site`, `page_views_per_visit`,
  `activity_score`, `profile_score`.
- Categorical (one-hot): `lead_origin`, `last_activity`, `occupation`, `specialization`, `city`.

`lead_source` is the tenant key and is never used as a feature. Leaky columns are excluded so the
model learns genuine behavioural signal, not post-hoc annotations. This produces 63 feature columns.

## The simulated delay

Real conversions arrive weeks after first contact. Because the dataset has no timestamps, the delay
is simulated: each lead gets a launch day (0 to `launch_span_days`) and a label-arrival day 7-30
days later. The Delayed Label Buffer releases a label only when the simulated clock passes its
arrival day. The MAE metric is computed on aggregate conversion rate per tenant over the delay
window (the dataset has no native conversion-rate column).

## Output

`make prepare` writes to `data/processed/`:

- `tenant_0.csv` ... `tenant_4.csv` — feature columns + `converted`, `launch_day`,
  `label_arrival_day`, `split`.
- `manifest.json` — seed, feature columns, and per-tenant row counts and conversion rates.

## Reproducibility

Generation is seeded (`config/default.yaml: seed`). Re-running `make prepare` with the same seed
reproduces identical per-tenant datasets.

## Note on running

Because the project path contains a space, run through the `make` targets (which set
`PYTHONPATH=src`) or prefix direct commands with `PYTHONPATH=src`.
