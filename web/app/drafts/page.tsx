"use client";
import { useEffect, useState } from "react";
import { api, Post } from "../../lib/api";

export default function Drafts() {
  const [drafts, setDrafts] = useState<Post[]>([]);
  const [err, setErr] = useState("");
  const [busyId, setBusyId] = useState<string | null>(null);

  async function load() {
    try {
      setErr("");
      const all = await api.posts();
      setDrafts(all.filter(p => ["draft", "review", "approved"].includes(p.state)));
    } catch (e: any) { setErr(String(e.message || e)); }
  }
  useEffect(() => { load(); }, []);

  async function decide(id: string, decision: "approve" | "reject") {
    setBusyId(id);
    try {
      await api.decide(id, decision);
      await load();
    } catch (e: any) { setErr(String(e.message || e)); }
    finally { setBusyId(null); }
  }

  return (
    <div className="grid">
      <h1>Pending drafts</h1>
      {err && <div className="card" style={{ color: "var(--danger)" }}>{err}</div>}
      {drafts.length === 0 && <div className="card muted">No drafts in review.</div>}
      {drafts.map(p => (
        <div key={p.id} className="card">
          <div className="row" style={{ justifyContent: "space-between" }}>
            <div className="row">
              <strong>{p.platform.toUpperCase()}</strong>
              <span className={`tag ${p.requires_human_review ? "warn" : ""}`}>
                {p.requires_human_review ? "human review required" : "ready"}
              </span>
              <span className="tag">{p.state}</span>
            </div>
            <span className="muted">{new Date(p.created_at).toLocaleString()}</span>
          </div>
          <h3 style={{ margin: "10px 0 4px" }}>{p.idea}</h3>
          <div className="muted" style={{ fontSize: 13 }}>{p.hook}</div>
          <pre style={{ marginTop: 8 }}>{p.caption}</pre>
          {p.cta && <div><strong>CTA:</strong> {p.cta}</div>}
          <div className="row" style={{ marginTop: 10, gap: 10, justifyContent: "flex-end" }}>
            <button className="danger" disabled={busyId === p.id} onClick={() => decide(p.id, "reject")}>
              Reject
            </button>
            <button className="primary" disabled={busyId === p.id || p.state === "approved"}
                    onClick={() => decide(p.id, "approve")}>
              {p.platform === "tiktok" ? "Approve TikTok post" : "Approve"}
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
