from __future__ import annotations

import pandas as pd

BINARY_COLS = ["do_not_email", "free_copy"]
NUMERIC_COLS = ["total_visits", "time_on_site", "page_views_per_visit", "activity_score", "profile_score"]
CATEGORICAL_COLS = ["lead_origin", "last_activity", "occupation", "specialization", "city", "last_notable_activity"]
PASSTHROUGH = ["converted", "lead_source"]


def _encode_binary(df: pd.DataFrame) -> pd.DataFrame:
    for col in BINARY_COLS:
        df[col] = (df[col].astype(str).str.lower() == "yes").astype(int)
    return df


def _encode_numeric(df: pd.DataFrame) -> pd.DataFrame:
    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].fillna(df[col].median())
        std = df[col].std()
        if std > 0:
            df[col] = (df[col] - df[col].mean()) / std
    return df


def _encode_categorical(df: pd.DataFrame) -> pd.DataFrame:
    for col in CATEGORICAL_COLS:
        df[col] = df[col].fillna("Unknown")
    return pd.get_dummies(df, columns=CATEGORICAL_COLS, dtype=int)


def encode_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out = _encode_binary(out)
    out = _encode_numeric(out)
    out = _encode_categorical(out)
    return out


def feature_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c not in PASSTHROUGH]
