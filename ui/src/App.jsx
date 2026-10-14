import { useEffect, useState, useCallback, useRef } from "react";
import { Gauge, Legend, GroupedBars, BarList, CompareBars } from "./charts.jsx";
import { PERSONALIZATION, PRIVACY, FAULTS, ROBUSTNESS, COMM, ABLATION } from "./results.js";

const API = "/api";

const TENANTS = [
  { id: 0, name: "Google" },
  { id: 1, name: "Direct Traffic (data-poor)" },
  { id: 2, name: "Olark Chat" },
  { id: 3, name: "Organic Search" },
  { id: 4, name: "Reference" },
];
const LEAD_ORIGIN = ["API", "Landing Page Submission", "Lead Add Form", "Lead Import"];
const OCCUPATION = ["Unemployed", "Working Professional", "Student", "Housewife", "Businessman"];
const LAST_ACTIVITY = ["Email Opened", "SMS Sent", "Olark Chat Conversation", "Page Visited on Website", "Converted to Lead", "Email Bounced"];
const LAST_NOTABLE = ["Modified", "Email Opened", "SMS Sent", "Page Visited on Website"];
const SPECIALIZATION = ["Unknown", "Finance Management", "Marketing Management", "Human Resource Management", "Operations Management"];

const HIGH = { lead_origin: "Lead Add Form", occupation: "Working Professional", last_activity: "SMS Sent", last_notable_activity: "SMS Sent", total_visits: 10, time_on_site: 1400, page_views_per_visit: 5, activity_score: 17 };
const LOW = { lead_origin: "API", occupation: "Unemployed", last_activity: "Olark Chat Conversation", last_notable_activity: "Modified", total_visits: 0, time_on_site: 30, page_views_per_visit: 1, activity_score: 14 };

const BASE = {
  tenant_id: 0, lead_origin: "API", occupation: "Unemployed", last_activity: "Email Opened",
  last_notable_activity: "Modified", specialization: "Unknown",
  total_visits: 3, time_on_site: 500, page_views_per_visit: 2.5, activity_score: 15,
};

const RANGES = {
  total_visits: { min: 0, max: 300, label: "Total visits", step: "1", hint: "0–300" },
  time_on_site: { min: 0, max: 7000, label: "Time on site (sec)", step: "1", hint: "0–7000" },
  page_views_per_visit: { min: 0, max: 60, label: "Page views / visit", step: "0.1", hint: "0–60" },
  activity_score: { min: 0, max: 30, label: "Activity score", step: "1", hint: "0–30" },
};

const STEPS = [
  "Encoding 79 lead features",
  "Loading federated global model",
  "Running inference across the network",
  "Calibrating against decision threshold",
  "Registering in delayed-label buffer",
];
const STEP_MS = 1500;
const PREDICT_MS = 7600;
const PERS_SERIES = [
  { key: "isolated", label: "Isolated (alone)", var: "--s1" },
  { key: "shared", label: "Shared federated", var: "--s2" },
  { key: "personalized", label: "Personalized", var: "--s3" },
];

function validate(form) {
  const errors = {};
  for (const [key, r] of Object.entries(RANGES)) {
    const v = form[key];
    if (v === "" || v === null || isNaN(Number(v))) errors[key] = "Enter a number";
    else if (Number(v) < r.min || Number(v) > r.max) errors[key] = `Must be ${r.hint}`;
  }
  return errors;
}

const sleep = (ms) => new Promise((res) => setTimeout(res, ms));

