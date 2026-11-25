import { Check } from "lucide-react";
import { useTranslation } from "react-i18next";

import { buttonVariants } from "@/shared/ui/button-variants";

import mainUrl from "../assets/why-main.svg";
import patternUrl from "../assets/why-pattern.svg";
import roundUrl from "../assets/why-round.svg";
import { Container, Eyebrow, SectionTitle } from "./SectionText";

const points = ["moh", "citations", "audience"] as const;

export function WhySection() {
  const { t } = useTranslation();
  return (
    <section id="about" aria-labelledby="why-title" className="py-16 lg:py-27.5">
      <Container className="flex flex-col items-center gap-12 lg:flex-row lg:gap-22.5">
        {/* Decorative illustration (Figma 500×460). */}
        <div className="relative hidden h-115 w-125 shrink-0 md:block">
          <img src={patternUrl} alt="" className="absolute top-5.5 left-0.5 size-16.5" />
          <div className="absolute top-0 left-37.5 flex h-105 w-75 items-end justify-center overflow-hidden rounded-t-full bg-teal-100">
            <img src={mainUrl} alt="" className="h-90 w-75" />
          </div>
          <div className="absolute top-60.5 left-7.5 flex h-52 w-50 items-end justify-center overflow-hidden rounded-full border-8 border-white bg-teal-900">
            <img src={roundUrl} alt="" className="h-50 w-45" />
          </div>
        </div>

        <div className="flex flex-1 flex-col items-start gap-4">
          <Eyebrow>{t("landing.why.eyebrow")}</Eyebrow>
          <SectionTitle id="why-title">{t("landing.why.title")}</SectionTitle>
          <p className="text-body text-muted-foreground">{t("landing.why.description")}</p>
          <ul className="flex flex-col gap-3.5 pt-2.5 pb-4">
            {points.map((point) => (
              <li
                key={point}
                className="flex items-center gap-3 text-base font-medium text-teal-900"
              >
                <span className="bg-peach-400 flex size-5.5 shrink-0 items-center justify-center rounded-full">
                  <Check aria-hidden="true" className="size-3 text-teal-900" strokeWidth={3} />
                </span>
                {t(`landing.why.points.${point}`)}
              </li>
            ))}
          </ul>
          <a href="#features" className={buttonVariants()}>
            {t("landing.why.cta")}
          </a>
        </div>
      </Container>
    </section>
  );
}
