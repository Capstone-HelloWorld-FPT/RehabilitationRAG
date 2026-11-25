import { useTranslation } from "react-i18next";
import { Link } from "react-router";

import logoUrl from "@/shared/assets/logo.svg";
import { cn } from "@/shared/lib/utils";
import { buttonVariants } from "@/shared/ui/button-variants";

import { AuthBrandPanel } from "../components/AuthBrandPanel";
import { LoginForm } from "../components/LoginForm";
import type { LoginValues } from "../schemas";

// TODO: call POST /api/v1/auth/login once the backend identity module and `shared/api` exist,
// then keep the access token in memory (session store) and go to /w.
// Until then login always fails with a clear message instead of pretending to work.
async function login(values: LoginValues): Promise<void> {
  void values;
  throw new Error("LOGIN_UNAVAILABLE");
}

// Full-screen login (Figma "RehabRAG - Đăng nhập"). It has its own brand panel, so it is not
// wrapped in PublicLayout. Below 1024px the brand panel is hidden and only the form card remains.
export function LoginPage() {
  const { t } = useTranslation();
  return (
    <div className="grid min-h-dvh lg:grid-cols-[640px_1fr]">
      <title>{t("auth.pageTitle")}</title>

      <div className="hidden lg:block">
        <AuthBrandPanel />
      </div>

      <main className="bg-cream-50 flex flex-col items-center justify-center gap-6 px-4 py-10">
        <Link
          to="/"
          aria-label={t("app.homeLink")}
          className="focus-visible:ring-ring flex items-center gap-2.5 rounded-sm focus-visible:ring-2 focus-visible:outline-none lg:hidden"
        >
          <img src={logoUrl} alt="" className="size-10" />
          <span className="text-logo font-bold text-teal-900">
            {t("app.nameLead")}
            <span className="text-teal-700">{t("app.nameAccent")}</span>
          </span>
        </Link>

        <div className="border-border bg-card flex w-full max-w-120 flex-col gap-6 rounded-sm border px-6 py-8 shadow-[0_12px_32px_0_rgb(15_59_56/0.06)] sm:px-12 sm:py-10">
          <div className="flex flex-col gap-2">
            <h1 className="text-[30px] leading-[38px] font-bold text-teal-900">
              {t("auth.form.title")}
            </h1>
            <p className="text-body-sm text-muted-foreground">{t("auth.form.subtitle")}</p>
          </div>

          <div className="flex flex-col gap-3">
            <LoginForm onSubmit={login} />
            <Link to="/" className={cn(buttonVariants(), "h-12 w-full")}>
              {t("auth.form.backHome")}
            </Link>
          </div>
        </div>

        <div className="text-center">
          <p className="text-caption text-muted-foreground">
            {t("footer.copyright", { year: new Date().getFullYear() })}
          </p>
        </div>
      </main>
    </div>
  );
}
