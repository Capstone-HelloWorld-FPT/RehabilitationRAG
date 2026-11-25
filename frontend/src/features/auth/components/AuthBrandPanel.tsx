import { Check, Heart } from "lucide-react";
import { Trans, useTranslation } from "react-i18next";
import { Link } from "react-router";

import logoUrl from "@/shared/assets/logo.svg";
import doctorLeftUrl from "@/shared/assets/doctor-left.svg";
import doctorRightUrl from "@/shared/assets/doctor-right.svg";

const benefits = ["citations", "history", "audience"] as const;

// Left side of the login screen (Figma "Brand Panel", 640px). The illustration is decorative.
export function AuthBrandPanel() {
  const { t } = useTranslation();
  return (
    <div className="flex h-full flex-col justify-between gap-10 overflow-hidden bg-teal-900 px-16 pt-12">
      <Link
        to="/"
        aria-label={t("app.homeLink")}
        className="focus-visible:ring-peach-400 flex items-center gap-2.5 self-start rounded-sm focus-visible:ring-2 focus-visible:outline-none"
      >
        <img src={logoUrl} alt="" className="size-10" />
        <span className="text-logo font-bold text-white">
          {t("app.nameLead")}
          <span className="text-peach-400">{t("app.nameAccent")}</span>
        </span>
      </Link>

      <div className="flex flex-col gap-4">
        <p className="text-eyebrow text-peach-400 font-bold uppercase">{t("auth.brand.eyebrow")}</p>
        <p className="text-[46px] leading-[54px] font-bold text-white">
          <Trans
            i18nKey="auth.brand.title"
            components={{ accent: <span className="text-peach-400" /> }}
          />
        </p>
        <p className="text-body text-on-dark-muted">{t("auth.brand.description")}</p>
        <ul className="flex flex-col gap-3 pt-2">
          {benefits.map((benefit) => (
            <li key={benefit} className="text-body flex items-center gap-3 text-white">
              <span className="bg-peach-400 flex size-5.5 shrink-0 items-center justify-center rounded-full">
                <Check aria-hidden="true" className="size-3 text-teal-900" strokeWidth={3} />
              </span>
              {t(`auth.brand.benefits.${benefit}`)}
            </li>
          ))}
        </ul>
      </div>

      <div aria-hidden="true" className="relative flex items-end gap-5 self-start">
        <div className="flex h-82.5 w-57.5 items-end justify-center overflow-hidden rounded-t-full bg-teal-700">
          <img src={doctorLeftUrl} alt="" className="h-69 w-57.5" />
        </div>
        <div className="bg-peach-400 flex h-105 w-62.5 items-end justify-center overflow-hidden rounded-t-full">
          <img src={doctorRightUrl} alt="" className="h-75 w-62.5" />
        </div>
        <div className="text-peach-400 absolute top-7.5 -right-5 flex size-17.5 items-center justify-center rounded-full bg-white">
          <Heart className="size-8.5 fill-current" />
        </div>
      </div>
    </div>
  );
}
