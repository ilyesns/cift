import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import { dirFor, type Lang } from "./languages";
import ar from "./locales/ar.json";
import en from "./locales/en.json";
import it from "./locales/it.json";
import { detectLang, saveLang } from "./storage";

void i18n.use(initReactI18next).init({
  resources: {
    it: { translation: it },
    ar: { translation: ar },
    en: { translation: en },
  },
  lng: detectLang(),
  // Missing Arabic or English text falls back to Italian, same rule as the backend
  fallbackLng: { ar: ["it", "en"], en: ["it"], default: ["it"] },
  interpolation: { escapeValue: false },
});

/** Switch translations, <html lang>, <html dir> and the saved preference together. */
export function applyLang(lang: Lang): void {
  if (i18n.language !== lang) void i18n.changeLanguage(lang);
  const root = document.documentElement;
  root.lang = lang;
  root.dir = dirFor(lang);
  saveLang(lang);
}

export default i18n;