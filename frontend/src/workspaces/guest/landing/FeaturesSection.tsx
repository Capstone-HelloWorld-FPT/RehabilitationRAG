import {
  Activity,
  BookOpenCheck,
  MessageCircle,
  Route,
  ShieldAlert,
  Stethoscope,
  type LucideIcon,
} from "lucide-react";
import { useTranslation } from "react-i18next";

import { buttonVariants } from "@/shared/ui/button-variants";

import { Container, Eyebrow, SectionTitle } from "./SectionText";

const features: { key: string; icon: LucideIcon }[] = [
  { key: "qa", icon: MessageCircle },
  { key: "citations", icon: BookOpenCheck },
  { key: "pathway", icon: Route },
  { key: "progress", icon: Activity },
  { key: "therapist", icon: Stethoscope },
  { key: "safety", icon: ShieldAlert },
];

// Feature cards (DESIGN.md §9.3). Figma's "Xem thêm →" footer strip has no page to open yet,
// so the strip shows who the feature is for instead of a dead link.
export function FeaturesSection() {
  const { t } = useTranslation();
  return (
    <section id="features" aria-labelledby="features-title" className="bg-cream-50 py-16 lg:py-25">
      <Container className="flex flex-col gap-10 lg:flex-row lg:gap-15">
        <div className="flex flex-col items-start gap-4 lg:w-82.5 lg:shrink-0">
          <Eyebrow>{t("landing.features.eyebrow")}</Eyebrow>
          <SectionTitle id="features-title">{t("landing.features.title")}</SectionTitle>
          <p className="text-body text-muted-foreground pb-3">
            {t("landing.features.description")}
          </p>
          <a href="#how-it-works" className={buttonVariants()}>
            {t("landing.features.cta")}
          </a>
        </div>

        <ul className="grid flex-1 gap-5 sm:grid-cols-2 xl:grid-cols-3">
          {features.map(({ key, icon: Icon }) => (
            <li key={key} className="border-border bg-card flex flex-col border">
              <div className="flex flex-1 flex-col gap-2 p-6.5">
                <span className="bg-cream-50 flex size-13 items-center justify-center rounded-full text-teal-900">
                  <Icon aria-hidden="true" className="size-6" />
                </span>
                <h3 className="text-h3 pt-2.5 font-bold text-teal-900">
                  {t(`landing.features.items.${key}.title`)}
                </h3>
                <p className="text-body-sm text-muted-foreground">
                  {t(`landing.features.items.${key}.description`)}
                </p>
              </div>
              <p className="bg-peach-400 flex min-h-16 items-center px-6.5 py-3 text-sm font-bold text-teal-900">
                {t("landing.features.forLabel", {
                  audience: t(`landing.features.items.${key}.audience`),
                })}
              </p>
            </li>
          ))}
        </ul>
      </Container>
    </section>
  );
}
