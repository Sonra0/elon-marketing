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
        <BigElon />

        <motion.h1
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1], delay: 0.18 }}
          className="mt-7 mx-auto max-w-[18ch] text-[clamp(2.6rem,6.4vw,5rem)]
                     leading-[1.02] tracking-tight font-semibold"
          style={{ fontFamily: '"Bricolage Grotesque", Inter, system-ui, sans-serif' }}
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
          <a href="/architecture.html" target="_blank" rel="noreferrer" className="btn btn-primary">View architecture →</a>
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

function BigElon() {
  const letters = ["E", "l", "o", "n"];
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
      className="relative mx-auto inline-flex select-none items-center gap-3"
    >
      <span className="relative inline-flex h-2 w-2">
        <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-coral/60" />
        <span className="relative inline-flex h-2 w-2 rounded-full bg-coral" />
      </span>

      <span
        aria-label="Elon"
        className="flex items-baseline text-[clamp(2.6rem,5.4vw,4rem)] font-bold leading-none tracking-tight text-ink"
      >
        {letters.map((ch, i) => (
          <motion.span
            key={i}
            initial={{ y: 14, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{
              duration: 0.55,
              ease: [0.22, 1, 0.36, 1],
              delay: 0.08 + i * 0.05,
            }}
            className="inline-block"
          >
            {ch}
          </motion.span>
        ))}
      </span>

      <motion.span
        initial={{ opacity: 0, scale: 0.5, rotate: -25 }}
        animate={{ opacity: 1, scale: 1, rotate: 0 }}
        transition={{ type: "spring", stiffness: 240, damping: 14, delay: 0.35 }}
        className="inline-block text-4xl md:text-5xl"
      >
        <motion.span
          className="inline-block origin-[70%_80%]"
          animate={{ rotate: [0, 16, -8, 16, 0] }}
          transition={{ duration: 1.4, repeat: Infinity, repeatDelay: 2.6, ease: "easeInOut" }}
        >
          👽
        </motion.span>
      </motion.span>
    </motion.div>
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
