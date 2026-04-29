"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, createTenant, getJwt, oauthStartUrl, setJwt } from "../../lib/api";

type Step = "tenant" | "telegram" | "meta" | "tiktok" | "ingest" | "done";

export default function Onboard() {
  const router = useRouter();
  const [step, setStep] = useState<Step>("tenant");
  const [name, setName] = useState("");
  const [tenant, setTenant] = useState<{ jwt: string; telegram_link_command: string } | null>(null);
  const [linked, setLinked] = useState(false);
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  const [websiteUrl, setWebsiteUrl] = useState("");
  const [notes, setNotes] = useState("");

  // Resume an in-progress onboarding if a JWT is already set.
  useEffect(() => {
    if (!getJwt()) return;
    (async () => {
      try {
        const me = await api.me();
        if (me.telegram_linked) setStep("meta");
        else setStep("telegram");
        setLinked(me.telegram_linked);
      } catch {
        // bad JWT — start over
      }
    })();
  }, []);

  // Poll for telegram link confirmation while on the telegram step.
  useEffect(() => {
    if (step !== "telegram") return;
    const t = setInterval(async () => {
      try {
        const me = await api.me();
        if (me.telegram_linked) { setLinked(true); setStep("meta"); clearInterval(t); }
      } catch { /* ignore */ }
    }, 3000);
    return () => clearInterval(t);
  }, [step]);

  async function doCreateTenant() {
    setBusy(true); setErr("");
    try {
      const t = await createTenant(name.trim() || "My Brand");
      setJwt(t.jwt);
      setTenant({ jwt: t.jwt, telegram_link_command: t.telegram_link_command });
      setStep("telegram");
    } catch (e: any) { setErr(String(e.message || e)); }
    finally { setBusy(false); }
  }

  async function doIngest() {
    setBusy(true); setErr("");
    try {
      await api.ingest(websiteUrl || undefined, notes || undefined);
      setStep("done");
    } catch (e: any) { setErr(String(e.message || e)); }
    finally { setBusy(false); }
  }

  return (
    <div className="grid" style={{ maxWidth: 720 }}>
      <h1>Set up your tenant</h1>
      <Stepper current={step} />
      {err && <div className="card" style={{ color: "var(--danger)" }}>{err}</div>}

      {step === "tenant" && (
        <section className="card">
          <h2>1. Name your brand</h2>
          <p className="muted">A workspace will be created for this brand. You can add more later.</p>
          <input placeholder="My Brand" value={name} onChange={e => setName(e.target.value)} />
          <div className="row" style={{ marginTop: 12, justifyContent: "flex-end" }}>
            <button className="primary" disabled={busy} onClick={doCreateTenant}>
              {busy ? "Creating…" : "Continue"}
            </button>
          </div>
        </section>
      )}

      {step === "telegram" && tenant && (
        <section className="card">
          <h2>2. Link Telegram</h2>
          <p className="muted">
            Open your bot on Telegram (the one whose token is in your <code>.env</code>),
            send <code>/start</code>, then send the command below.
          </p>
          <pre>{tenant.telegram_link_command}</pre>
          <div className="row" style={{ gap: 8 }}>
            <span className={`tag ${linked ? "ok" : "warn"}`}>
              {linked ? "linked" : "waiting for link…"}
            </span>
          </div>
          <div className="row" style={{ marginTop: 12, justifyContent: "flex-end" }}>
            <button onClick={() => setStep("meta")}>Skip for now</button>
          </div>
        </section>
      )}

      {step === "meta" && (
        <section className="card">
          <h2>3. Connect Meta (Instagram + Facebook)</h2>
          <p className="muted">
            Opens Facebook Login. Grant the requested page + Instagram Business + business-management
            scopes. Each Page (and any IG Business linked to it) is stored with the long-lived
            page token encrypted at rest.
          </p>
          <div className="row" style={{ marginTop: 12, justifyContent: "space-between" }}>
            <button onClick={() => setStep("telegram")}>Back</button>
            <div className="row" style={{ gap: 8 }}>
              <button onClick={() => setStep("tiktok")}>Skip</button>
              <a className="button-link" href={oauthStartUrl("meta")} target="_blank" rel="noreferrer">
                <button className="primary">Connect Meta →</button>
              </a>
              <button onClick={() => setStep("tiktok")}>I&rsquo;m done</button>
            </div>
          </div>
        </section>
      )}

      {step === "tiktok" && (
        <section className="card">
          <h2>4. Connect TikTok</h2>
          <p className="muted">
            Opens TikTok for Developers. Until your app is approved for the
            <code> video.publish </code> scope, we&rsquo;ll capture the token but
            posting will fail; even after approval, every TikTok post requires your
            explicit per-post approval.
          </p>
          <div className="row" style={{ marginTop: 12, justifyContent: "space-between" }}>
            <button onClick={() => setStep("meta")}>Back</button>
            <div className="row" style={{ gap: 8 }}>
              <button onClick={() => setStep("ingest")}>Skip</button>
              <a className="button-link" href={oauthStartUrl("tiktok")} target="_blank" rel="noreferrer">
                <button className="primary">Connect TikTok →</button>
              </a>
              <button onClick={() => setStep("ingest")}>I&rsquo;m done</button>
            </div>
          </div>
        </section>
      )}

      {step === "ingest" && (
        <section className="card">
          <h2>5. Tell Elon about your brand</h2>
          <p className="muted">
            Drop your homepage and any context. Elon fetches the site, extracts
            voice + visuals, and builds <code>BrandMemory v1</code>. You can edit it later.
          </p>
          <input placeholder="https://yourbrand.com" value={websiteUrl}
                 onChange={e => setWebsiteUrl(e.target.value)} />
          <textarea rows={4} placeholder="Notes: industry, audience, what you stand for, anything off-limits"
                    value={notes} onChange={e => setNotes(e.target.value)} />
          <div className="row" style={{ marginTop: 12, justifyContent: "space-between" }}>
            <button onClick={() => setStep("tiktok")}>Back</button>
            <button className="primary" disabled={busy} onClick={doIngest}>
              {busy ? "Queueing…" : "Ingest"}
            </button>
          </div>
        </section>
      )}

      {step === "done" && (
        <section className="card">
          <h2>You&rsquo;re set up.</h2>
          <p>
            Brand ingestion is running in the background. You&rsquo;ll get a
            confirmation card on Telegram when v1 is ready.
          </p>
          <div className="row" style={{ marginTop: 12, justifyContent: "flex-end" }}>
            <button className="primary" onClick={() => router.push("/dashboard")}>
              Go to dashboard
            </button>
          </div>
        </section>
      )}
    </div>
  );
}

function Stepper({ current }: { current: Step }) {
  const order: Step[] = ["tenant", "telegram", "meta", "tiktok", "ingest", "done"];
  const labels: Record<Step, string> = {
    tenant: "Tenant", telegram: "Telegram", meta: "Meta",
    tiktok: "TikTok", ingest: "Brand", done: "Done",
  };
  const idx = order.indexOf(current);
  return (
    <div className="row" style={{ gap: 8, marginBottom: 8 }}>
      {order.map((s, i) => (
        <span key={s} className={`tag ${i <= idx ? "ok" : ""}`} style={{ flex: 1, textAlign: "center" }}>
          {labels[s]}
        </span>
      ))}
    </div>
  );
}
