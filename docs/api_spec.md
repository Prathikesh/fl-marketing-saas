# API Specification

The component exposes a REST service (FastAPI, `src/fl_marketing/api/`). This is the contract other
platform components depend on. Start it with `make serve` (loads the saved model from `models/`).

Base URL (local): `http://127.0.0.1:8000`
Interactive docs: `http://127.0.0.1:8000/docs`

Prerequisite: run `make prepare` then `make train` with saving enabled
(`python scripts/run_federated.py --save`) so `models/global_model.pt` exists.

## GET /health

Returns `{ "status": "ok" }`.

## POST /predict

Takes a lead's attributes, returns a conversion probability, and registers the prediction with the
delayed label buffer.

Request (all fields optional, with defaults):
```
{
  "campaign_id": "lead-A", "tenant_id": 0,
  "lead_origin": "Lead Add Form", "occupation": "Working Professional",
  "last_activity": "SMS Sent", "last_notable_activity": "SMS Sent",
  "specialization": "Unknown", "city": "Mumbai",
  "do_not_email": 0, "free_copy": 0,
  "total_visits": 10, "time_on_site": 1400, "page_views_per_visit": 5,
  "activity_score": 17, "profile_score": 18, "launch_day": 0
}
```

Response:
```
{ "campaign_id": "lead-A", "conversion_probability": 0.9999,
  "predicted_converted": 1, "threshold": 0.38 }
```

## POST /feedback

Submits the real outcome. The buffer matches it to the original prediction.

Request:
```
{ "campaign_id": "lead-A", "converted": 1 }
```

Response:
```
{ "campaign_id": "lead-A", "status": "label_matched", "tenant_fulfilled_count": 1 }
```

## GET /audit

Returns the federated round log, whether differential privacy was used, and the number of
predictions still waiting for their delayed label.

## GET /tenants

Returns the tenant id to source-name mapping.

## Notes

- Request/response shapes are defined in `src/fl_marketing/api/schemas.py`.
- The server encodes incoming lead attributes with the same preprocessing used in training
  (numeric standardisation stats and feature columns are read from the data manifest).
