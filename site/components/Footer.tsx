export function Footer() {
  return (
    <footer className="border-t border-line">
      <div className="container-x py-10 flex flex-col md:flex-row gap-3 md:items-center md:justify-between text-[12px] text-soft">
        <div className="flex items-center gap-2">
          <span className="grid place-items-center w-5 h-5 rounded-full bg-sun shadow-soft text-[11px]">☀️</span>
          <span>Elon · ConHacks 2026</span>
        </div>
        <div className="flex flex-wrap gap-x-5 gap-y-1">
          <a href="#how" className="hover:text-ink transition">How</a>
          <a href="#features" className="hover:text-ink transition">Features</a>
          <a href="#demo" className="hover:text-ink transition">Demo</a>
          <a href="#stack" className="hover:text-ink transition">Stack</a>
          <a href="https://conhacks-2026.devpost.com/" target="_blank" rel="noreferrer"
             className="hover:text-ink transition">Submission ↗</a>
        </div>
        <span className="font-mono">v0.2.0</span>
      </div>
    </footer>
  );
}
