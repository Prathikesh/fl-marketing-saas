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
1. Click "Load high-intent lead" then "Predict conversion" — the probability gauge jumps near 100%.
2. Click "Load low-intent lead" then "Predict" — the gauge drops near 0%.
3. Click an outcome button ("Converted" / "Not converted") — the real label is matched back in the
   delayed buffer; the status panel updates.
4. The "System status" panel shows the number of federated rounds, whether differential privacy is
   on, and how many predictions are still waiting for their delayed label.

To demo privacy being on: train with `python scripts/run_federated.py --private --save`, restart
`make serve`, and the status panel shows "Differential privacy: ON".

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
