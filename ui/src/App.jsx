import { useEffect, useState, useCallback, useRef } from "react";

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
  "Running inference on federated model",
  "Registering in delayed-label buffer",
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

  const refreshAudit = useCallback(async () => {
    try {
      const r = await fetch(`${API}/audit`);
      setAudit(await r.json());
      setOnline(true);
    } catch {
      setOnline(false);
    }
  }, []);

  useEffect(() => { refreshAudit(); }, [refreshAudit]);
  useEffect(() => () => clearInterval(timer.current), []);

  const predict = async () => {
    if (hasErrors || predicting) return;
    const id = "lead-" + counter;
    setCounter(counter + 1);
    setCampaign(id);
    setFb("");
    setResult(null);
    setPredicting(true);
    setStage(0);

    let i = 0;
    clearInterval(timer.current);
    timer.current = setInterval(() => {
      i += 1;
      if (i < STEPS.length) setStage(i);
      else clearInterval(timer.current);
    }, 420);

    const body = {
      campaign_id: id,
      tenant_id: Number(form.tenant_id),
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
        sleep(1350),
      ]);
      res = await r.json();
    } catch {
      res = { error: true };
    }
    clearInterval(timer.current);
    setPredicting(false);
    setStage(0);
    setResult(res);
    refreshAudit();
  };

  const feedback = async (converted) => {
    if (!campaign) { setFb("Predict a lead first."); return; }
    try {
      const r = await fetch(`${API}/feedback`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ campaign_id: campaign, converted }) });
      const d = await r.json();
      setFb(`Real outcome submitted — ${d.status} (tenant fulfilled labels: ${d.tenant_fulfilled_count})`);
      refreshAudit();
    } catch {
      setFb("Could not reach the API.");
    }
  };

  const pct = result && !result.error ? result.conversion_probability * 100 : 0;
  const positive = result && result.predicted_converted === 1;

  return (
    <div className="app">
      <header>
        <div>
          <h1>AI Marketing — Federated Lead Conversion Predictor</h1>
          <p>Privacy-preserving continuous learning across multiple tenants</p>
        </div>
        <div className={`status ${online ? "up" : "down"}`}>
          <span className="dot" /> {online ? "API connected" : "API offline"}
        </div>
      </header>

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

          <button className="primary" onClick={predict} disabled={hasErrors || predicting}>
            {predicting ? "Predicting…" : "Predict conversion"}
          </button>
          {hasErrors && <span className="form-note">Fix the highlighted fields to continue.</span>}
          {!hasErrors && campaign && !predicting && <span className="form-note ok">{campaign} registered in the delayed buffer.</span>}
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
                      <span className="tick">{idx < stage ? "done" : idx === stage ? "running" : "queued"}</span>
                      {s}
                    </li>
                  ))}
                </ol>
              </div>
            ) : (
              <div className="result">
                <div className="prob">{result && !result.error ? pct.toFixed(1) + "%" : "—"}</div>
                <div className="bar"><div className="fill" style={{ width: pct + "%", background: positive ? "var(--good)" : "var(--bad)" }} /></div>
                <div className="verdict" style={{ color: !result ? "var(--muted)" : result.error ? "var(--bad)" : positive ? "var(--good)" : "var(--bad)" }}>
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
            <details className="audit">
              <summary>Raw audit response</summary>
              <pre>{audit ? JSON.stringify(audit, null, 2) : "—"}</pre>
            </details>
          </section>
        </div>
      </div>
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
