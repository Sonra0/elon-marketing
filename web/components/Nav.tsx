"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { clearJwt, getJwt } from "../lib/api";
import { useEffect, useState } from "react";

export function Nav() {
  const pathname = usePathname();
  const router = useRouter();
  const [authed, setAuthed] = useState(false);
  useEffect(() => { setAuthed(!!getJwt()); }, [pathname]);
  const linkClass = (href: string) => (pathname?.startsWith(href) ? "active" : "");
  return (
    <nav className="top">
      <strong>Elon</strong>
      {authed && <>
        <Link href="/dashboard" className={linkClass("/dashboard")}>Dashboard</Link>
        <Link href="/drafts" className={linkClass("/drafts")}>Drafts</Link>
        <Link href="/brand" className={linkClass("/brand")}>Brand</Link>
      </>}
      <div style={{ marginLeft: "auto" }}>
        {authed
          ? <button onClick={() => { clearJwt(); router.push("/login"); }}>Log out</button>
          : <>
              <Link href="/onboard">Onboard</Link>
              <span style={{ margin: "0 8px", color: "var(--muted)" }}>|</span>
              <Link href="/login">Log in</Link>
            </>}
      </div>
    </nav>
  );
}
