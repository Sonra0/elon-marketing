"use client";

import { motion } from "framer-motion";

const examples = [
  {
    src: "/videos/example-1.mp4",
    title: "Brand-aware drafting",
    body: "Elon turns brand context into ready-to-post captions, hooks, and creative variants.",
  },
  {
    src: "/videos/example-2.mp4",
    title: "Operator approval",
    body: "Drafts surface in Telegram. Approve, edit, or reject before anything goes live.",
  },
  {
    src: "/videos/example-3.mp4",
    title: "Multi-channel publishing",
    body: "Approved posts ship through official APIs and report results back automatically.",
  },
];

export function Examples() {
  return (
    <section id="examples" className="relative">
      <div className="container-x py-10 md:py-14">
        <div className="mb-8 flex items-end justify-between gap-6 md:mb-10">
          <div>
            <span className="text-xs uppercase tracking-[0.22em] text-muted">Examples</span>
            <h2 className="mt-3 text-[clamp(1.8rem,3.6vw,3rem)] font-medium leading-[1] tracking-tight">
              See it in motion.
            </h2>
          </div>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          {examples.map((item, index) => (
            <motion.figure
              key={item.src}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.2 }}
              transition={{
                duration: 0.55,
                ease: [0.22, 1, 0.36, 1],
                delay: index * 0.07,
              }}
              className="card overflow-hidden p-0"
            >
              <div className="aspect-[9/16] w-full overflow-hidden bg-cream">
                <video
                  src={item.src}
                  className="h-full w-full object-cover"
                  controls
                  preload="metadata"
                  playsInline
                />
              </div>
              <figcaption className="p-5 md:p-6">
                <h3 className="text-base font-medium tracking-tight">{item.title}</h3>
                <p className="mt-2 text-[13px] leading-relaxed text-soft">{item.body}</p>
              </figcaption>
            </motion.figure>
          ))}
        </div>
      </div>
    </section>
  );
}
