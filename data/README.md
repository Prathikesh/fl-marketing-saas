# Data

Raw data is **not** committed to version control. This file documents what goes where, the
datasets used, and the field definitions. Place the raw files in `data/raw/` before running
`make prepare`.

## Folders

| Folder | Contents | In git? |
|--------|----------|---------|
| `data/raw/` | Original CSV/XLSX files as received | No |
| `data/interim/` | Cleaned intermediate data (optional) | No |
| `data/processed/` | Final per-tenant datasets with the simulated delay | No |
| `data/external/` | Small benchmark sets for realism calibration | No |

## Primary dataset

`Lead Scoring.csv` — 9,240 rows, 37 columns, binary `Converted` label. A real lead-conversion
dataset where lead behaviour and profile genuinely predict conversion. Chosen over the campaign
datasets because those were tested and found to be statistical noise (no feature-outcome signal),
so no model could reach the F1 target on them.

Tenants are formed by splitting on **Lead Source**: Google, Direct Traffic, Olark Chat, Organic
Search, Reference. These have genuinely different conversion rates (26%-92%) and sizes, so Reference
is a natural data-poor tenant. See [../docs/data_pipeline.md](../docs/data_pipeline.md) for details.

### Columns used

| Clean name | Source column | Type | Role |
|------------|---------------|------|------|
| converted | Converted | binary | target |
| lead_source | Lead Source | categorical | tenant key (not a feature) |
| lead_origin | Lead Origin | categorical | feature |
| do_not_email | Do Not Email | binary | feature |
| free_copy | A free copy of Mastering The Interview | binary | feature |
| total_visits | TotalVisits | numeric | feature |
| time_on_site | Total Time Spent on Website | numeric | feature |
| page_views_per_visit | Page Views Per Visit | numeric | feature |
| activity_score | Asymmetrique Activity Score | numeric | feature |
| profile_score | Asymmetrique Profile Score | numeric | feature |
| last_activity | Last Activity | categorical | feature |
| occupation | What is your current occupation | categorical | feature |
| specialization | Specialization | categorical | feature |
| city | City | categorical | feature |

Dropped on purpose: identifiers (Prospect ID, Lead Number) and leaky columns assigned after the
outcome is known (Tags, Lead Quality, Last Notable Activity).

## Supporting datasets (calibration only, not for training)

| File | Rows | Use |
|------|------|-----|
| `global_ads_performance_dataset.csv` | 1,800 | realistic CTR / CPA / conversion ranges |
| `Marketing.csv` | 308 | small reference log |
| relational DB archive (campaigns, ads, users, ad_events) | - | optional real-delay validation |

Not used (tested and found unusable): the 200k `marketing_campaign_dataset`, the nykaa/purplle/tira
brand files (statistical noise), KAG Facebook ads (too small/weak), the broken ROI xlsx.

## Licensing

These are public datasets. Record the source and licence of each file here before use so they can
be cited in the final report.

## Derived fields (added by the pipeline)

| Field | Meaning |
|-------|---------|
| `tenant_id` | Which tenant the lead belongs to |
| `launch_day` | Simulated day the lead entered |
| `label_arrival_day` | `launch_day` + a 7-30 day delay; when the result becomes known |
| `split` | train / val / test |
