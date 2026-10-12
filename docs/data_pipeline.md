# Data Pipeline

This describes how the raw marketing datasets become clean, per-tenant training data with a
simulated conversion delay. All steps live in `src/fl_marketing/data/` and are run through
`scripts/prepare_data.py`.

## Primary dataset

The primary dataset is `marketing_campaign_dataset.csv` (200,000 rows, 5 companies). It is chosen
because it has both a conversion-rate value (for the MAE target) and a derivable binary conversion
label (for the F1 target), with a clean schema and five companies that become five tenants.

Supporting datasets (`global_ads_performance`, `ppc_campaign_performance`, `Marketing.csv`) are
used only to calibrate realistic value ranges. The relational-DB archive is kept as an optional
source for a small real-delay validation.

## Tenants

The five companies become five tenants. To create genuine heterogeneity (required so that shared
learning demonstrably helps weaker tenants), one or two tenants are deliberately downsampled to be
data-poor. Without this step the federated model would show little advantage over isolated models.

## Pipeline steps

| Step | Module | What it does |
|------|--------|--------------|
| 1. Ingest | `ingest.py` | Load the raw CSV(s). |
| 2. Harmonize | `harmonize.py` | Unify column names and types into one schema. |
| 3. Features | `features.py` | Encode categoricals, scale numerics into the model feature set. |
| 4. Labels | `labels.py` | Build the binary `converted` label and the `conversion_rate` target. |
| 5. Delay | `delay.py` | Assign each campaign a `launch_day` and `label_arrival_day = launch_day + delay(7-30)`. |
| 6. Partition | `partition.py` | Split into per-tenant datasets; downsample the data-poor tenant(s). |

The result is written to `data/processed/` as one dataset per tenant, with fixed-seed
train/validation/test splits.

## The simulated delay

Real marketing conversions arrive weeks after a campaign launches. Because the primary dataset has
only a single date, the delay is simulated: each campaign is given a launch day and a label-arrival
day 7-30 days later. The Delayed Label Buffer releases a label only when the simulated clock passes
its arrival day. This is what the buffer and adaptation layers are built to handle.

## Record fields

| Group | Fields | Role |
|-------|--------|------|
| Campaign settings | channel, budget, audience segment, content type, duration | model inputs |
| Engagement | impressions, clicks, click-through rate | model inputs |
| Timing | launch_day, label_arrival_day | drives the buffer |
| Outcome | converted (0/1), conversion_rate | prediction targets (hidden until arrival day) |

## Reproducibility

Dataset generation is seeded (`config/default.yaml: seed`). Re-running `make prepare` with the same
seed produces identical per-tenant datasets.
