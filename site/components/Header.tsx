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
<a
          href="https://github.com/Sonra0/elon-marketing"
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-2 rounded-full border border-ink/15 bg-white/60 px-3.5 py-1.5 text-xs text-ink/80 transition hover:border-ink/30 hover:bg-white hover:text-ink"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden>
            <path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.1.79-.25.79-.56v-2c-3.2.7-3.87-1.37-3.87-1.37-.52-1.32-1.27-1.67-1.27-1.67-1.04-.71.08-.7.08-.7 1.15.08 1.76 1.18 1.76 1.18 1.02 1.75 2.69 1.25 3.34.95.1-.74.4-1.25.72-1.54-2.55-.29-5.24-1.28-5.24-5.69 0-1.26.45-2.29 1.18-3.1-.12-.29-.51-1.46.11-3.04 0 0 .96-.31 3.16 1.18a10.96 10.96 0 0 1 5.76 0c2.2-1.49 3.16-1.18 3.16-1.18.62 1.58.23 2.75.11 3.04.74.81 1.18 1.84 1.18 3.1 0 4.42-2.69 5.39-5.25 5.68.41.36.78 1.06.78 2.13v3.16c0 .31.21.67.8.56C20.21 21.39 23.5 17.08 23.5 12 23.5 5.65 18.35.5 12 .5z" />
          </svg>
          GitHub
        </a>
      </div>
    </header>
  );
}
