import { useTranslation } from "react-i18next";
import { Link } from "react-router";

import { buttonVariants } from "@/shared/ui/button-variants";

import illustrationUrl from "../assets/login-cta.svg";
import { guestPaths } from "./guest-paths";
import { Container, Eyebrow, SectionTitle } from "./SectionText";

// Replaces Figma's clinic contact form: the app is internal to one center, so the page
// points to login instead (DESIGN.md §12.3). Overlaps the footer top on desktop, as in Figma.
export function LoginCtaSection() {
  const { t } = useTranslation();
  return (
    <section aria-labelledby="login-cta-title" className="relative z-10 pb-16 lg:-mb-12 lg:pb-0">
      <Container className="flex flex-col md:flex-row">
        <div className="bg-peach-400 hidden items-end justify-center overflow-hidden pt-10 md:flex md:w-2/5 lg:w-115 lg:shrink-0">
          <img src={illustrationUrl} alt="" className="h-auto w-full max-w-85" />
        </div>
        <div className="flex flex-1 flex-col items-start gap-3.5 bg-teal-800 p-8 sm:p-14">
          <Eyebrow tone="dark">{t("landing.login.eyebrow")}</Eyebrow>
          <SectionTitle id="login-cta-title" tone="dark">
            {t("landing.login.title")}
          </SectionTitle>
          <p className="text-body text-on-dark-muted pb-2">{t("landing.login.description")}</p>
          <Link to={guestPaths.login} className={buttonVariants({ variant: "accent" })}>
            {t("landing.login.cta")}
          </Link>
        </div>
      </Container>
    </section>
  );
}
