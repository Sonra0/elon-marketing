"use client";

import { Fragment } from "react";
import { motion } from "framer-motion";

const overview = [
  {
    step: "01",
    title: "Reads company data",
    body: "Elon learns from project details, company context, brand voice, audience notes, and previous content.",
  },
  {
    step: "02",
    title: "Creates content",
    body: "It turns that context into data-informed posts, captions, hooks, scripts, and channel-specific variants.",
  },
  {
    step: "03",
    title: "Gets verified",
    body: "Drafts stay under human control. The team reviews, approves, edits, or rejects before anything goes live.",
  },
  {
    step: "04",
    title: "Posts to social media",
    body: "Approved content is scheduled and published through official social APIs, then measured after posting.",
  },
];

export function ElonOverview() {
  return (
    <section id="overview" className="relative">
      <div className="container-x py-10 md:py-14">
        <div className="flex flex-col items-stretch gap-3 md:flex-row md:items-stretch">
          {overview.map((item, index) => (
            <Fragment key={item.title}>
              <motion.article
                initial={{ opacity: 0, y: 14 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, amount: 0.3 }}
                transition={{
                  duration: 0.5,
                  ease: [0.22, 1, 0.36, 1],
                  delay: index * 0.06,
                }}
                className="card card-hover min-h-48 basis-0 flex-1 p-5 md:p-6"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs text-coral">{item.step}</span>
                  {item.step === "04" && (
                    <div className="flex items-center gap-2 text-soft">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" aria-label="Instagram">
                        <rect x="3" y="3" width="18" height="18" rx="5" />
                        <circle cx="12" cy="12" r="4" />
                        <circle cx="17.5" cy="6.5" r="0.6" fill="currentColor" stroke="none" />
                      </svg>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-label="Facebook">
                        <path d="M13.5 22v-8h2.7l.4-3.2h-3.1V8.7c0-.9.3-1.6 1.6-1.6h1.6V4.2c-.3 0-1.3-.1-2.4-.1-2.4 0-4 1.5-4 4.1v2.6H7.6V14h2.7v8h3.2z" />
                      </svg>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-label="TikTok">
                        <path d="M16.5 3c.3 1.6 1.2 2.9 2.6 3.6.7.4 1.5.6 2.4.6v3c-1.6 0-3.1-.4-4.4-1.2v6.7c0 3.5-2.8 6.3-6.3 6.3S4.5 19.2 4.5 15.7s2.8-6.3 6.3-6.3c.4 0 .8 0 1.1.1v3.1c-.4-.1-.7-.2-1.1-.2-1.8 0-3.3 1.5-3.3 3.3s1.5 3.3 3.3 3.3 3.3-1.5 3.3-3.3V3h2.4z" />
                      </svg>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-label="LinkedIn">
                        <path d="M4.98 3.5C4.98 4.88 3.87 6 2.5 6S0 4.88 0 3.5 1.12 1 2.5 1s2.48 1.12 2.48 2.5zM.22 8h4.56v14H.22V8zm7.4 0h4.37v1.92h.06c.61-1.15 2.1-2.36 4.32-2.36 4.62 0 5.47 3.04 5.47 6.99V22h-4.56v-6.21c0-1.48-.03-3.39-2.06-3.39-2.07 0-2.39 1.62-2.39 3.29V22H7.62V8z" />
                      </svg>
                    </div>
                  )}
                </div>
                <h2 className="mt-5 text-xl font-medium leading-tight tracking-tight">
                  {item.title}
                </h2>
                <p className="mt-3 text-[13px] leading-relaxed text-soft">{item.body}</p>
              </motion.article>
              {index < overview.length - 1 && (
                <motion.div
                  aria-hidden
                  initial={{ opacity: 0, scale: 0.8 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true, amount: 0.3 }}
                  transition={{
                    duration: 0.4,
                    ease: [0.22, 1, 0.36, 1],
                    delay: index * 0.06 + 0.2,
                  }}
                  className="flex shrink-0 items-center justify-center py-1 text-coral md:py-0"
                >
                  <svg
                    width="22"
                    height="22"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.75"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="rotate-90 md:rotate-0"
                  >
                    <line x1="4" y1="12" x2="19" y2="12" />
                    <polyline points="13 6 19 12 13 18" />
                  </svg>
                </motion.div>
              )}
            </Fragment>
          ))}
        </div>
      </div>
    </section>
  );
}
