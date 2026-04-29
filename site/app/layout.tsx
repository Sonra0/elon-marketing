import "./globals.css";
import type { Metadata } from "next";
import { Header } from "@/components/Header";

export const metadata: Metadata = {
  title: "Elon — your friendly AI marketing teammate",
  description:
    "Elon is the cheerful AI specialist that learns your brand and posts every day across Instagram, TikTok, and Facebook. You sip your coffee. Built for ConHacks 2026.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="grain-warm">
        <Header />
        {children}
      </body>
    </html>
  );
}
