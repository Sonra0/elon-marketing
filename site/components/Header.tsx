"use client";

import Link from "next/link";

export function Header() {
  return (
    <header className="fixed inset-x-0 top-0 z-50 bg-bg/80 backdrop-blur-md">
      <div className="container-x flex items-center justify-between h-16">
        <Link href="/" className="flex items-center gap-2.5">
          <span className="grid place-items-center w-7 h-7 rounded-full bg-sun shadow-soft">
            <span className="text-[14px] leading-none">☀️</span>
          </span>
          <span className="font-medium tracking-tight">Elon</span>
        </Link>
        <nav className="hidden md:flex items-center gap-7 text-sm text-soft">
          <a href="#how" className="hover:text-ink transition">How</a>
          <a href="#features" className="hover:text-ink transition">Features</a>
          <a href="#demo" className="hover:text-ink transition">Demo</a>
          <a href="#stack" className="hover:text-ink transition">Stack</a>
        </nav>
        <a
          href="https://conhacks-2026.devpost.com/"
          target="_blank" rel="noreferrer"
          className="text-xs text-soft hover:text-ink transition"
        >
          ConHacks 2026 ↗
        </a>
      </div>
    </header>
  );
}
