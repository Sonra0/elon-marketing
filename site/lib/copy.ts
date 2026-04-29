export const copy = {
  hero: {
    eyebrow: "Hi, I'm Elon 👋",
    title_pre: "Your friendly",
    title_em:  "marketing teammate",
    title_post: "that posts every day.",
    subtitle:
      "I learn your brand, write tomorrow's posts tonight, and ship to Instagram, TikTok, and Facebook through official APIs. You sip your coffee and tap ✓.",
  },
  steps: [
    { n: "01", emoji: "📚", color: "mint",  title: "I learn your brand.",
      body: "Drop a URL or a folder. I find your voice, palette, audience, and the things you'd never say." },
    { n: "02", emoji: "🧠", color: "lav",   title: "I draft on brand.",
      body: "Your instructions beat brand memory beats analytics beats trends. Every draft cites a pillar and an expected lift." },
    { n: "03", emoji: "🚀", color: "coral", title: "I ship through the front door.",
      body: "Tap ✓ in Telegram. I post via the official APIs and check on the numbers a few hours later." },
  ],
  features: [
    { emoji: "🧷", color: "sun",   title: "Brand memory",      body: "Versioned & immutable. Voice, pillars, audience, and the words we'll never use." },
    { emoji: "📡", color: "sky",   title: "Multi-platform",    body: "Instagram Reels, TikTok direct post, Facebook Pages — all official, all idempotent." },
    { emoji: "💬", color: "rose",  title: "Telegram chat",     body: "Approve, reject, reschedule, all from your thumb. Live alerts. Nightly digest." },
    { emoji: "📈", color: "mint",  title: "Always learning",   body: "Pillars that beat baseline get a little nudge up. Anomalies ping you in real time." },
    { emoji: "🧪", color: "lav",   title: "Weekly experiments", body: "I propose hypotheses every Monday and quietly retire the ones that aren't working." },
    { emoji: "🛡️", color: "coral", title: "Crisis playbooks",  body: "Sensitive copy gets a hard stop. Deny-list, double sign-off, kind templated replies." },
  ],
  stats: [
    { emoji: "📅", v: "7",   label: "posts / week",         note: "kind, not chaotic" },
    { emoji: "⏱️", v: "11",  label: "minutes brief → live", note: "approve, ship, measure" },
    { emoji: "💸", v: "$50", label: "monthly cap / tenant", note: "prompt caching for the win" },
    { emoji: "🌐", v: "3",   label: "platforms",            note: "ig · tiktok · facebook" },
  ],
  demo: [
    { who: "elon", t: "06:00", text: "Morning! Three drafts ready ☕ Pillar mix: craft × story × proof." },
    { who: "you",  t: "06:01", text: "approve all" },
    { who: "elon", t: "06:01", text: "On it. IG 09:00 · TT 13:00 · FB 17:00 ✓" },
    { who: "elon", t: "10:14", text: "That Reel is doing numbers — +312% reach vs your usual 🚀" },
    { who: "elon", t: "21:55", text: "Day's wrap-up: 3 posted · 1 anomaly · 1 hypothesis cooking for Monday 🌙" },
  ],
  stack: [
    "Anthropic Claude", "Instagram Graph", "TikTok Content Posting", "Meta Pages",
    "WhatsApp Cloud", "Telegram Bot", "Postgres + pgvector", "Celery · Redis",
    "FastAPI", "Next.js", "Playwright", "MinIO",
  ],
  cta: {
    title_pre: "Less posting.",
    title_em:  "More smiling.",
    sub: "Built in twelve happy days for ConHacks 2026.",
  },
};
