# Data

Raw data is **not** committed to version control. This file documents what goes where, the
datasets used, and the field definitions. Place the raw files in `data/raw/` before running
`make prepare`.

## Folders

| Folder | Contents | In git? |
|--------|----------|---------|
| `data/raw/` | Original CSV/XLSX files as received | No |
| `data/interim/` | Cleaned and schema-harmonized data | No |
| `data/processed/` | Final per-tenant datasets with the simulated delay | No |
| `data/external/` | Small benchmark sets for realism calibration | No |

## Primary dataset

`marketing_campaign_dataset.csv` — 200,000 rows, 5 companies (Innovate Industries, TechCorp,
Alpha Innovations, NexGen Systems, DataTech Solutions). Public marketing campaign dataset.

Key columns: `Company`, `Campaign_Type`, `Target_Audience`, `Duration`, `Channel_Used`,
`Conversion_Rate`, `Acquisition_Cost`, `ROI`, `Clicks`, `Impressions`, `Engagement_Score`,
`Customer_Segment`, `Date`.

The five companies are mapped to five tenants; one or two are downsampled to be data-poor.

## Supporting datasets (calibration only)

| File | Rows | Use |
|------|------|-----|
| `global_ads_performance_dataset.csv` | 1,800 | realistic CTR / CPA / conversion ranges |
| `ppc_campaign_performance_data.xlsx` | 1,000 | realistic conversion-rate ranges |
| `Marketing.csv` | 308 | small reference log |
| relational DB archive (campaigns, ads, users, ad_events) | - | optional real-delay validation |

## Licensing

These are public marketing datasets. Record the source and licence of each file here before use,
so they can be cited in the final report.

## Derived fields (added by the pipeline)

| Field | Meaning |
|-------|---------|
| `tenant_id` | Which tenant the campaign belongs to |
| `converted` | Binary conversion label (0/1) |
| `launch_day` | Simulated day the campaign launched |
| `label_arrival_day` | `launch_day` + a 7-30 day delay; when the result becomes known |
