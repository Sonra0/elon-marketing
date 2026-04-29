import { Hero } from "@/components/Hero";
import { Steps } from "@/components/Steps";
import { Features } from "@/components/Features";
import { Demo } from "@/components/Demo";
import { Stats } from "@/components/Stats";
import { Stack } from "@/components/Stack";
import { CTA } from "@/components/CTA";
import { Footer } from "@/components/Footer";

export default function Page() {
  return (
    <>
      <Hero />
      <Stats />
      <Steps />
      <Features />
      <Demo />
      <Stack />
      <CTA />
      <Footer />
    </>
  );
}
