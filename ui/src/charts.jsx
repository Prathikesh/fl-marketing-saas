import { useState, useEffect } from "react";

function useGrow() {
  const [g, setG] = useState(0);
  useEffect(() => {
    const id = setTimeout(() => setG(1), 80);
    return () => clearTimeout(id);
  }, []);
  return g;
}

export function Gauge({ pct, color, idle }) {
  const r = 92, cx = 110, cy = 110;
  const circ = Math.PI * r;
  const path = `M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`;
  const shown = idle ? 0 : pct;
  return (
    <svg viewBox="0 0 220 124" className="gauge" role="img" aria-label={`conversion probability ${pct.toFixed(1)}%`}>
      <path d={path} className="gauge-bg" />
      <path d={path} className="gauge-fg" style={{ stroke: color, strokeDasharray: `${(circ * shown) / 100} ${circ}` }} />
    </svg>
  );
}

export function Legend({ series }) {
  return (
    <div className="legend">
      {series.map((s) => (
        <span className="legend-item" key={s.key}>
          <span className="swatch" style={{ background: `var(${s.var})` }} />
          {s.label}
        </span>
      ))}
    </div>
  );
}

export function GroupedBars({ tenants, series, domain = 1 }) {
  const g = useGrow();
  return (
    <div className="gbars">
      {tenants.map((t) => (
        <div className="ggroup" key={t.name}>
          <div className="glabel">{t.name}</div>
          <div className="gset">
            {series.map((s) => (
              <div className="grow" key={s.key} title={`${s.label}: ${t[s.key].toFixed(4)}`}>
                <div className="gtrack">
                  <div className="gfill" style={{ width: `${(t[s.key] / domain) * 100 * g}%`, background: `var(${s.var})` }} />
                </div>
                <span className="gval">{t[s.key].toFixed(3)}</span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

export function BarList({ rows, max = 1, nullLabel = "—" }) {
  const g = useGrow();
  return (
    <div className="blist">
      {rows.map((r) => (
        <div className="brow" key={r.label} title={r.f1 != null ? `${r.label}: ${r.f1.toFixed(4)}` : `${r.label}: ${nullLabel}`}>
          <div className="blabel">{r.label}</div>
          <div className="btrack">
            {r.f1 != null && (
              <div className={`bfill ${r.status || (r.ok === false ? "critical" : "")}`} style={{ width: `${(r.f1 / max) * 100 * g}%` }} />
            )}
          </div>
          <div className="bval">{r.f1 != null ? r.f1.toFixed(4) : nullLabel}</div>
        </div>
      ))}
    </div>
  );
}

export function CompareBars({ rows, unit }) {
  const g = useGrow();
  const max = Math.max(...rows.map((r) => r.mb));
  return (
    <div className="blist">
      {rows.map((r, i) => (
        <div className="brow" key={r.label} title={`${r.label}: ${r.mb} ${unit}`}>
          <div className="blabel">{r.label}</div>
          <div className="btrack">
            <div className="bfill" style={{ width: `${(r.mb / max) * 100 * g}%`, background: i === 0 ? "var(--s1)" : "var(--s2)" }} />
          </div>
          <div className="bval">{r.mb} {unit}</div>
        </div>
      ))}
    </div>
  );
}

// Zoomed comparison for the ablation (F1 values cluster between ~0.75 and ~0.79).
export function AblationBars({ rows, lo = 0.74, hi = 0.8 }) {
  const g = useGrow();
  const label = (v) => (v === "best" ? "winner" : v === "flat" ? "no gain" : "lower");
  return (
    <div className="ablist">
      {rows.map((r) => {
        const w = Math.max(2, Math.min(100, ((r.f1 - lo) / (hi - lo)) * 100)) * g;
        const cls = r.verdict === "best" ? "win" : r.verdict === "flat" ? "flat" : "low";
        return (
          <div className="abrow" key={r.change} title={`${r.change}: ${r.f1.toFixed(4)}`}>
            <div className="ablabel">{r.change}</div>
            <div className="abtrack">
              <div className={`abfill ${cls}`} style={{ width: `${w}%` }} />
            </div>
            <div className="abval">{r.f1.toFixed(4)}</div>
            <div className={`abtag ${cls}`}>{label(r.verdict)}</div>
          </div>
        );
      })}
      <div className="abaxis"><span>{lo.toFixed(2)}</span><span>axis zoomed to show differences</span><span>{hi.toFixed(2)}</span></div>
    </div>
  );
}
