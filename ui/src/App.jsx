import { useEffect, useState, useCallback } from "react";

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

export default function App() {
  const [form, setForm] = useState(BASE);
  const [result, setResult] = useState(null);
  const [campaign, setCampaign] = useState(null);
  const [counter, setCounter] = useState(1);
  const [fb, setFb] = useState("");
  const [audit, setAudit] = useState(null);
  const [online, setOnline] = useState(false);

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const refreshAudit = useCallback(async () => {
    try {
      const r = await fetch(`${API}/audit`);
      const d = await r.json();
      setAudit(d);
      setOnline(true);
    } catch {
      setOnline(false);
    }
  }, []);

  useEffect(() => { refreshAudit(); }, [refreshAudit]);

  const predict = async () => {
    const id = "lead-" + counter;
    setCounter(counter + 1);
    setCampaign(id);
    setFb("");
    const body = {
      campaign_id: id,
      tenant_id: Number(form.tenant_id),
      lead_origin: form.lead_origin, occupation: form.occupation,
      last_activity: form.last_activity, last_notable_activity: form.last_notable_activity,
      specialization: form.specialization,
      total_visits: Number(form.total_visits), time_on_site: Number(form.time_on_site),
      page_views_per_visit: Number(form.page_views_per_visit), activity_score: Number(form.activity_score),
    };
    try {
      const r = await fetch(`${API}/predict`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
      setResult(await r.json());
      refreshAudit();
    } catch {
      setResult({ error: true });
    }
  };

  const feedback = async (converted) => {
    if (!campaign) { setFb("Predict a lead first."); return; }
    const r = await fetch(`${API}/feedback`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ campaign_id: campaign, converted }) });
    const d = await r.json();
    setFb(`Real outcome submitted → ${d.status} (tenant fulfilled labels: ${d.tenant_fulfilled_count})`);
    refreshAudit();
  };

  const pct = result && !result.error ? (result.conversion_probability * 100) : 0;
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
          <h2>Lead details</h2>
          <div className="presets">
            <button className="ghost" onClick={() => setForm({ ...form, ...HIGH })}>Load high-intent lead</button>
            <button className="ghost" onClick={() => setForm({ ...form, ...LOW })}>Load low-intent lead</button>
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
            <Num label="Total visits" value={form.total_visits} onChange={set("total_visits")} />
            <Num label="Time on site (sec)" value={form.time_on_site} onChange={set("time_on_site")} />
            <Num label="Page views / visit" value={form.page_views_per_visit} step="0.1" onChange={set("page_views_per_visit")} />
            <Num label="Activity score" value={form.activity_score} onChange={set("activity_score")} />
          </div>
          <button className="primary" onClick={predict}>Predict conversion</button>
          {campaign && <span className="muted"> {campaign} registered in delayed buffer</span>}
        </section>

        <div className="col">
          <section className="card">
            <h2>Prediction</h2>
            <div className="result">
              <div className="prob">{result && !result.error ? pct.toFixed(1) + "%" : "—"}</div>
              <div className="bar"><div className="fill" style={{ width: pct + "%", background: positive ? "var(--good)" : "var(--bad)" }} /></div>
              <div className="verdict" style={{ color: !result ? "var(--muted)" : positive ? "var(--good)" : "var(--bad)" }}>
                {!result ? "Enter a lead and predict" : result.error ? "API not reachable" : positive ? "Likely to CONVERT" : "Unlikely to convert"}
              </div>
              {result && !result.error && <div className="muted">decision threshold {result.threshold}</div>}
            </div>
            <div className="presets">
              <button className="good" onClick={() => feedback(1)}>Outcome: Converted</button>
              <button className="bad" onClick={() => feedback(0)}>Outcome: Not converted</button>
            </div>
            {fb && <div className="muted fb">{fb}</div>}
          </section>

          <section className="card">
            <h2>System status (live from API)</h2>
            <Row k="Federated rounds completed" v={audit ? audit.federated_rounds.length : "—"} />
            <Row k="Differential privacy" v={audit ? <span className={`pill ${audit.differential_privacy ? "on" : "off"}`}>{audit.differential_privacy ? "ON" : "OFF"}</span> : "—"} />
            <Row k="Predictions awaiting delayed label" v={audit ? audit.buffer_pending : "—"} />
            <div className="muted" style={{ marginTop: 10 }}>Raw audit response</div>
            <pre>{audit ? JSON.stringify(audit, null, 2) : "—"}</pre>
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
function Num({ label, value, onChange, step }) {
  return <Field label={label}><input type="number" step={step || "1"} value={value} onChange={onChange} /></Field>;
}
function Row({ k, v }) {
  return <div className="kv"><span>{k}</span><b>{v}</b></div>;
}
