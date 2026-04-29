"use client";

import { motion } from "framer-motion";
import { copy } from "@/lib/copy";

export function Hero() {
  return (
    <section className="relative pt-36 pb-24 md:pt-44 md:pb-32 overflow-hidden">
      {/* warm color blobs */}
      <Blob className="left-[-10%] top-24 w-[36rem] h-[36rem] bg-sun/40" />
      <Blob className="right-[-12%] top-48 w-[34rem] h-[34rem] bg-rose/45" />
      <Blob className="left-1/3 top-[28rem] w-[26rem] h-[26rem] bg-mint/40" />

      <div className="relative container-x text-center">
        <motion.span
          initial={{ opacity: 0, y: 6, rotate: -3 }}
          animate={{ opacity: 1, y: 0, rotate: -3 }}
          transition={{ type: "spring", stiffness: 220, damping: 18, delay: 0.1 }}
          className="sticker bg-white inline-block"
        >
          {copy.hero.eyebrow}
        </motion.span>

        <motion.h1
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1], delay: 0.18 }}
          className="mt-7 mx-auto max-w-[18ch] text-[clamp(2.6rem,6.4vw,5rem)]
                     leading-[1.02] tracking-tightest font-medium"
        >
          {copy.hero.title_pre}{" "}
          <span className="display italic font-normal text-coral">{copy.hero.title_em}</span>{" "}
          {copy.hero.title_post}
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1], delay: 0.26 }}
          className="mt-7 mx-auto max-w-[60ch] text-soft text-base md:text-lg leading-relaxed"
        >
          {copy.hero.subtitle}
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1], delay: 0.34 }}
          className="mt-10 flex flex-wrap items-center justify-center gap-3"
        >
          <a href="#how" className="btn btn-primary">Show me how →</a>
          <a href="https://conhacks-2026.devpost.com/" target="_blank" rel="noreferrer"
             className="btn btn-ghost">ConHacks 2026 ↗</a>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1], delay: 0.5 }}
          className="mt-16 mx-auto max-w-[640px]"
        >
          <PreviewCard />
        </motion.div>
      </div>
    </section>
  );
}

function Blob({ className }: { className: string }) {
  return (
    <div
      aria-hidden
      className={"absolute rounded-full blur-3xl pointer-events-none " + className}
    />
  );
}

function PreviewCard() {
  return (
    <div className="card text-left rotate-[-0.3deg] hover:rotate-0 transition-transform duration-500">
      <div className="flex items-center justify-between border-b border-line px-4 py-2.5 text-[11px] text-muted">
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-coral" />
          <span className="w-2 h-2 rounded-full bg-sun" />
          <span className="w-2 h-2 rounded-full bg-mint" />
        </div>
        <span className="font-mono">@elon · telegram</span>
        <span className="flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-mint animate-pulse" /> here
        </span>
      </div>
      <div className="p-5 space-y-3">
        <Bubble who="elon" text="Morning! 3 drafts ready ☕" />
        <Bubble who="you" text="approve all" />
        <Bubble who="elon" text="On it. IG 09:00 · TT 13:00 · FB 17:00 ✓" />
      </div>
    </div>
  );
}

function Bubble({ who, text }: { who: "elon" | "you"; text: string }) {
  const me = who === "you";
  return (
    <div className={"flex " + (me ? "justify-end" : "justify-start")}>
      <span className={
        "max-w-[80%] px-3.5 py-2 rounded-2xl text-[13px] leading-snug " +
        (me ? "bg-ink text-bg rounded-br-sm" : "bg-cream text-ink rounded-bl-sm border border-line")
      }>
        {text}
      </span>
    </div>
  );
}
