"use client";
import { useEffect, useState } from "react";
import { api, Brand } from "../../lib/api";

export default function BrandPage() {
  const [brand, setBrand] = useState<Brand | null | undefined>(undefined);
  const [err, setErr] = useState("");
  const [websiteUrl, setWebsiteUrl] = useState("");
  const [notes, setNotes] = useState("");
  const [busy, setBusy] = useState(false);

  async function load() {
    try { setErr(""); setBrand(await api.brand()); }
    catch (e: any) { setErr(String(e.message || e)); }
  }
  useEffect(() => { load(); }, []);

  async function ingest() {
    setBusy(true); setErr("");
    try {
      await api.ingest(websiteUrl || undefined, notes || undefined);
      setWebsiteUrl(""); setNotes("");
      setTimeout(load, 4000);
    } catch (e: any) { setErr(String(e.message || e)); }
    finally { setBusy(false); }
  }

  return (
    <div className="grid">
      <h1>Brand memory</h1>
      {err && <div className="card" style={{ color: "var(--danger)" }}>{err}</div>}

      <section className="card">
        <h2>Trigger ingest</h2>
        <div className="grid" style={{ gridTemplateColumns: "1fr 1fr", gap: 8 }}>
          <input placeholder="https://yourbrand.com" value={websiteUrl}
                 onChange={e => setWebsiteUrl(e.target.value)} />
          <input placeholder="Notes (industry, audience hints, …)" value={notes}
                 onChange={e => setNotes(e.target.value)} />
        </div>
        <div className="row" style={{ marginTop: 10, justifyContent: "flex-end" }}>
          <button className="primary" disabled={busy} onClick={ingest}>
            {busy ? "Queueing…" : "Ingest"}
          </button>
        </div>
      </section>

      {brand === undefined && <div className="card muted">Loading…</div>}
      {brand === null && <div className="card muted">No brand memory yet.</div>}
      {brand && (
        <section className="card">
          <h2>v{brand.version}</h2>
          <div className="grid" style={{ gridTemplateColumns: "1fr 1fr" }}>
            <div>
              <h3>Positioning</h3>
              <pre>{JSON.stringify(brand.positioning_json, null, 2)}</pre>
              <h3>Voice</h3>
              <pre>{JSON.stringify(brand.voice_json, null, 2)}</pre>
              <h3>Forbidden</h3>
              <pre>{JSON.stringify(brand.forbidden_json, null, 2)}</pre>
            </div>
            <div>
              <h3>Pillars</h3>
              <pre>{JSON.stringify(brand.pillars_json, null, 2)}</pre>
              <h3>Audience</h3>
              <pre>{JSON.stringify(brand.audience_json, null, 2)}</pre>
              <h3>Visual</h3>
              <pre>{JSON.stringify(brand.visual_json, null, 2)}</pre>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
