"use client";

import { motion } from "framer-motion";

const memoryItems = [
  {
    title: "Brand memory",
    body: "Stores voice, audience, product facts, content pillars, and rules about what the brand should never say.",
  },
  {
    title: "Content history",
    body: "Keeps track of previous posts, drafts, approvals, rejections, and the reasoning behind each decision.",
  },
  {
    title: "Performance feedback",
    body: "Uses reach, engagement, anomalies, and operator feedback to understand what should be repeated or avoided.",
  },
];

const loop = ["remember", "create", "measure", "improve"];

export function MemoryFeedbackLoop() {
  return (
    <section id="memory-feedback" className="relative overflow-hidden">
      <div className="container-x py-20 md:py-28">
        <div className="grid gap-10 lg:grid-cols-[0.95fr_1.05fr] lg:items-center">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.65, ease: [0.22, 1, 0.36, 1] }}
          >
            <span className="text-xs uppercase tracking-[0.22em] text-muted">
              Memory and feedback
            </span>
            <h2 className="mt-4 max-w-[14ch] text-[clamp(2.1rem,4.8vw,4.4rem)] font-medium leading-[0.98] tracking-tight">
              The agent remembers, learns, and gets sharper over time.
            </h2>
            <p className="mt-6 max-w-[62ch] text-[15px] leading-relaxed text-soft md:text-base">
              Elon is not a one-shot content generator. It builds memory from previous content,
              human feedback, and performance results, then uses that memory to make the next
              draft more accurate, more on-brand, and more useful.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 18, scale: 0.98 }}
            whileInView={{ opacity: 1, y: 0, scale: 1 }}
            viewport={{ once: true, amount: 0.25 }}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1], delay: 0.08 }}
            className="relative"
          >
            <div className="absolute -left-8 -top-8 h-36 w-36 rounded-full bg-lav/35 blur-3xl" />
            <div className="absolute -bottom-10 -right-8 h-44 w-44 rounded-full bg-coral/30 blur-3xl" />
            <div className="card relative overflow-hidden p-5 md:p-6">
              <div className="flex items-center justify-between border-b border-line pb-4">
                <span className="font-mono text-[11px] uppercase tracking-[0.18em] text-muted">
                  learning loop
                </span>
                <span className="rounded-full bg-lav/35 px-3 py-1 text-xs text-ink/75">
                  persistent
                </span>
              </div>

              <div className="mt-6 grid grid-cols-2 gap-2 md:grid-cols-4">
                {loop.map((item, index) => (
                  <motion.div
                    key={item}
                    initial={{ opacity: 0, y: 10 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, amount: 0.5 }}
                    transition={{
                      duration: 0.45,
                      ease: [0.22, 1, 0.36, 1],
                      delay: index * 0.06,
                    }}
                    className="rounded-2xl border border-line bg-cream/70 p-4 text-center"
                  >
                    <p className="font-mono text-[11px] text-coral">
                      {String(index + 1).padStart(2, "0")}
                    </p>
                    <p className="mt-2 text-sm font-medium text-ink">{item}</p>
                  </motion.div>
                ))}
              </div>

              <div className="mt-5 grid gap-3">
                {memoryItems.map((item, index) => (
                  <motion.article
                    key={item.title}
                    initial={{ opacity: 0, x: 14 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true, amount: 0.5 }}
                    transition={{
                      duration: 0.5,
                      ease: [0.22, 1, 0.36, 1],
                      delay: 0.12 + index * 0.08,
                    }}
                    className="rounded-2xl border border-line bg-bg/75 p-4"
                  >
                    <h3 className="text-base font-medium tracking-tight">{item.title}</h3>
                    <p className="mt-1.5 text-[13px] leading-relaxed text-soft">{item.body}</p>
                  </motion.article>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
