import { BookOpenCheck, ClipboardCheck, type LucideIcon } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router";

import { buttonVariants } from "@/shared/ui/button-variants";

import { guestPaths } from "./guest-paths";
import { Container } from "./SectionText";

const highlights: { key: "cited" | "doctorApproved"; icon: LucideIcon }[] = [
  { key: "cited", icon: BookOpenCheck },
  { key: "doctorApproved", icon: ClipboardCheck },
];

// Peach CTA block + teal-800 highlights. On desktop it overlaps the hero bottom by 60px (Figma).
export function AskStripSection() {
  const { t } = useTranslation();
  return (
    <section aria-labelledby="ask-strip-title" className="relative z-10 lg:-mt-15">
      <Container className="flex flex-col lg:flex-row">
        <div className="bg-peach-400 flex flex-col gap-5.5 px-6 py-8 sm:px-9 lg:w-100 lg:shrink-0">
          <h2 id="ask-strip-title" className="text-h3-lg font-bold text-teal-900">
            {t("landing.askStrip.title")}
          </h2>
          <Link to={guestPaths.ask} className={buttonVariants({ className: "self-start" })}>
            {t("landing.askStrip.cta")}
          </Link>
        </div>
        <ul className="flex flex-1 flex-col gap-8 bg-teal-800 px-6 py-8 sm:flex-row sm:px-10 lg:gap-10">
          {highlights.map(({ key, icon: Icon }) => (
            <li key={key} className="flex flex-1 items-start gap-4">
              <span className="bg-peach-400 flex size-13 shrink-0 items-center justify-center rounded-full text-teal-900">
                <Icon aria-hidden="true" className="size-6" />
              </span>
              <div className="flex flex-col gap-1">
                <h3 className="text-h3 font-bold text-white">
                  {t(`landing.askStrip.${key}.title`)}
                </h3>
                <p className="text-body text-on-dark-muted">
                  {t(`landing.askStrip.${key}.description`)}
                </p>
              </div>
            </li>
          ))}
        </ul>
      </Container>
    </section>
  );
}
