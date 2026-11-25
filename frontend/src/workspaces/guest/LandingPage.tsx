import { useTranslation } from "react-i18next";

import { AskBannerSection } from "./landing/AskBannerSection";
import { AskStripSection } from "./landing/AskStripSection";
import { FaqSection } from "./landing/FaqSection";
import { FeaturesSection } from "./landing/FeaturesSection";
import { HeroSection } from "./landing/HeroSection";
import { HowItWorksSection } from "./landing/HowItWorksSection";
import { LoginCtaSection } from "./landing/LoginCtaSection";
import { WhySection } from "./landing/WhySection";

// Guest landing page (Figma "Landing Page", DESIGN.md §0). Content follows DESIGN.md §12.3:
// testimonials, articles, newsletter, contact form and "24/7" claims are left out.
export function LandingPage() {
  const { t } = useTranslation();
  return (
    <>
      <title>{t("landing.pageTitle")}</title>
      <HeroSection />
      <AskStripSection />
      <WhySection />
      <FeaturesSection />
      <AskBannerSection />
      <HowItWorksSection />
      <FaqSection />
      <LoginCtaSection />
    </>
  );
}
