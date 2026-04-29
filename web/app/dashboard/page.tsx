"use client";
import { useEffect, useState } from "react";
import { api, Post } from "../../lib/api";

type Spend = { tenant_id: string; period_usd: number; budget_usd: number; pct_of_budget: number };
type Connector = { platform: string; handle: string | null; status: string };

export default function Dashboard() {
  const [spend, setSpend] = useState<Spend | null>(null);
  const [connectors, setConnectors] = useState<Connector[]>([]);
  const [recent, setRecent] = useState<Post[]>([]);
  const [draftBrief, setDraftBrief] = useState("");
  const [draftPlatform, setDraftPlatform] = useState("ig");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  async function load() {
    try {
      setErr("");
      const [s, c, p] = await Promise.all([api.spend(), api.connectors(), api.posts()]);
      setSpend(s); setConnectors(c); setRecent(p.slice(0, 8));
    } catch (e: any) { setErr(String(e.message || e)); }
  }
  useEffect(() => { load(); }, []);

  async function queueDraft() {
    setBusy(true); setErr("");
    try {
      await api.draft(draftBrief, draftPlatform);
      setDraftBrief("");
      setTimeout(load, 1500);
    } catch (e: any) { setErr(String(e.message || e)); }
    finally { setBusy(false); }
  }

  return (
    <div className="grid" style={{ gridTemplateColumns: "1fr 1fr" }}>
      {err && <div className="card" style={{ gridColumn: "1 / -1", color: "var(--danger)" }}>{err}</div>}

      <section className="card">
        <h2>Spend (this period)</h2>
        {spend ? (
          <>
            <div style={{ fontSize: 24 }}>
              ${spend.period_usd.toFixed(2)}{" "}
              <span className="muted">/ ${spend.budget_usd.toFixed(0)}</span>
            </div>
            <div className="muted">
              {Math.round(spend.pct_of_budget * 100)}% of monthly cap
            </div>
          </>
        ) : <span className="muted">Loading…</span>}
      </section>

      <section className="card">
        <h2>Connected accounts</h2>
        {connectors.length === 0 ? <span className="muted">None yet.</span> :
          connectors.map((c, i) => (
            <div key={i} className="row" style={{ justifyContent: "space-between" }}>
              <span><strong>{c.platform.toUpperCase()}</strong> {c.handle || "—"}</span>
              <span className={`tag ${c.status === "connected" ? "ok" : "warn"}`}>{c.status}</span>
            </div>
          ))
        }
      </section>

      <section className="card" style={{ gridColumn: "1 / -1" }}>
        <h2>Quick draft</h2>
        <div className="row" style={{ alignItems: "flex-start", gap: 12 }}>
          <select value={draftPlatform} onChange={(e) => setDraftPlatform(e.target.value)} style={{ width: 120 }}>
            <option value="ig">Instagram</option>
            <option value="tiktok">TikTok</option>
            <option value="fb">Facebook</option>
          </select>
          <textarea
            rows={2}
            placeholder="Tell Elon what to draft (or leave blank for a brand-led pick)"
            value={draftBrief}
            onChange={(e) => setDraftBrief(e.target.value)}
          />
          <button className="primary" disabled={busy} onClick={queueDraft}>
            {busy ? "Queueing…" : "Draft"}
          </button>
        </div>
      </section>

      <section className="card" style={{ gridColumn: "1 / -1" }}>
        <h2>Recent posts</h2>
        {recent.length === 0 ? <span className="muted">No posts yet.</span> :
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th align="left">Platform</th>
                <th align="left">State</th>
                <th align="left">Idea</th>
                <th align="left">Created</th>
              </tr>
            </thead>
            <tbody>
              {recent.map((p) => (
                <tr key={p.id} style={{ borderTop: "1px solid var(--border)" }}>
                  <td>{p.platform.toUpperCase()}</td>
                  <td><span className={`tag ${p.state === "published" ? "ok" : (p.state === "rejected" || p.state === "failed" ? "warn" : "")}`}>{p.state}</span></td>
                  <td>{p.idea.slice(0, 80)}</td>
                  <td className="muted">{new Date(p.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        }
      </section>
    </div>
  );
}
