import { HeartPulse, Play } from "lucide-react";
import { Trans, useTranslation } from "react-i18next";

import { buttonVariants } from "@/shared/ui/button-variants";

import doctorLeftUrl from "@/shared/assets/doctor-left.svg";
import doctorRightUrl from "@/shared/assets/doctor-right.svg";
import patternUrl from "../assets/hero-pattern.svg";
import { Container, Eyebrow } from "./SectionText";

export function HeroSection() {
  const { t } = useTranslation();
  return (
    <section
      aria-labelledby="hero-title"
      className="relative overflow-hidden bg-teal-900 pt-12 pb-16 lg:pt-17.5 lg:pb-30"
    >
      <img
        src={patternUrl}
        alt=""
        className="pointer-events-none absolute top-10.5 left-15.5 hidden h-11.5 w-21.5 xl:block"
      />
      <Container className="flex items-center justify-between gap-10">
        <div className="flex max-w-140 flex-col gap-4">
          <Eyebrow tone="dark">{t("landing.hero.eyebrow")}</Eyebrow>
          <h1
            id="hero-title"
            className="lg:text-display text-[36px] leading-[1.15] font-bold text-white sm:text-[46px]"
          >
            <Trans
              i18nKey="landing.hero.title"
              components={{ accent: <span className="text-peach-400" /> }}
            />
          </h1>
          <p className="text-body text-on-dark-muted pt-1">{t("landing.hero.description")}</p>
          <div className="flex flex-wrap items-center gap-5.5 pt-4">
            <a href="#about" className={buttonVariants({ variant: "accent" })}>
              {t("landing.hero.learnMore")}
            </a>
            <a
              href="#how-it-works"
              className="group focus-visible:ring-peach-400 inline-flex min-h-11 items-center gap-3 rounded-sm text-base font-bold text-white focus-visible:ring-2 focus-visible:outline-none"
            >
              <span className="border-peach-400 text-peach-400 group-hover:bg-peach-400 flex size-11.5 items-center justify-center rounded-full border-2 transition-colors group-hover:text-teal-900">
                <Play aria-hidden="true" className="size-4 fill-current" />
              </span>
              {t("landing.hero.seeHowItWorks")}
            </a>
          </div>
        </div>

        {/* Illustration: two arch frames (DESIGN.md §5 "Arch") + a round badge. Decorative. */}
        <div className="relative hidden shrink-0 items-end gap-5 lg:flex">
          <div className="flex h-82.5 w-57.5 items-end justify-center overflow-hidden rounded-t-full bg-teal-700">
            <img src={doctorLeftUrl} alt="" className="h-69 w-57.5" />
          </div>
          <div className="bg-peach-400 flex h-105 w-62.5 items-end justify-center overflow-hidden rounded-t-full">
            <img src={doctorRightUrl} alt="" className="h-75 w-62.5" />
          </div>
          <div className="absolute top-7.5 -right-5 flex size-17.5 items-center justify-center rounded-full bg-white text-teal-900">
            <HeartPulse aria-hidden="true" className="size-8.5" />
          </div>
        </div>
      </Container>
    </section>
  );
}
