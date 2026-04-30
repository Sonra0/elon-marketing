"use client";

import { motion, useReducedMotion } from "framer-motion";

const flow = [
  {
    step: "01",
    title: "Ingest the brand",
    body: "Elon starts from links, notes, previous posts, and operator input. The system turns messy context into brand memory, voice rules, audience signals, and reusable constraints.",
    detail: "BrandMemory + RAG + encrypted tenant data",
  },
  {
    step: "02",
    title: "Plan the calendar",
    body: "The planner picks platform-specific ideas, cadence, channel fit, and approval needs. It keeps TikTok conservative and makes every publish auditable.",
    detail: "strategy planner + policy gates + spend meter",
  },
  {
    step: "03",
    title: "Create the assets",
    body: "Drafts, captions, variants, and media requests move through workers. The operator sees only the useful surface: what is ready, why it fits, and what needs approval.",
    detail: "Celery workers + media adapters + MinIO",
  },
  {
    step: "04",
    title: "Approve, publish, learn",
    body: "Approved posts go through official APIs. Analytics are pulled back into the loop so the next plan reflects what actually happened.",
    detail: "Meta/TikTok OAuth + analytics aggregation",
  },
];

const features = [
  ["Brand memory", "Keeps voice, positioning, audience, and product facts consistent across campaigns."],
  ["Approval control", "Every MVP post waits for a human decision, with explicit TikTok confirmation."],
  ["Signal response", "Flags anomalies, post performance, and trend opportunities without creating noise."],
  ["Multi-channel output", "Shapes the same strategy into Instagram, TikTok, Facebook, Telegram, and web review flows."],
  ["Cost guardrails", "Tracks tenant spend and uses prompt caching so autonomous work stays bounded."],
  ["Self-hosted core", "FastAPI, workers, database, storage, and scheduler run in a deployable Docker stack."],
];

const stack = [
  "Next.js site",
  "FastAPI",
  "Postgres + pgvector",
  "Redis",
  "Celery + Beat",
  "MinIO",
  "OAuth",
  "Official social APIs",
  "Encrypted tokens",
  "Claude planning",
];

const outcomes = [
  {
    value: "11 min",
    label: "brief to scheduled draft",
    body: "The tool compresses research, planning, copy, and approval into one reviewable loop.",
  },
  {
    value: "3x",
    label: "platform-specific output",
    body: "One brand strategy becomes distinct Instagram, TikTok, and Facebook execution.",
  },
  {
    value: "$50",
    label: "monthly soft cap",
    body: "Spend tracking and prompt caching keep autonomy inside practical operating limits.",
  },
  {
    value: "0",
    label: "blind publishing",
    body: "Every MVP post requires approval, with explicit confirmation before TikTok publishing.",
  },
];

