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
  return (
    <div className="gbars">
      {tenants.map((t) => (
        <div className="ggroup" key={t.name}>
          <div className="glabel">{t.name}</div>
          <div className="gset">
            {series.map((s) => (
              <div className="grow" key={s.key}>
                <div className="gtrack">
                  <div className="gfill" style={{ width: `${(t[s.key] / domain) * 100}%`, background: `var(${s.var})` }} />
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
  return (
    <div className="blist">
      {rows.map((r) => (
        <div className="brow" key={r.label}>
          <div className="blabel">{r.label}</div>
          <div className="btrack">
            {r.f1 != null && (
              <div className={`bfill ${r.status || (r.ok === false ? "critical" : "")}`} style={{ width: `${(r.f1 / max) * 100}%` }} />
            )}
          </div>
          <div className="bval">{r.f1 != null ? r.f1.toFixed(4) : nullLabel}</div>
        </div>
      ))}
    </div>
  );
}

export function CompareBars({ rows, unit }) {
  const max = Math.max(...rows.map((r) => r.mb));
  return (
    <div className="blist">
      {rows.map((r, i) => (
        <div className="brow" key={r.label}>
          <div className="blabel">{r.label}</div>
          <div className="btrack">
            <div className="bfill" style={{ width: `${(r.mb / max) * 100}%`, background: i === 0 ? "var(--s1)" : "var(--s2)" }} />
          </div>
          <div className="bval">{r.mb} {unit}</div>
        </div>
      ))}
    </div>
  );
}
