import { Hero } from "@/components/Hero";
import { ElonOverview } from "@/components/ElonOverview";
import { TrendIntelligence } from "@/components/TrendIntelligence";
import { DataContentEngine } from "@/components/DataContentEngine";
import { MemoryFeedbackLoop } from "@/components/MemoryFeedbackLoop";
import { AnalyticsInsight } from "@/components/AnalyticsInsight";
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
      <ElonOverview />
      <TrendIntelligence />
      <DataContentEngine />
      <MemoryFeedbackLoop />
      <AnalyticsInsight />
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
