"use client";

import { motion } from "framer-motion";
import { copy } from "@/lib/copy";
import { SectionHead } from "./Steps";

const tints: Record<string, string> = {
  mint: "bg-mint/30",
  lav: "bg-lav/30",
  coral: "bg-coral/30",
  sun: "bg-sun/35",
  sky: "bg-sky/35",
  rose: "bg-rose/40",
};

export function Features() {
  return (
    <section id="features" className="relative">
      <div className="container-x py-24 md:py-32">
        <SectionHead label="What I do" title="Six small superpowers." />
        <div className="mt-14 grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {copy.features.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 14 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.2 }}
              transition={{ type: "spring", stiffness: 180, damping: 22, delay: (i % 3) * 0.06 }}
              className="card card-hover p-6 md:p-7 relative overflow-hidden"
            >
              <div aria-hidden
                   className={"absolute -right-12 -top-12 w-32 h-32 rounded-full blur-2xl " + tints[f.color]} />
              <div className="relative text-2xl">{f.emoji}</div>
              <h3 className="relative mt-4 text-[17px] font-medium tracking-tight">{f.title}</h3>
              <p className="relative mt-2 text-soft text-[14px] leading-relaxed">{f.body}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
