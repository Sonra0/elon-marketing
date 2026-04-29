"use client";

import { motion } from "framer-motion";
import { copy } from "@/lib/copy";

export function CTA() {
  return (
    <section className="relative overflow-hidden">
      <div aria-hidden className="absolute left-1/2 -translate-x-1/2 top-12 w-[60rem] h-[60rem] rounded-full bg-sun/30 blur-3xl pointer-events-none" />
      <div className="relative container-x py-28 md:py-36 text-center">
        <motion.h2
          initial={{ opacity: 0, y: 14 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.5 }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          className="mx-auto max-w-[20ch] text-[clamp(2.2rem,5vw,3.6rem)] font-medium tracking-tightest leading-[1.05]"
        >
          {copy.cta.title_pre}{" "}
          <span className="display italic font-normal text-coral">{copy.cta.title_em}</span>
        </motion.h2>
        <p className="mt-6 mx-auto max-w-[52ch] text-soft text-[15px] md:text-base">
          {copy.cta.sub}
        </p>
        <div className="mt-10 flex flex-wrap items-center justify-center gap-3">
          <a href="https://conhacks-2026.devpost.com/" target="_blank" rel="noreferrer"
             className="btn btn-primary">View submission ↗</a>
          <a href="#how" className="btn btn-ghost">Re-watch the loop</a>
        </div>
        <div className="mt-12 flex items-center justify-center gap-2 text-soft text-sm">
          <span>Made with</span>
          <span className="animate-pulse">❤️</span>
          <span>for ConHacks 2026</span>
        </div>
      </div>
    </section>
  );
}
