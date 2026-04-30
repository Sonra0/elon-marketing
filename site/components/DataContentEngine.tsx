"use client";

import { motion } from "framer-motion";

const outputs = [
  {
    title: "Automatic draft mode",
    body: "Elon can generate ready-to-review posts on its own by combining analytics, trends, brand rules, and audience evidence.",
  },
  {
    title: "Manual assist mode",
    body: "A human can start with an idea or prompt, and Elon shapes it with evidence from what performed, what the audience cares about, and how the brand should sound.",
  },
  {
    title: "Evidence-based variants",
    body: "Both paths produce captions, hooks, scripts, and platform-specific versions that are grounded in the same data.",
  },
];

export function DataContentEngine() {
  return (
    <section id="data-content" className="relative overflow-hidden">
      <div className="container-x py-20 md:py-28">
        <div className="grid gap-10 lg:grid-cols-[1.05fr_0.95fr] lg:items-center">
          <motion.div
            initial={{ opacity: 0, y: 18, scale: 0.98 }}
            whileInView={{ opacity: 1, y: 0, scale: 1 }}
            viewport={{ once: true, amount: 0.25 }}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
            className="relative order-2 lg:order-1"
          >
            <div className="absolute -left-8 -bottom-8 h-40 w-40 rounded-full bg-rose/45 blur-3xl" />
            <div className="absolute -right-8 -top-8 h-36 w-36 rounded-full bg-mint/35 blur-3xl" />
            <div className="card relative overflow-hidden p-5 md:p-6">
              <div className="flex items-center justify-between border-b border-line pb-4">
                <span className="font-mono text-[11px] uppercase tracking-[0.18em] text-muted">
                  content engine
                </span>
                <span className="rounded-full bg-sun/45 px-3 py-1 text-xs text-ink/75">
                  auto + manual
                </span>
              </div>

              <div className="mt-6 space-y-3">
                {outputs.map((item, index) => (
                  <motion.div
                    key={item.title}
                    initial={{ opacity: 0, x: -12 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true, amount: 0.5 }}
                    transition={{
                      duration: 0.5,
                      ease: [0.22, 1, 0.36, 1],
                      delay: 0.12 + index * 0.08,
                    }}
                    className="rounded-2xl border border-line bg-bg/75 p-4"
                  >
                    <div className="flex items-start gap-3">
                      <span className="font-mono text-xs text-coral">
                        {String(index + 1).padStart(2, "0")}
                      </span>
                      <div>
                        <h3 className="text-base font-medium tracking-tight">{item.title}</h3>
                        <p className="mt-1.5 text-[13px] leading-relaxed text-soft">
                          {item.body}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.65, ease: [0.22, 1, 0.36, 1], delay: 0.08 }}
            className="order-1 lg:order-2"
          >
            <span className="text-xs uppercase tracking-[0.22em] text-muted">
              Data-driven creation
            </span>
            <h2 className="mt-4 max-w-[14ch] text-[clamp(2.1rem,4.8vw,4.4rem)] font-medium leading-[0.98] tracking-tight">
              Content is created from evidence, automatically or manually.
            </h2>
            <p className="mt-6 max-w-[62ch] text-[15px] leading-relaxed text-soft md:text-base">
              Instead of asking a marketer to manually connect analytics, trends, and brand rules,
              Elon uses those signals as the starting point. The agent can produce ready-to-review
              drafts automatically, or help a human create manual content that already knows what
              performed, what the audience cares about, and what the brand should sound like.
            </p>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
