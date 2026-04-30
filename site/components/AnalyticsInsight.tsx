"use client";

import { motion } from "framer-motion";

const metrics = [
  { value: "+312%", label: "reach anomaly" },
  { value: "41%", label: "hook retention" },
  { value: "2.8x", label: "pillar lift" },
];

const insights = [
  {
    title: "Performance analytics",
    body: "Collects reach, engagement, clicks, timing, post type, and platform response so results are visible in one place.",
  },
  {
    title: "Pattern detection",
    body: "Separates random spikes from repeatable signals, then highlights which topics, formats, and hooks are improving.",
  },
  {
    title: "Next-step decisions",
    body: "Turns statistics into actions: repeat a pillar, change timing, retire weak formats, or escalate unusual performance.",
  },
];

export function AnalyticsInsight() {
  return (
    <section id="analytics-insight" className="relative overflow-hidden">
      <div className="container-x py-20 md:py-28">
        <div className="grid gap-10 lg:grid-cols-[1.05fr_0.95fr] lg:items-center">
          <motion.div
            initial={{ opacity: 0, y: 18, scale: 0.98 }}
            whileInView={{ opacity: 1, y: 0, scale: 1 }}
            viewport={{ once: true, amount: 0.25 }}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
            className="relative order-2 lg:order-1"
          >
            <div className="absolute -left-8 -top-8 h-36 w-36 rounded-full bg-mint/35 blur-3xl" />
            <div className="absolute -bottom-8 -right-8 h-40 w-40 rounded-full bg-sky/40 blur-3xl" />
            <div className="card relative overflow-hidden p-5 md:p-6">
              <div className="flex items-center justify-between border-b border-line pb-4">
                <span className="font-mono text-[11px] uppercase tracking-[0.18em] text-muted">
                  analytics layer
                </span>
                <span className="rounded-full bg-mint/35 px-3 py-1 text-xs text-ink/75">
                  measured
                </span>
              </div>

              <div className="mt-6 grid grid-cols-3 gap-2">
                {metrics.map((metric, index) => (
                  <motion.div
                    key={metric.label}
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
                    <p className="text-2xl font-medium tracking-tight text-ink md:text-3xl">
                      {metric.value}
                    </p>
                    <p className="mt-1 font-mono text-[10px] uppercase tracking-[0.12em] text-muted">
                      {metric.label}
                    </p>
                  </motion.div>
                ))}
              </div>

              <div className="mt-5 space-y-3">
                {insights.map((item, index) => (
                  <motion.article
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
                    <h3 className="text-base font-medium tracking-tight">{item.title}</h3>
                    <p className="mt-1.5 text-[13px] leading-relaxed text-soft">{item.body}</p>
                  </motion.article>
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
              Statistics and analytics
            </span>
            <h2 className="mt-4 max-w-[14ch] text-[clamp(2.1rem,4.8vw,4.4rem)] font-medium leading-[0.98] tracking-tight">
              Analyzes data for reporting and better results.
            </h2>
            <p className="mt-6 max-w-[62ch] text-[15px] leading-relaxed text-soft md:text-base">
              Elon analyzes the statistics behind each post so the team can understand what is
              working, what is underperforming, and where the next opportunity is. The agent does
              not just publish content; it measures outcomes and feeds those insights back into
              planning.
            </p>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
