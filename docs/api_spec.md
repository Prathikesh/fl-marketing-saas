# API Specification

The component exposes a REST service (FastAPI, `src/fl_marketing/api/`). This is the contract other
platform components depend on, so it is frozen early and changes are communicated in advance.

Base URL (local): `http://localhost:8000`

## POST /predict

Returns a conversion probability for a campaign and registers the prediction with the delayed
label buffer.

Request:
```
{
  "campaign_id": "C12345",
  "tenant_id": 2,
  "features": { "channel": "email", "budget": 5000, "audience_segment": "Men 25-34", ... }
}
```

Response:
```
{ "campaign_id": "C12345", "conversion_probability": 0.68 }
```

## POST /feedback

Submits a real campaign outcome. The buffer matches it to the original prediction and, once enough
results are collected for a tenant, triggers continuous adaptation.

Request:
```
{ "campaign_id": "C12345", "converted": 1 }
```

Response:
```
{ "status": "buffered" }
```

## GET /audit

Returns the federated-round audit log (administrator use).

Response:
```
[
  { "round_id": 1, "timestamp": "...", "participating_tenants": 5,
    "model_version": "v1", "aggregation_outcome": "ok", "mean_test_f1": 0.83 }
]
```

## Notes

- Request and response shapes are defined in `src/fl_marketing/api/schemas.py`.
- Interactive documentation is auto-generated at `/docs` when the service runs.
