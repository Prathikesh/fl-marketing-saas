# Demo Guide (PP1)

A step-by-step live demo of the component. Total time: about three minutes.

## One-time setup

```
cd fl-marketing-saas
source .venv/bin/activate      # or: make dev   (first time only)
```

## Option A — full live demo with the React web UI (recommended)

The UI is a Vite + React app in `ui/`. First time only, install its dependencies:
```
make ui-install        # one-time: installs React/Vite (cd ui && npm install)
```

Then use two terminals.

Terminal 1 (prepare, train, serve the API backend):
```
make prepare                           # build the 5 tenants + data-poor tenant + delay
python scripts/run_federated.py --save # federated training, saves the model for serving
make serve                             # starts the API at http://127.0.0.1:8000
```

Terminal 2 (start the React UI):
```
make ui                                # starts Vite at http://localhost:5173 and opens the browser
```

The React app talks to the API through a dev proxy (`/api` -> `http://127.0.0.1:8000`), so there are
no cross-origin issues. The header shows "API connected" when the backend is reachable.

In the UI:
1. Click "High-intent sample" then "Predict conversion". The prediction panel first shows the live
   pipeline — encoding the 79 lead features, running inference on the federated model, then
   registering the lead in the delayed-label buffer — before revealing the probability gauge near
   100%. These are the real steps the backend runs; surfacing them (over ~1.3s) makes clear the
   prediction is computed, not looked up.
2. Click "Low-intent sample" then "Predict" — the gauge drops near 0%.
3. The numeric fields are validated inline (allowed ranges shown next to each label); the Predict
   button stays disabled until every field is valid, so you cannot send a malformed lead.
4. Click an outcome button ("Converted" / "Not converted") — the real label is matched back in the
   delayed buffer; the status panel updates.
5. The "System status" panel shows the number of federated rounds, whether differential privacy is
   on, and how many predictions are still waiting for their delayed label (expand "Raw audit
   response" for the live JSON).

To demo privacy being on: train with `python scripts/run_federated.py --private --save`, restart
`make serve`, and the status panel shows "Differential privacy: ON".

## Testing the API with real leads

Instead of hand-typing leads, `scripts/test_api_realdata.py` samples real rows from
`data/raw/Lead Scoring.csv`, maps their raw columns to the `/predict` fields (Lead Source ->
tenant_id via the manifest), POSTs each to the running API, and prints predicted probability,
predicted label, the ACTUAL `Converted` value, and overall accuracy.

The API must already be running (`make serve`). Then, in another terminal:
```
python scripts/test_api_realdata.py --n 20       # or --n 300 for a more stable number
```
Typical result: ~0.83 accuracy, consistent with the ~0.80 F1 ceiling — confirming the served
model behaves like the trained one. Lead Source values outside the five tenants (e.g. "Referral
Sites") fall back to tenant 0.

To type a real lead into the React UI instead, pick any row from the CSV and copy its columns into
the form fields (Lead Origin -> Lead origin, What is your current occupation -> Occupation, etc.);
set Tenant from the row's Lead Source.

## Option B — terminal-only demo

Each command tells one part of the story:

```
make test       # all modules unit-tested
make prepare     # 5 isolated tenants, one data-poor "new business", simulated delay
make train       # federated learning: local training + FedAvg, global F1
make evaluate    # cross-client gain: the data-poor tenant gains ~10% from federation
make delayed     # delayed feedback: adaptation cuts MAE ~47% under concept drift
make privacy     # membership inference attack: DP drops leakage to near zero
```

## Talking points

- Data never leaves a tenant; only model updates are shared (federated learning).
- The data-poor tenant benefits most from the shared model (the value of cross-tenant learning).
- The delayed label buffer handles the weeks-long gap before marketing outcomes are known.
- Differential privacy defends against membership inference with little accuracy cost.
- All results use real public data; numbers are reported honestly (see experiment_guide.md).
