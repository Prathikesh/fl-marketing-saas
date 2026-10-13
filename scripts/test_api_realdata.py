from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

import pandas as pd

RAW_TO_FIELD = {
    "Lead Origin": "lead_origin",
    "Last Activity": "last_activity",
    "What is your current occupation": "occupation",
    "Specialization": "specialization",
    "City": "city",
    "Last Notable Activity": "last_notable_activity",
    "TotalVisits": "total_visits",
    "Total Time Spent on Website": "time_on_site",
    "Page Views Per Visit": "page_views_per_visit",
    "Asymmetrique Activity Score": "activity_score",
    "Asymmetrique Profile Score": "profile_score",
}
NUMERIC_FIELDS = {"total_visits", "time_on_site", "page_views_per_visit", "activity_score", "profile_score"}
CATEGORICAL_FIELDS = {"lead_origin", "last_activity", "occupation", "specialization", "city", "last_notable_activity"}
BINARY_RAW = {"Do Not Email": "do_not_email", "A free copy of Mastering The Interview": "free_copy"}


def load_tenant_map(manifest_path: Path) -> dict[str, int]:
    manifest = json.loads(manifest_path.read_text())
    return {t["source"].strip().lower(): t["tenant_id"] for t in manifest["tenants"]}


def build_payload(row: pd.Series, tenant_map: dict[str, int], idx: int) -> dict:
    payload = {"campaign_id": f"realtest-{idx}", "launch_day": 0}
    source = str(row.get("Lead Source", "")).strip().lower()
    payload["tenant_id"] = tenant_map.get(source, 0)
    for raw_col, field in RAW_TO_FIELD.items():
        value = row.get(raw_col)
        if field in NUMERIC_FIELDS:
            num = pd.to_numeric(value, errors="coerce")
            if not pd.isna(num):
                payload[field] = float(num)
        else:
            payload[field] = str(value) if not pd.isna(value) else "Unknown"
    for raw_col, field in BINARY_RAW.items():
        payload[field] = 1 if str(row.get(raw_col, "")).strip().lower() == "yes" else 0
    return payload


def post_predict(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke-test the /predict API with real Lead Scoring leads.")
    parser.add_argument("--n", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--url", default="http://127.0.0.1:8000/predict")
    parser.add_argument("--csv", default="data/raw/Lead Scoring.csv")
    parser.add_argument("--manifest", default="data/processed/manifest.json")
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    tenant_map = load_tenant_map(Path(args.manifest))
    sample = df.sample(n=min(args.n, len(df)), random_state=args.seed).reset_index(drop=True)

    print(f"{'#':>3}  {'source':<15} {'tenant':>6} {'prob':>7} {'pred':>5} {'actual':>7}  ok")
    print("-" * 56)
    correct = 0
    scored = 0
    for idx, row in sample.iterrows():
        actual = row.get("Converted")
        payload = build_payload(row, tenant_map, idx)
        result = post_predict(args.url, payload)
        prob = result["conversion_probability"]
        pred = result["predicted_converted"]
        source = str(row.get("Lead Source", ""))[:15]
        if not pd.isna(actual):
            scored += 1
            hit = int(pred) == int(actual)
            correct += int(hit)
            mark = "Y" if hit else "."
            actual_str = str(int(actual))
        else:
            mark = "?"
            actual_str = "NA"
        print(f"{idx:>3}  {source:<15} {payload['tenant_id']:>6} {prob:>7.4f} {pred:>5} {actual_str:>7}  {mark}")

    if scored:
        print("-" * 56)
        print(f"accuracy: {correct}/{scored} = {correct / scored:.3f}")


if __name__ == "__main__":
    main()
