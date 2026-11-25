import { useTranslation } from "react-i18next";

import logoUrl from "@/shared/assets/logo.svg";
import { cn } from "@/shared/lib/utils";

type LogoProps = { size?: "md" | "sm" };

// Logo icon + "Rehab" (white) + "Graph-RAG" (peach), as in Figma. The name lives in vi.json.
export function Logo({ size = "md" }: LogoProps) {
  const { t } = useTranslation();
  return (
    <span className="inline-flex items-center gap-2.5">
      <img src={logoUrl} alt="" className={size === "md" ? "size-10" : "size-9"} />
      <span
        className={cn(
          "font-bold whitespace-nowrap text-white",
          size === "md" ? "text-logo" : "text-xl",
        )}
      >
        {t("app.nameLead")}
        <span className="text-peach-400">{t("app.nameAccent")}</span>
      </span>
    </span>
  );
}
