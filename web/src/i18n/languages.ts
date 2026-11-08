export const LANGUAGES = ["it", "ar", "en"] as const;
export type Lang = (typeof LANGUAGES)[number];

export const DEFAULT_LANG: Lang = "it";

export const LANGUAGE_LABELS: Record<Lang, string> = {
  it: "Italiano",
  ar: "العربية",
  en: "English",
};

export function isLang(value: string | null | undefined): value is Lang {
  return !!value && (LANGUAGES as readonly string[]).includes(value);
}

export function dirFor(lang: Lang): "rtl" | "ltr" {
  return lang === "ar" ? "rtl" : "ltr";
}

/** First supported language from a browser preference list, e.g. ["ar-TN", "fr"]. */
export function pickPreferredLang(preferred: readonly string[]): Lang {
  for (const tag of preferred) {
    const base = tag.toLowerCase().split("-")[0];
    if (isLang(base)) return base;
  }
  return DEFAULT_LANG;
}