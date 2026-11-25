import { useTranslation } from "react-i18next";
import { Link } from "react-router";

import { Logo } from "./Logo";
import { landingNavLinks } from "./nav-links";

const linkClass =
  "inline-flex min-h-11 items-center rounded-sm text-body text-on-dark-muted transition-colors hover:text-white focus-visible:ring-2 focus-visible:ring-peach-400 focus-visible:outline-none sm:min-h-0";

// Guest footer (DESIGN.md §9.8). The newsletter column is removed: out of scope (DESIGN.md §12.3).
export function PublicFooter() {
  const { t } = useTranslation();
  const sectionLinks = landingNavLinks.filter((link) => link.href !== "/" && link.href !== "/#faq");

  return (
    <footer className="bg-teal-900 pt-16 lg:pt-37">
      <div className="max-w-content mx-auto grid w-full gap-10 px-4 pb-12 sm:grid-cols-2 lg:grid-cols-[2fr_1fr_1fr] lg:gap-12.5 xl:px-0">
        <div className="flex flex-col gap-4 sm:col-span-2 lg:col-span-1">
          <Logo size="sm" />
          <p className="text-body text-on-dark-muted max-w-sm">{t("footer.description")}</p>
        </div>

        <nav aria-labelledby="footer-links-title" className="flex flex-col gap-3">
          <h2 id="footer-links-title" className="text-h3 font-bold text-white">
            {t("footer.linksTitle")}
          </h2>
          <ul className="flex flex-col">
            {sectionLinks.map((link) => (
              <li key={link.href}>
                <a href={link.href} className={linkClass}>
                  {t(link.labelKey)}
                </a>
              </li>
            ))}
          </ul>
        </nav>

        <nav aria-labelledby="footer-support-title" className="flex flex-col gap-3">
          <h2 id="footer-support-title" className="text-h3 font-bold text-white">
            {t("footer.supportTitle")}
          </h2>
          <ul className="flex flex-col">
            <li>
              <a href="/#faq" className={linkClass}>
                {t("footer.faq")}
              </a>
            </li>
            <li>
              <Link to="/login" className={linkClass}>
                {t("nav.login")}
              </Link>
            </li>
          </ul>
        </nav>
      </div>

      <div className="max-w-content mx-auto w-full px-4 xl:px-0">
        <p className="text-caption text-on-dark-muted border-t border-white/12 py-6 text-center">
          {t("footer.copyright", { year: new Date().getFullYear() })}
        </p>
      </div>
    </footer>
  );
}
