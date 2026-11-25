import type { ReactNode } from "react";
import { I18nextProvider } from "react-i18next";

import { i18n } from "@/shared/i18n";

// TODO: add QueryClientProvider when the first API call lands (FRONT-END-ARCHITECTURE §3).
export function Providers({ children }: { children: ReactNode }) {
  return <I18nextProvider i18n={i18n}>{children}</I18nextProvider>;
}
