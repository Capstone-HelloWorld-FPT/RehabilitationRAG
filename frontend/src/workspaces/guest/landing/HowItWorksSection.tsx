import { BadgeCheck, FileSearch, MessageSquareText, Sparkles, type LucideIcon } from "lucide-react";
import { useTranslation } from "react-i18next";

import { Container, Eyebrow, SectionTitle } from "./SectionText";

const steps: { key: string; icon: LucideIcon }[] = [
  { key: "ask", icon: MessageSquareText },
  { key: "retrieve", icon: FileSearch },
  { key: "answer", icon: Sparkles },
  { key: "verify", icon: BadgeCheck },
];

export function HowItWorksSection() {
  const { t } = useTranslation();
  return (
    <section id="how-it-works" aria-labelledby="how-title" className="bg-cream-50 py-16 lg:py-22.5">
      <Container className="flex flex-col gap-12 lg:gap-14">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div className="flex flex-col gap-3.5">
            <Eyebrow>{t("landing.howItWorks.eyebrow")}</Eyebrow>
            <SectionTitle id="how-title" className="max-w-130">
              {t("landing.howItWorks.title")}
            </SectionTitle>
          </div>
          <p className="text-body text-muted-foreground lg:max-w-115">
            {t("landing.howItWorks.description")}
          </p>
        </div>

        <ol className="grid grid-cols-2 gap-x-6 gap-y-10 md:grid-cols-4">
          {steps.map(({ key, icon: Icon }) => (
            <li key={key} className="flex flex-col items-center gap-4.5 text-center">
              <span className="flex size-24 items-center justify-center rounded-full bg-white text-teal-900">
                <Icon aria-hidden="true" className="size-11" strokeWidth={1.5} />
              </span>
              <h3 className="text-h3 font-bold text-teal-900">
                {t(`landing.howItWorks.steps.${key}`)}
              </h3>
            </li>
          ))}
        </ol>
      </Container>
    </section>
  );
}