export default function App() {
  const [tab, setTab] = useState("demo");
  const [theme, setTheme] = useState(() => (typeof matchMedia !== "undefined" && matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"));
  const [form, setForm] = useState(BASE);
  const [result, setResult] = useState(null);
  const [campaign, setCampaign] = useState(null);
  const [counter, setCounter] = useState(1);
  const [fb, setFb] = useState("");
  const [audit, setAudit] = useState(null);
  const [online, setOnline] = useState(false);
  const [predicting, setPredicting] = useState(false);
  const [stage, setStage] = useState(0);
  const timer = useRef(null);

  const errors = validate(form);
  const hasErrors = Object.keys(errors).length > 0;
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  useEffect(() => { document.documentElement.setAttribute("data-theme", theme); }, [theme]);

  const refreshAudit = useCallback(async () => {
    try {
      const r = await fetch(`${API}/audit`);
      setAudit(await r.json());
      setOnline(true);
    } catch { setOnline(false); }
  }, []);

  useEffect(() => { refreshAudit(); }, [refreshAudit]);
  useEffect(() => () => clearInterval(timer.current), []);

  const predict = async () => {
    if (hasErrors || predicting) return;
    const id = "lead-" + counter;
    setCounter(counter + 1);
    setCampaign(id);
    setFb(""); setResult(null); setPredicting(true); setStage(0);

    let i = 0;
    clearInterval(timer.current);
    timer.current = setInterval(() => { i += 1; if (i < STEPS.length) setStage(i); else clearInterval(timer.current); }, STEP_MS);

    const body = {
      campaign_id: id, tenant_id: Number(form.tenant_id),
      lead_origin: form.lead_origin, occupation: form.occupation,
      last_activity: form.last_activity, last_notable_activity: form.last_notable_activity,
      specialization: form.specialization,
      total_visits: Number(form.total_visits), time_on_site: Number(form.time_on_site),
      page_views_per_visit: Number(form.page_views_per_visit), activity_score: Number(form.activity_score),
    };
    let res;
    try {
      const [r] = await Promise.all([
        fetch(`${API}/predict`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }),
        sleep(PREDICT_MS),
      ]);
      res = await r.json();
    } catch { res = { error: true }; }
    clearInterval(timer.current);
    setPredicting(false); setStage(0); setResult(res); refreshAudit();
  };

  const feedback = async (converted) => {
    if (!campaign) { setFb("Predict a lead first."); return; }
    try {
      const r = await fetch(`${API}/feedback`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ campaign_id: campaign, converted }) });
      const d = await r.json();
      setFb(`Real outcome recorded — ${d.status} (tenant fulfilled labels: ${d.tenant_fulfilled_count})`);
      refreshAudit();
    } catch { setFb("Could not reach the API."); }
  };

  const pct = result && !result.error ? result.conversion_probability * 100 : 0;
  const positive = result && result.predicted_converted === 1;
  const gaugeColor = !result || result.error ? "var(--muted)" : positive ? "var(--good)" : "var(--critical)";

  return (
    <div className="app">
      <header>
        <div className="brand">
          <h1>Federated Lead Intelligence</h1>
          <p>Privacy-preserving continuous learning across marketing tenants</p>
        </div>
        <div className="head-right">
          <div className={`status ${online ? "up" : "down"}`}><span className="dot" /> {online ? "API connected" : "API offline"}</div>
          <button className="theme" onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>{theme === "dark" ? "Light" : "Dark"}</button>
        </div>
      </header>

      <nav className="tabs">
        <button className={tab === "demo" ? "active" : ""} onClick={() => setTab("demo")}>Live demo</button>
        <button className={tab === "results" ? "active" : ""} onClick={() => setTab("results")}>Research results</button>
        <button className={tab === "ablation" ? "active" : ""} onClick={() => setTab("ablation")}>Ablation &amp; overview</button>
      </nav>

      {tab === "demo" && (
        <div className="grid">
          <section className="card">
            <div className="card-head">
              <h2>Lead details</h2>
              <div className="presets">
                <button className="ghost" onClick={() => setForm({ ...form, ...HIGH })}>High-intent sample</button>
                <button className="ghost" onClick={() => setForm({ ...form, ...LOW })}>Low-intent sample</button>
              </div>
            </div>
            <div className="fields">
              <Field label="Tenant (client business)">
                <select value={form.tenant_id} onChange={set("tenant_id")}>
                  {TENANTS.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
                </select>
              </Field>
              <Select label="Lead origin" value={form.lead_origin} onChange={set("lead_origin")} opts={LEAD_ORIGIN} />
              <Select label="Occupation" value={form.occupation} onChange={set("occupation")} opts={OCCUPATION} />
              <Select label="Last activity" value={form.last_activity} onChange={set("last_activity")} opts={LAST_ACTIVITY} />
              <Select label="Last notable activity" value={form.last_notable_activity} onChange={set("last_notable_activity")} opts={LAST_NOTABLE} />
              <Select label="Specialization" value={form.specialization} onChange={set("specialization")} opts={SPECIALIZATION} />
              {Object.entries(RANGES).map(([key, r]) => (
                <Num key={key} label={r.label} value={form[key]} step={r.step} hint={r.hint} error={errors[key]} onChange={set(key)} />
              ))}
            </div>
            <button className="primary" onClick={predict} disabled={hasErrors || predicting}>{predicting ? "Predicting…" : "Predict conversion"}</button>
            {hasErrors && <span className="form-note err">Fix the highlighted fields to continue.</span>}
            {!hasErrors && campaign && !predicting && <span className="form-note">{campaign} registered in the delayed buffer.</span>}
          </section>

          <div className="col">
            <section className="card">
              <h2>Prediction</h2>
              {predicting ? (
                <div className="pipeline">
                  <div className="pbar"><div className="pbar-fill" style={{ width: `${((stage + 1) / STEPS.length) * 100}%` }} /></div>
                  <ol className="steps">
                    {STEPS.map((s, idx) => (
                      <li key={s} className={idx < stage ? "done" : idx === stage ? "active" : ""}>
                        <span className="tick">{idx < stage ? "done" : idx === stage ? "running" : "queued"}</span>{s}
                      </li>
                    ))}
                  </ol>
                </div>
              ) : (
                <div className="result">
                  <Gauge pct={pct} color={gaugeColor} idle={!result || result.error} />
                  <div className="prob" style={{ color: gaugeColor }}>{result && !result.error ? pct.toFixed(1) + "%" : "—"}</div>
                  <div className="verdict" style={{ color: gaugeColor }}>
                    {!result ? "Enter a lead and predict" : result.error ? "API not reachable" : positive ? "Likely to CONVERT" : "Unlikely to convert"}
                  </div>
                  {result && !result.error && <div className="muted">decision threshold {result.threshold}</div>}
                </div>
              )}
              <div className="presets outcome">
                <button className="good" onClick={() => feedback(1)} disabled={predicting}>Record outcome: Converted</button>
                <button className="bad" onClick={() => feedback(0)} disabled={predicting}>Record outcome: Not converted</button>
              </div>
              {fb && <div className="muted fb">{fb}</div>}
            </section>

            <section className="card">
              <h2>System status (live from API)</h2>
              <Row k="Federated rounds completed" v={audit ? audit.federated_rounds.length : "—"} />
              <Row k="Differential privacy" v={audit ? <span className={`pill ${audit.differential_privacy ? "on" : "off"}`}>{audit.differential_privacy ? "ON" : "OFF"}</span> : "—"} />
              <Row k="Predictions awaiting delayed label" v={audit ? audit.buffer_pending : "—"} />
            </section>
          </div>
        </div>
      )}

      {tab === "results" && (
        <div className="results">
          <p className="results-intro">Benchmark results from the evaluation suite. Each panel is reproducible with the <code>make</code> target shown; the numbers are measured, not illustrative.</p>

          <section className="card wide">
            <div className="card-head"><h2>Cross-tenant learning &amp; personalization</h2><code>{PERSONALIZATION.reproduce}</code></div>
            <p className="muted">Test F1 per tenant. Federation lifts the data-poor tenant; personalization recovers the divergent tenant (Olark Chat) that the shared model alone hurt — so every tenant ends at least as good as training alone.</p>
            <Legend series={PERS_SERIES} />
            <GroupedBars tenants={PERSONALIZATION.tenants} series={PERS_SERIES} domain={1} />
          </section>

          <div className="results-grid">
            <section className="card">
              <div className="card-head"><h2>Privacy vs accuracy</h2><code>{PRIVACY.reproduce}</code></div>
              <p className="muted">Differential privacy collapses membership-inference leakage from +4% to within ±0.3% for a ~5-point F1 cost.</p>
              <table className="rtable">
                <thead><tr><th>Setting</th><th>ε/round</th><th>F1</th><th>Leakage</th></tr></thead>
                <tbody>
                  {PRIVACY.rows.map((r) => (
                    <tr key={r.setting}>
                      <td>{r.setting}</td><td>{r.eps}</td><td>{r.f1.toFixed(4)}</td>
                      <td className={Math.abs(r.advantage) <= 1 ? "good-text" : "crit-text"}>{r.advantage > 0 ? "+" : ""}{r.advantage}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>

            <section className="card">
              <div className="card-head"><h2>Robustness to poisoning</h2><code>{ROBUSTNESS.reproduce}</code></div>
              <p className="muted">One malicious tenant collapses plain FedAvg; robust aggregation filters it out.</p>
              <BarList rows={ROBUSTNESS.rows} max={1} />
            </section>

            <section className="card">
              <div className="card-head"><h2>Fault tolerance</h2><code>{FAULTS.reproduce}</code></div>
              <p className="muted">Global F1 as tenants drop out per round. Below quorum (min 3 of 5) the server safely aborts.</p>
              <BarList rows={FAULTS.rows} max={1} nullLabel="quorum lost" />
            </section>

            <section className="card">
              <div className="card-head"><h2>Communication cost</h2><code>{COMM.reproduce}</code></div>
              <p className="muted">Model update {COMM.updateSize} per transfer. Federation trades more bytes for never moving raw data — the benefit here is privacy, not bandwidth.</p>
              <CompareBars rows={COMM.rows} unit="MB" />
            </section>
          </div>
        </div>
      )}

      {tab === "ablation" && (
        <div className="doc">
          <section className="card">
            <h2>What this component is</h2>
            <p>A <strong>Privacy-Preserving Continuous Learning Framework for Multi-Tenant Marketing AI</strong>.
              Several separate marketing businesses (tenants) jointly train one lead-conversion model
              <em> without ever sharing their raw customer data</em>, the model is protected against
              privacy and poisoning attacks, and it keeps learning as real conversion outcomes arrive
              weeks late. Lead conversion prediction is the task used to demonstrate the framework; the
              framework itself is the contribution.</p>
            <div className="pillars">
              <div className="pillar"><b>Federated learning</b><span>Tenants exchange only model weights (FedAvg); raw leads never leave a tenant.</span></div>
              <div className="pillar"><b>Differential privacy</b><span>DP-SGD noise blocks membership-inference against an honest-but-curious server.</span></div>
              <div className="pillar"><b>Robust aggregation</b><span>Coordinate-median / trimmed-mean defend against a malicious tenant.</span></div>
              <div className="pillar"><b>Continuous adaptation</b><span>A delayed-label buffer feeds late real outcomes back to keep the model current.</span></div>
            </div>
          </section>

          <section className="card">
            <h2>The individual research contribution</h2>
            <p>Everything in this component was built as the individual Lead-Intelligence research piece:</p>
            <ul className="doclist">
              <li>A federated training loop (FedAvg, with a FedProx ablation) over five naturally heterogeneous tenants split by Lead Source.</li>
              <li>A differential-privacy layer (Opacus DP-SGD) with a measured privacy–accuracy–leakage sweep.</li>
              <li>A delayed-label buffer and continuous-adaptation layer handling the 7–30 day conversion delay.</li>
              <li>A personalization layer (shared backbone + per-tenant fine-tuned head) fixing negative transfer.</li>
              <li>Byzantine-robust aggregation defending against a model-poisoning tenant.</li>
              <li>Fault tolerance under per-round tenant dropout with a quorum floor.</li>
              <li>A REST API (FastAPI) serving the model, and this dashboard.</li>
            </ul>
            <p className="muted">Honest positioning: conversion accuracy is bounded by the data (~0.81 F1 ceiling across all model families). The contribution is reaching that ceiling under privacy, robustness, and delayed feedback — not a higher raw score.</p>
          </section>

          <section className="card">
            <div className="card-head"><h2>Ablation 1 — model strengthening</h2><code>experiment_guide.md</code></div>
            <p className="muted">Every attempt to strengthen the model was measured against the baseline. None beat it, proving accuracy is data-bound, not model-bound (0.788 ± 0.003 over 5 seeds).</p>
            <table className="rtable">
              <thead><tr><th>Change</th><th>Pooled F1</th><th>Verdict</th></tr></thead>
              <tbody>
                {ABLATION.model.map((r) => (
                  <tr key={r.change}>
                    <td>{r.change}</td><td>{r.f1.toFixed(4)}</td>
                    <td className={r.verdict === "best" ? "good-text" : r.verdict === "flat" ? "" : "crit-text"}>{r.verdict}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>

          <div className="results-grid">
            <section className="card">
              <div className="card-head"><h2>Ablation 2 — aggregation under attack</h2><code>make robust</code></div>
              <p className="muted">Swapping the aggregation rule while a poisoning tenant is present.</p>
              <BarList rows={ROBUSTNESS.rows} max={1} />
            </section>
            <section className="card">
              <div className="card-head"><h2>Ablation 3 — differential privacy</h2><code>make epsilon</code></div>
              <p className="muted">Turning DP on trades ~5 F1 points for near-zero leakage.</p>
              <table className="rtable">
                <thead><tr><th>Setting</th><th>F1</th><th>Leakage</th></tr></thead>
                <tbody>
                  {PRIVACY.rows.map((r) => (
                    <tr key={r.setting}>
                      <td>{r.setting}</td><td>{r.f1.toFixed(4)}</td>
                      <td className={Math.abs(r.advantage) <= 1 ? "good-text" : "crit-text"}>{r.advantage > 0 ? "+" : ""}{r.advantage}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>
          </div>
        </div>
      )}
    </div>
  );
}

function Field({ label, children }) {
  return <label className="field"><span>{label}</span>{children}</label>;
}
function Select({ label, value, onChange, opts }) {
  return <Field label={label}><select value={value} onChange={onChange}>{opts.map((o) => <option key={o} value={o}>{o}</option>)}</select></Field>;
}
function Num({ label, value, onChange, step, hint, error }) {
  return (
    <label className="field">
      <span>{label} <em>{hint}</em></span>
      <input type="number" step={step || "1"} value={value} onChange={onChange} className={error ? "invalid" : ""} />
      {error && <small className="err">{error}</small>}
    </label>
  );
}
function Row({ k, v }) {
  return <div className="kv"><span>{k}</span><b>{v}</b></div>;
}
