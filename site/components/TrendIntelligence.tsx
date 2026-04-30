"use client";

import { motion } from "framer-motion";

const signals = [
  {
    label: "Platform patterns",
    body: "Tracks format shifts, posting windows, retention cues, and engagement patterns across short-form and feed channels.",
  },
  {
    label: "Trend discovery",
    body: "Actively scans for topics, hooks, competitor moves, and cultural moments that fit the brand before they go stale.",
  },
];

export function TrendIntelligence() {
  return (
    <section id="trend-intelligence" className="relative overflow-hidden">
      <div className="container-x py-20 md:py-28">
        <div className="grid gap-10 lg:grid-cols-[0.95fr_1.05fr] lg:items-center">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.65, ease: [0.22, 1, 0.36, 1] }}
          >
            <span className="text-xs uppercase tracking-[0.22em] text-muted">
              Trend intelligence
            </span>
            <h2 className="mt-4 max-w-[13ch] text-[clamp(2.1rem,4.8vw,4.4rem)] font-medium leading-[0.98] tracking-tight">
              Built to read the algorithm and find trends early.
            </h2>
            <p className="mt-6 max-w-[62ch] text-[15px] leading-relaxed text-soft md:text-base">
              Elon watches how social platforms change over time. It looks for the formats, timing,
              topics, hooks, and competitor movements that algorithms are rewarding, then surfaces
              trend opportunities before they become old news.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 18, scale: 0.98 }}
            whileInView={{ opacity: 1, y: 0, scale: 1 }}
            viewport={{ once: true, amount: 0.25 }}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1], delay: 0.08 }}
            className="relative"
          >
            <div className="absolute -left-8 -top-8 h-36 w-36 rounded-full bg-sky/35 blur-3xl" />
            <div className="absolute -bottom-8 -right-6 h-40 w-40 rounded-full bg-sun/45 blur-3xl" />
            <div className="card relative overflow-hidden p-5 md:p-6">
              <div className="flex items-center justify-between border-b border-line pb-4">
                <span className="font-mono text-[11px] uppercase tracking-[0.18em] text-muted">
                  signal scan
                </span>
                <span className="rounded-full bg-mint/35 px-3 py-1 text-xs text-ink/75">
                  active
                </span>
              </div>

              <div className="mt-5 grid gap-3">
                {signals.map((signal, index) => (
                  <motion.div
                    key={signal.label}
                    initial={{ opacity: 0, x: 14 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true, amount: 0.5 }}
                    transition={{
                      duration: 0.5,
                      ease: [0.22, 1, 0.36, 1],
                      delay: 0.12 + index * 0.08,
                    }}
                    className="rounded-2xl border border-line bg-bg/70 p-4"
                  >
                    <div className="flex items-start gap-3">
                      <span className="mt-1 h-2.5 w-2.5 rounded-full bg-coral shadow-soft" />
                      <div>
                        <h3 className="text-base font-medium tracking-tight">{signal.label}</h3>
                        <p className="mt-1.5 text-[13px] leading-relaxed text-soft">
                          {signal.body}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
