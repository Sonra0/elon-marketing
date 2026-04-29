"use client";

import { motion } from "framer-motion";
import clsx from "clsx";
import { copy } from "@/lib/copy";
import { SectionHead } from "./Steps";

export function Demo() {
  return (
    <section id="demo" className="relative">
      <div className="container-x py-24 md:py-32">
        <SectionHead label="A day with me" title="Brief to live in eleven minutes." />
        <div className="mt-14 grid md:grid-cols-12 gap-10 items-start">
          <div className="md:col-span-5 space-y-5">
            <Bullet emoji="☀️" text="Mornings start with three options. Approve in Telegram or the web." />
            <Bullet emoji="📈" text="Live anomaly alerts when a post breaks out — good or bad." />
            <Bullet emoji="🌙" text="Evenings end with a one-screen digest and tomorrow's plan." />
          </div>
          <div className="md:col-span-7">
            <div className="card overflow-hidden rotate-[0.4deg] hover:rotate-0 transition-transform duration-500">
              <div className="flex items-center justify-between border-b border-line px-4 py-2.5 text-[11px] text-muted">
                <span className="font-mono">@elon · telegram</span>
                <span>chat preview</span>
              </div>
              <div className="p-5 space-y-3">
                {copy.demo.map((m, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 6 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, amount: 0.3 }}
                    transition={{ duration: 0.5, delay: i * 0.12 }}
                    className={clsx("flex flex-col gap-1", m.who === "you" ? "items-end" : "items-start")}
                  >
                    <span className="text-[10px] font-mono text-muted">{m.t}</span>
                    <span className={clsx(
                      "max-w-[80%] px-3.5 py-2 rounded-2xl text-[13px] leading-snug",
                      m.who === "you"
                        ? "bg-ink text-bg rounded-br-sm"
                        : "bg-cream text-ink rounded-bl-sm border border-line"
                    )}>
                      {m.text}
                    </span>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function Bullet({ emoji, text }: { emoji: string; text: string }) {
  return (
    <div className="flex gap-3 items-start">
      <span className="text-xl shrink-0">{emoji}</span>
      <p className="text-ink/85 text-[15px] leading-relaxed">{text}</p>
    </div>
  );
}
