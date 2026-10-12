from __future__ import annotations

import pandas as pd

COLUMN_MAP = {
    "Lead Source": "lead_source",
    "Lead Origin": "lead_origin",
    "Do Not Email": "do_not_email",
    "Converted": "converted",
    "TotalVisits": "total_visits",
    "Total Time Spent on Website": "time_on_site",
    "Page Views Per Visit": "page_views_per_visit",
    "Last Activity": "last_activity",
    "What is your current occupation": "occupation",
    "Specialization": "specialization",
    "City": "city",
    "A free copy of Mastering The Interview": "free_copy",
    "Asymmetrique Activity Score": "activity_score",
    "Asymmetrique Profile Score": "profile_score",
}

# Dropped on purpose: identifiers and columns that leak the outcome
# (Tags, Lead Quality, Last Notable Activity are assigned after the outcome is known).


def harmonize_schema(df: pd.DataFrame) -> pd.DataFrame:
    kept = [c for c in COLUMN_MAP if c in df.columns]
    out = df[kept].rename(columns=COLUMN_MAP)
    return out
