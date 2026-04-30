import { Hero } from "@/components/Hero";
import { ElonOverview } from "@/components/ElonOverview";
import { Examples } from "@/components/Examples";
import { TrendIntelligence } from "@/components/TrendIntelligence";
import { DataContentEngine } from "@/components/DataContentEngine";
import { MemoryFeedbackLoop } from "@/components/MemoryFeedbackLoop";
import { AnalyticsInsight } from "@/components/AnalyticsInsight";
import { ComingSoon } from "@/components/ComingSoon";
import { Stack } from "@/components/Stack";
import { CTA } from "@/components/CTA";
import { Footer } from "@/components/Footer";

export default function Page() {
  return (
    <>
      <Hero />
      <ElonOverview />
      <Examples />
      <TrendIntelligence />
      <DataContentEngine />
      <MemoryFeedbackLoop />
      <AnalyticsInsight />
      <ComingSoon />
      <Stack />
      <CTA />
      <Footer />
    </>
  );
}
