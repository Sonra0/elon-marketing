"use client";

import { motion } from "framer-motion";

export function ComingSoon() {
  return (
    <section id="coming-soon" className="relative">
      <div className="container-x py-14 md:py-20">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          className="card relative overflow-hidden p-8 md:p-14"
        >
          <motion.div
            aria-hidden
            className="pointer-events-none absolute -inset-x-20 -top-32 h-72 bg-gradient-to-r from-coral/0 via-coral/25 to-lav/0 blur-3xl"
            initial={{ x: "-30%" }}
            animate={{ x: "30%" }}
            transition={{ duration: 9, repeat: Infinity, repeatType: "mirror", ease: "easeInOut" }}
          />
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(255,156,138,0.08),transparent_60%),radial-gradient(circle_at_80%_80%,rgba(200,182,255,0.10),transparent_55%)]" />

          <div className="relative grid items-center gap-10 md:grid-cols-[auto,1fr] md:gap-14">
            <div className="relative mx-auto md:mx-0">
              <motion.div
                aria-hidden
                className="absolute inset-0 rounded-[2rem] bg-coral/15 blur-2xl"
                animate={{ scale: [1, 1.08, 1], opacity: [0.55, 0.85, 0.55] }}
                transition={{ duration: 3.5, repeat: Infinity, ease: "easeInOut" }}
              />
              <motion.div
                className="relative grid h-40 w-40 place-items-center rounded-[2rem] border border-ink/10 bg-white/80 shadow-soft backdrop-blur md:h-48 md:w-48"
                initial={{ rotate: -4, scale: 0.92 }}
                whileInView={{ rotate: 0, scale: 1 }}
                viewport={{ once: true, amount: 0.4 }}
                transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
                whileHover={{ scale: 1.04 }}
              >
                <motion.svg
                  width="84"
                  height="84"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.4"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="text-ink"
                  initial={{ y: 4, opacity: 0 }}
                  whileInView={{ y: 0, opacity: 1 }}
                  viewport={{ once: true, amount: 0.4 }}
                  transition={{ duration: 0.7, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
                >
                  <motion.path
                    d="M7 10V7a5 5 0 0 1 10 0v3"
                    initial={{ pathLength: 0 }}
                    whileInView={{ pathLength: 1 }}
                    viewport={{ once: true, amount: 0.4 }}
                    transition={{ duration: 1.1, delay: 0.3, ease: [0.22, 1, 0.36, 1] }}
                  />
                  <rect x="4" y="10" width="16" height="11" rx="2.5" />
                  <circle cx="12" cy="15.5" r="1.4" fill="currentColor" stroke="none" />
                  <line x1="12" y1="16.5" x2="12" y2="18.5" />
                </motion.svg>
                <motion.span
                  aria-hidden
                  className="pointer-events-none absolute inset-0 rounded-[2rem] ring-1 ring-coral/0"
                  animate={{ boxShadow: ["0 0 0 0 rgba(255,156,138,0.0)", "0 0 0 14px rgba(255,156,138,0.0)"] }}
                  transition={{ duration: 2.4, repeat: Infinity, ease: "easeOut" }}
                />
              </motion.div>
            </div>

            <div className="relative">
              <motion.span
                initial={{ opacity: 0, y: 8 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, amount: 0.5 }}
                transition={{ duration: 0.5, delay: 0.1 }}
                className="inline-flex items-center gap-2 rounded-full border border-coral/30 bg-coral/10 px-3 py-1 text-[11px] font-mono uppercase tracking-[0.18em] text-coral"
              >
                <span className="h-1.5 w-1.5 rounded-full bg-coral animate-pulse" />
                Coming update
              </motion.span>

              <motion.h2
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, amount: 0.5 }}
                transition={{ duration: 0.6, delay: 0.18, ease: [0.22, 1, 0.36, 1] }}
                className="mt-4 text-[clamp(1.9rem,4vw,3.4rem)] font-medium leading-[1.02] tracking-tight"
              >
                Meta &amp; Google Ads, on autopilot.
              </motion.h2>

              <motion.p
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, amount: 0.5 }}
                transition={{ duration: 0.6, delay: 0.26, ease: [0.22, 1, 0.36, 1] }}
                className="mt-5 max-w-[58ch] text-[15px] leading-relaxed text-soft md:text-base"
              >
                The next release brings paid campaigns into the same loop — Elon will plan, draft,
                approve, and measure ad creative across Meta and Google with the same operator-in-
                the-loop discipline as organic posts.
              </motion.p>

              <motion.div
                initial="hidden"
                whileInView="show"
                viewport={{ once: true, amount: 0.5 }}
                variants={{
                  hidden: {},
                  show: { transition: { staggerChildren: 0.08, delayChildren: 0.32 } },
                }}
                className="mt-7 flex flex-wrap items-center gap-2.5"
              >
                {[
                  { label: "Meta Ads", dot: "bg-sky" },
                  { label: "Google Ads", dot: "bg-sun" },
                  { label: "Locked until launch", dot: "bg-coral" },
                ].map((p) => (
                  <motion.span
                    key={p.label}
                    variants={{
                      hidden: { opacity: 0, y: 8 },
                      show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.22, 1, 0.36, 1] } },
                    }}
                    className="inline-flex items-center gap-2 rounded-full border border-ink/10 bg-white/70 px-3.5 py-1.5 text-xs text-ink/80 shadow-soft backdrop-blur"
                  >
                    <span className={`h-1.5 w-1.5 rounded-full ${p.dot}`} />
                    {p.label}
                  </motion.span>
                ))}
              </motion.div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
