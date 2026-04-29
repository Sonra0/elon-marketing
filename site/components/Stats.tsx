"use client";

import { motion } from "framer-motion";
import { copy } from "@/lib/copy";

export function Stats() {
  return (
    <section className="relative">
      <div className="container-x py-16 md:py-20">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {copy.stats.map((s, i) => (
            <motion.div
              key={s.label}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.3 }}
              transition={{ type: "spring", stiffness: 180, damping: 22, delay: i * 0.06 }}
              className="card card-hover p-5 md:p-6"
            >
              <div className="flex items-baseline justify-between">
                <span className="num-tabular text-3xl md:text-4xl font-medium tracking-tight">{s.v}</span>
                <span className="text-xl">{s.emoji}</span>
              </div>
              <div className="mt-1.5 text-[13px] text-ink/85">{s.label}</div>
              <div className="mt-0.5 text-[11px] text-muted">{s.note}</div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
