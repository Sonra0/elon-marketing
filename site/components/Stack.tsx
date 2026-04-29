"use client";

import { copy } from "@/lib/copy";
import { SectionHead } from "./Steps";

const colorRotation = ["bg-mint", "bg-lav", "bg-coral", "bg-sun", "bg-sky", "bg-rose"];

export function Stack() {
  return (
    <section id="stack" className="relative">
      <div className="container-x py-24 md:py-32">
        <SectionHead label="Built with" title="Self-hosted. Official APIs only." />
        <div className="mt-12 flex flex-wrap gap-2">
          {copy.stack.map((s, i) => (
            <span
              key={s}
              className="px-3.5 py-1.5 rounded-full bg-white border border-line text-sm text-ink/80 shadow-soft transition-transform hover:-translate-y-0.5"
            >
              <span className={"inline-block w-1.5 h-1.5 rounded-full mr-2 " + colorRotation[i % colorRotation.length]} />
              {s}
            </span>
          ))}
        </div>
        <p className="mt-10 max-w-[60ch] text-soft text-[15px] leading-relaxed">
          Tokens encrypted at rest. Prompt caching keeps costs friendly. Every TikTok publish gets your
          explicit thumbs-up — that's a project rule, not a setting.
        </p>
      </div>
    </section>
  );
}
