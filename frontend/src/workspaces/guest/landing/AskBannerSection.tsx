import { MessageCircleQuestion } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router";

import { buttonVariants } from "@/shared/ui/button-variants";

import { guestPaths } from "./guest-paths";
import { Container } from "./SectionText";

// Dark CTA strip (Figma: 44px vertical padding, 64px peach icon circle).
export function AskBannerSection() {
  const { t } = useTranslation();
  return (
    <section aria-labelledby="ask-banner-title" className="bg-teal-900 py-11">
      <Container className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex items-center gap-5">
          <span className="bg-peach-400 flex size-16 shrink-0 items-center justify-center rounded-full text-teal-900">
            <MessageCircleQuestion aria-hidden="true" className="size-7.5" />
          </span>
          <h2
            id="ask-banner-title"
            className="text-h3-lg sm:text-h2-sm font-bold whitespace-pre-line text-white"
          >
            {t("landing.askBanner.title")}
          </h2>
        </div>
        <p className="text-body text-on-dark-muted lg:max-w-105">
          {t("landing.askBanner.description")}
        </p>
        <Link
          to={guestPaths.ask}
          className={buttonVariants({ variant: "accent", className: "self-start lg:self-auto" })}
        >
          {t("landing.askBanner.cta")}
        </Link>
      </Container>
    </section>
  );
}
