import { isLang, pickPreferredLang, type Lang } from "./languages";

const STORAGE_KEY = "cift.lang";

export function loadSavedLang(): Lang | null {
  try {
    const value = localStorage.getItem(STORAGE_KEY);
    return isLang(value) ? value : null;
  } catch {
    return null; // storage blocked (private mode)
  }
}

export function saveLang(lang: Lang): void {
  try {
    localStorage.setItem(STORAGE_KEY, lang);
  } catch {
    // ignore
  }
}

/** Saved choice, then browser languages, then Italian. */
export function detectLang(): Lang {
  return loadSavedLang() ?? pickPreferredLang(navigator.languages ?? [navigator.language]);
}