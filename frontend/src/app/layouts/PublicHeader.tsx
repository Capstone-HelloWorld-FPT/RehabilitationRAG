import { Menu, X } from "lucide-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Link, useLocation } from "react-router";

import { cn } from "@/shared/lib/utils";
import { buttonVariants } from "@/shared/ui/button-variants";

import { Logo } from "./Logo";
import { landingNavLinks } from "./nav-links";

// Guest header (DESIGN.md §9.7): teal-900, logo left, menu center, one accent button right.
// Below 1024px the menu collapses behind a toggle button.
export function PublicHeader() {
  const { t } = useTranslation();
  const { pathname, hash } = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);

  const isActive = (href: string) => href === "/" && pathname === "/" && hash === "";

  const navItems = landingNavLinks.map((link) => (
    <li key={link.href}>
      <a
        href={link.href}
        aria-current={isActive(link.href) ? "page" : undefined}
        onClick={() => setMenuOpen(false)}
        className={cn(
          "text-body hover:text-peach-400 focus-visible:ring-peach-400 inline-flex min-h-11 items-center rounded-sm transition-colors focus-visible:ring-2 focus-visible:outline-none",
          isActive(link.href) ? "text-peach-400" : "text-teal-100",
        )}
      >
        {t(link.labelKey)}
      </a>
    </li>
  ));

  return (
    <header className="border-sidebar-border border-b bg-teal-900">
      <div className="max-w-content mx-auto flex w-full items-center justify-between gap-4 px-4 py-5 xl:px-0">
        <Link
          to="/"
          aria-label={t("app.homeLink")}
          className="focus-visible:ring-peach-400 rounded-sm focus-visible:ring-2 focus-visible:outline-none"
        >
          <Logo />
        </Link>

        <nav aria-label={t("nav.mainMenu")} className="hidden lg:block">
          <ul className="flex items-center gap-9">{navItems}</ul>
        </nav>

        <div className="flex items-center gap-2">
          <Link
            to="/login"
            className={cn(buttonVariants({ variant: "accent" }), "hidden sm:inline-flex")}
          >
            {t("nav.login")}
          </Link>
          <button
            type="button"
            aria-expanded={menuOpen}
            aria-controls="mobile-menu"
            aria-label={menuOpen ? t("nav.closeMenu") : t("nav.openMenu")}
            onClick={() => setMenuOpen((open) => !open)}
            className={cn(
              buttonVariants({ variant: "ghost", size: "icon" }),
              "text-white lg:hidden",
            )}
          >
            {menuOpen ? <X className="size-6" /> : <Menu className="size-6" />}
          </button>
        </div>
      </div>

      {menuOpen && (
        <nav id="mobile-menu" aria-label={t("nav.mainMenu")} className="px-4 pb-4 lg:hidden">
          <ul className="flex flex-col gap-1">{navItems}</ul>
          <Link
            to="/login"
            onClick={() => setMenuOpen(false)}
            className={cn(buttonVariants({ variant: "accent" }), "mt-3 w-full sm:hidden")}
          >
            {t("nav.login")}
          </Link>
        </nav>
      )}
    </header>
  );
}
