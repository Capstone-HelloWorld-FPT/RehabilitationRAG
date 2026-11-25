import { useTranslation } from "react-i18next";
import { Link } from "react-router";

import { buttonVariants } from "@/shared/ui/button-variants";

// Placeholder for routes the landing page links to before their feature exists.
export function ComingSoonPage({
  variant = "comingSoon",
}: {
  variant?: "comingSoon" | "notFound";
}) {
  const { t } = useTranslation();
  return (
    <section className="mx-auto flex max-w-xl flex-col items-center gap-4 px-4 py-24 text-center">
      <title>{t(`${variant}.title`)}</title>
      <h1 className="text-h3-lg font-bold text-teal-900">{t(`${variant}.title`)}</h1>
      <p className="text-muted-foreground text-base">{t(`${variant}.description`)}</p>
      <Link to="/" className={buttonVariants()}>
        {t(`${variant}.backHome`)}
      </Link>
    </section>
  );
}
