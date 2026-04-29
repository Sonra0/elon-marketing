import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg:    "#FFF6E6",   // warm butter
        cream: "#FFF1D8",
        ink:   "#1A1612",   // warm near-black
        soft:  "#5C544A",
        muted: "#8A8377",
        line:  "#EBDFC6",

        mint:    "#84D9A7",
        coral:   "#FF9C8A",
        lav:     "#C8B6FF",
        sun:     "#FFD566",
        sky:     "#A6D8FF",
        rose:    "#FFC5DD",
      },
      fontFamily: {
        sans: ['"Inter"', "system-ui", "sans-serif"],
        display: ['"Instrument Serif"', "ui-serif", "Georgia", "serif"],
        mono: ['"JetBrains Mono"', "ui-monospace", "monospace"],
      },
      letterSpacing: {
        tightest: "-0.04em",
      },
      boxShadow: {
        soft: "0 1px 0 rgba(26,22,18,0.04), 0 8px 24px -12px rgba(26,22,18,0.10)",
        pop: "0 2px 0 rgba(26,22,18,0.06), 0 14px 36px -12px rgba(26,22,18,0.18)",
      },
    },
  },
  plugins: [],
};
export default config;
