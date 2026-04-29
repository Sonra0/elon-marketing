"use client";
import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { setJwt } from "../../lib/api";

export default function LoginPage() {
  const [jwt, setLocalJwt] = useState("");
  const router = useRouter();
  return (
    <div className="card" style={{ maxWidth: 540 }}>
      <h1>Log in</h1>
      <p className="muted">
        New here? <Link href="/onboard">Run the onboarding wizard</Link> — it creates a
        tenant, links Telegram, connects Meta + TikTok, and ingests your brand.
      </p>
      <p className="muted" style={{ marginTop: 12 }}>
        Already have a JWT (e.g. from a CLI <code>POST /tenants</code>)? Paste it here.
      </p>
      <textarea
        rows={6}
        placeholder="eyJhbGciOi..."
        value={jwt}
        onChange={(e) => setLocalJwt(e.target.value.trim())}
      />
      <div className="row" style={{ marginTop: 12 }}>
        <button
          className="primary"
          onClick={() => { if (jwt) { setJwt(jwt); router.push("/dashboard"); } }}
        >
          Continue
        </button>
      </div>
    </div>
  );
}
