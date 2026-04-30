"use client";

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
        <div className="grid gap-3 md:grid-cols-4">
          {overview.map((item, index) => (
            <motion.article
              key={item.title}
              initial={{ opacity: 0, y: 14 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.3 }}
              transition={{
                duration: 0.5,
                ease: [0.22, 1, 0.36, 1],
                delay: index * 0.06,
              }}
              className="card card-hover min-h-48 p-5 md:p-6"
            >
              <span className="font-mono text-xs text-coral">{item.step}</span>
              <h2 className="mt-5 text-xl font-medium leading-tight tracking-tight">
                {item.title}
              </h2>
              <p className="mt-3 text-[13px] leading-relaxed text-soft">{item.body}</p>
            </motion.article>
          ))}
        </div>
      </div>
    </section>
  );
}
