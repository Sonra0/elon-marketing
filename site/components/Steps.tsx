"use client";

import { motion } from "framer-motion";
import { copy } from "@/lib/copy";

const tints: Record<string, string> = {
  mint: "bg-mint/35",
  lav: "bg-lav/35",
  coral: "bg-coral/35",
  sun: "bg-sun/40",
  sky: "bg-sky/40",
  rose: "bg-rose/45",
};

export function Steps() {
  return (
    <section id="how" className="relative">
      <div className="container-x py-24 md:py-32">
        <SectionHead label="How I work" title="Three little steps. One happy loop." />
        <div className="mt-14 grid md:grid-cols-3 gap-4">
          {copy.steps.map((s, i) => (
            <motion.div
              key={s.n}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.3 }}
              transition={{ type: "spring", stiffness: 180, damping: 20, delay: i * 0.08 }}
              className="card card-hover p-7 md:p-8 relative overflow-hidden"
            >
              <div aria-hidden
                   className={"absolute -right-10 -top-10 w-44 h-44 rounded-full blur-2xl " + tints[s.color]} />
              <div className="relative flex items-center justify-between">
                <span className="font-mono text-xs text-soft">{s.n}</span>
                <span className="text-2xl">{s.emoji}</span>
              </div>
              <h3 className="relative mt-7 text-2xl md:text-[26px] font-medium tracking-tight leading-tight">
                {s.title}
              </h3>
              <p className="relative mt-3 text-soft text-[15px] leading-relaxed">
                {s.body}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

export function SectionHead({ label, title }: { label: string; title: string }) {
  return (
    <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-3">
      <span className="text-xs uppercase tracking-[0.22em] text-muted">{label}</span>
      <h2 className="max-w-[24ch] text-[clamp(1.8rem,3.4vw,2.6rem)] font-medium tracking-tight leading-tight">
        {title}
      </h2>
    </div>
  );
}
