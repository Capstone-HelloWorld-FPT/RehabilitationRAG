import { useTranslation } from "react-i18next";
import { Outlet } from "react-router";

import { PublicFooter } from "./PublicFooter";
import { PublicHeader } from "./PublicHeader";

// Layout for guest pages (FRONT-END-ARCHITECTURE §3).
export function PublicLayout() {
  const { t } = useTranslation();
  return (
    <div className="flex min-h-dvh flex-col">
      <a
        href="#main-content"
        className="bg-peach-400 sr-only z-50 rounded-sm px-4 py-3 font-bold text-teal-900 focus:not-sr-only focus:fixed focus:top-2 focus:left-2"
      >
        {t("nav.skipToContent")}
      </a>
      <PublicHeader />
      <main id="main-content" className="flex-1">
        <Outlet />
      </main>
      <PublicFooter />
    </div>
  );
}
