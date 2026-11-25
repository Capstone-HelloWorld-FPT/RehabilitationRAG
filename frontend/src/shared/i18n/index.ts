import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import vi from "./vi.json";

// MVP is Vietnamese only, but every display string still goes through i18next (AGENTS.md rule 26).
void i18n.use(initReactI18next).init({
  resources: { vi: { translation: vi } },
  lng: "vi",
  fallbackLng: "vi",
  // React already escapes rendered text.
  interpolation: { escapeValue: false },
});

export { i18n };