export default function DemoPage() {
  const reducedMotion = useReducedMotion();
  const reveal = {
    initial: reducedMotion ? false : { opacity: 0, y: 18 },
    whileInView: { opacity: 1, y: 0 },
    viewport: { once: true, amount: 0.28 },
    transition: { duration: 0.55, ease: [0.22, 1, 0.36, 1] },
  };

  return (
    <main className="relative overflow-hidden pt-24">
      <section id="demo" className="container-x min-h-[calc(100vh-6rem)] py-12 md:py-20">
        <div className="grid gap-10 lg:grid-cols-[0.95fr_1.05fr] lg:items-center">
          <motion.div
            initial={reducedMotion ? false : { opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.65, ease: [0.22, 1, 0.36, 1] }}
          >
            <p className="font-mono text-xs uppercase tracking-[0.28em] text-muted">
              Product demo
            </p>
            <h1 className="mt-5 max-w-[11ch] text-[clamp(3rem,8vw,6.7rem)] font-medium leading-[0.92] tracking-tight">
              Elon in one page.
            </h1>
            <p className="mt-7 max-w-[58ch] text-base leading-relaxed text-soft md:text-lg">
              An autonomous brand marketing agent that learns a brand, plans daily content,
              creates drafts, waits for approval, publishes through official APIs, and learns
              from performance.
            </p>
            <div className="mt-9 flex flex-wrap gap-3">
              <a href="#flow" className="btn btn-primary">
                Start walkthrough
              </a>
              <a href="#technical" className="btn btn-ghost">
                View stack
              </a>
            </div>
          </motion.div>

          <motion.div
            initial={reducedMotion ? false : { opacity: 0, scale: 0.96, y: 18 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ duration: 0.75, ease: [0.22, 1, 0.36, 1], delay: 0.12 }}
            className="relative"
          >
            <div className="absolute -left-8 -top-8 h-36 w-36 rounded-full bg-mint/40 blur-3xl" />
            <div className="absolute -bottom-10 -right-10 h-44 w-44 rounded-full bg-coral/35 blur-3xl" />
            <div className="relative overflow-hidden rounded-[2rem] border border-line bg-white shadow-pop">
              <div className="flex items-center justify-between border-b border-line px-5 py-3 font-mono text-[11px] text-muted">
                <span>elon.pipeline</span>
                <span className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-mint" />
                  live demo
                </span>
              </div>
              <div className="grid gap-0 md:grid-cols-[0.9fr_1.1fr]">
                <div className="border-b border-line bg-cream/55 p-5 md:border-b-0 md:border-r">
                  <ConsoleLine label="signal" value="3 competitor launches detected" />
                  <ConsoleLine label="memory" value="voice: direct, useful, optimistic" />
                  <ConsoleLine label="plan" value="IG carousel + TikTok script + FB recap" />
                  <ConsoleLine label="gate" value="waiting for operator approval" strong />
                </div>
                <div className="p-5">
                  <div className="rounded-2xl border border-line bg-bg p-4">
                    <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-muted">
                      Draft preview
                    </p>
                    <h2 className="mt-3 text-2xl font-medium tracking-tight">
                      Today&apos;s strongest angle
                    </h2>
                    <p className="mt-3 text-sm leading-relaxed text-soft">
                      Turn a product update into a customer story, then adapt it for each
                      channel with one approval path.
                    </p>
                    <div className="mt-5 grid grid-cols-3 gap-2 text-center text-[11px] text-soft">
                      <Metric label="IG" value="09:00" />
                      <Metric label="TT" value="13:00" />
                      <Metric label="FB" value="17:00" />
                    </div>
                  </div>
                  <div className="mt-4 flex gap-2">
                    <span className="rounded-full bg-ink px-3 py-1.5 text-xs text-bg">Approve</span>
                    <span className="rounded-full border border-line bg-white px-3 py-1.5 text-xs text-soft">
                      Request changes
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      <section id="flow" className="container-x py-20 md:py-28">
        <motion.div {...reveal} className="max-w-[760px]">
          <p className="font-mono text-xs uppercase tracking-[0.28em] text-muted">Tool flow</p>
          <h2 className="mt-4 text-4xl font-medium tracking-tight md:text-6xl">
            From raw context to approved publishing.
          </h2>
        </motion.div>
        <div className="mt-14 grid gap-4">
          {flow.map((item, index) => (
            <motion.article
              key={item.title}
              {...reveal}
              transition={{ duration: 0.55, delay: index * 0.05, ease: [0.22, 1, 0.36, 1] }}
              className="grid gap-5 rounded-[1.75rem] border border-line bg-white p-5 shadow-soft md:grid-cols-[7rem_1fr_18rem] md:items-center md:p-7"
            >
              <span className="font-mono text-3xl text-coral">{item.step}</span>
              <div>
                <h3 className="text-2xl font-medium tracking-tight">{item.title}</h3>
                <p className="mt-2 max-w-[70ch] text-sm leading-relaxed text-soft md:text-[15px]">
                  {item.body}
                </p>
              </div>
              <p className="rounded-2xl bg-cream px-4 py-3 font-mono text-xs leading-relaxed text-ink/75">
                {item.detail}
              </p>
            </motion.article>
          ))}
        </div>
      </section>

      <section id="features" className="container-x py-20 md:py-28">
        <motion.div {...reveal} className="flex flex-col justify-between gap-5 md:flex-row md:items-end">
          <div>
            <p className="font-mono text-xs uppercase tracking-[0.28em] text-muted">Features</p>
            <h2 className="mt-4 text-4xl font-medium tracking-tight md:text-6xl">
              General enough to demo. Technical enough to trust.
            </h2>
          </div>
          <p className="max-w-[34ch] text-sm leading-relaxed text-soft">
            Built for founders and small teams that need consistent marketing without giving up
            final control.
          </p>
        </motion.div>
        <div className="mt-12 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {features.map(([title, body], index) => (
            <motion.article
              key={title}
              {...reveal}
              transition={{ duration: 0.5, delay: (index % 3) * 0.05, ease: [0.22, 1, 0.36, 1] }}
              className="min-h-44 rounded-[1.5rem] border border-line bg-white p-6 shadow-soft transition-transform duration-300 hover:-translate-y-1"
            >
              <div className="h-1.5 w-12 rounded-full bg-sun" />
              <h3 className="mt-5 text-xl font-medium tracking-tight">{title}</h3>
              <p className="mt-3 text-sm leading-relaxed text-soft">{body}</p>
            </motion.article>
          ))}
        </div>
      </section>

      <section id="technical" className="border-y border-line bg-white/60">
        <div className="container-x py-20 md:py-24">
          <motion.div {...reveal} className="grid gap-10 lg:grid-cols-[0.8fr_1.2fr] lg:items-start">
            <div>
              <p className="font-mono text-xs uppercase tracking-[0.28em] text-muted">Technical view</p>
              <h2 className="mt-4 text-4xl font-medium tracking-tight md:text-5xl">
                A self-hosted marketing agent with explicit human gates.
              </h2>
            </div>
            <div>
              <div className="flex flex-wrap gap-2">
                {stack.map((item, index) => (
                  <span
                    key={item}
                    className="rounded-full border border-line bg-bg px-3.5 py-2 text-sm text-ink/80 shadow-soft"
                  >
                    <span
                      className={[
                        "mr-2 inline-block h-1.5 w-1.5 rounded-full",
                        index % 4 === 0
                          ? "bg-mint"
                          : index % 4 === 1
                            ? "bg-coral"
                            : index % 4 === 2
                              ? "bg-sky"
                              : "bg-sun",
                      ].join(" ")}
                    />
                    {item}
                  </span>
                ))}
              </div>
              <p className="mt-8 max-w-[70ch] text-sm leading-relaxed text-soft md:text-[15px]">
                The system separates product experience from background execution: the Next.js
                frontends present approvals and status, FastAPI owns routes and webhooks, workers
                handle long-running content jobs, and the database stores tenant memory, accounts,
                drafts, approvals, publishing events, and analytics.
              </p>
            </div>
          </motion.div>
        </div>
      </section>

      <section className="container-x py-20 md:py-28">
        <motion.div
          {...reveal}
          className="rounded-[2rem] border border-ink/10 bg-ink p-6 text-bg shadow-pop md:p-9"
        >
          <div className="max-w-[760px]">
            <p className="font-mono text-xs uppercase tracking-[0.28em] text-bg/55">
              Product impact
            </p>
            <h2 className="mt-4 text-3xl font-medium tracking-tight md:text-5xl">
              Less coordination. More consistent output.
            </h2>
            <p className="mt-5 text-sm leading-relaxed text-bg/70 md:text-base">
              Elon is not a black-box scheduler. It is a controlled workflow for moving from
              brand context to approved content while preserving human judgment, auditability,
              and platform-specific execution.
            </p>
          </div>
          <div className="mt-9 grid gap-3 md:grid-cols-2 lg:grid-cols-4">
            {outcomes.map((item) => (
              <div
                key={item.label}
                className="rounded-2xl border border-bg/10 bg-bg/5 p-4"
              >
                <p className="text-3xl font-medium tracking-tight text-sun">{item.value}</p>
                <h3 className="mt-2 text-sm font-medium text-bg">{item.label}</h3>
                <p className="mt-3 text-xs leading-relaxed text-bg/65">{item.body}</p>
              </div>
            ))}
          </div>
        </motion.div>
      </section>
    </main>
  );
}

function ConsoleLine({
  label,
  value,
  strong = false,
}: {
  label: string;
  value: string;
  strong?: boolean;
}) {
  return (
    <div className="border-b border-line py-3 last:border-b-0">
      <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-muted">{label}</p>
      <p className={["mt-1 text-sm leading-snug", strong ? "font-medium text-ink" : "text-soft"].join(" ")}>
        {value}
      </p>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-line bg-white px-2 py-2">
      <p className="font-mono text-[10px] text-muted">{label}</p>
      <p className="mt-1 font-medium text-ink">{value}</p>
    </div>
  );
}
