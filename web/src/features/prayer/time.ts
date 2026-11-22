import type { TFunction } from "i18next";
import type { Lang } from "@/i18n/languages";
import { PRAYERS, type HijriDate, type PrayerDay, type PrayerEntry } from "./types";

// Arabic with Western digits (05:54), as printed on the mosque timetable
const INTL_LOCALE: Record<Lang, string> = { it: "it-IT", en: "en-GB", ar: "ar-u-nu-latn" };

export function intlLocale(lang: Lang): string {
  return INTL_LOCALE[lang];
}

/** "2026-11-22" for this moment in the given time zone. */
export function isoDateIn(timeZone: string, moment: Date = new Date()): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(moment);
}

export function addDays(isoDay: string, days: number): string {
  const date = new Date(`${isoDay}T12:00:00Z`);
  date.setUTCDate(date.getUTCDate() + days);
  return date.toISOString().slice(0, 10);
}

export function monthRange(year: number, month: number): { from: string; to: string } {
  const lastDay = new Date(Date.UTC(year, month, 0)).getUTCDate();
  const mm = String(month).padStart(2, "0");
  return { from: `${year}-${mm}-01`, to: `${year}-${mm}-${String(lastDay).padStart(2, "0")}` };
}

/** "05:54" on the city's clock. */
export function formatTime(iso: string, timeZone: string, lang: Lang): string {
  return new Intl.DateTimeFormat(intlLocale(lang), {
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23",
    timeZone,
  }).format(new Date(iso));
}

/** "domenica 22 novembre 2026" */
export function formatLongDate(isoDay: string, lang: Lang): string {
  return new Intl.DateTimeFormat(intlLocale(lang), {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
    timeZone: "UTC",
  }).format(new Date(`${isoDay}T12:00:00Z`));
}

/** "dom 22" */
export function formatShortDate(isoDay: string, lang: Lang): string {
  return new Intl.DateTimeFormat(intlLocale(lang), {
    weekday: "short",
    day: "numeric",
    timeZone: "UTC",
  }).format(new Date(`${isoDay}T12:00:00Z`));
}

/** "novembre 2026" */
export function formatMonth(isoDay: string, lang: Lang): string {
  return new Intl.DateTimeFormat(intlLocale(lang), {
    month: "long",
    year: "numeric",
    timeZone: "UTC",
  }).format(new Date(`${isoDay}T12:00:00Z`));
}

/** "12 Jumada al-Akhira 1448 AH" */
export function formatHijri(hijri: HijriDate, t: TFunction): string {
  return `${hijri.day} ${t(`hijri.m${hijri.month}`)} ${hijri.year} ${t("hijri.suffix")}`;
}

/** "01:23:45" */
export function formatCountdown(ms: number): string {
  const total = Math.max(0, Math.floor(ms / 1000));
  const parts = [Math.floor(total / 3600), Math.floor((total % 3600) / 60), total % 60];
  return parts.map((n) => String(n).padStart(2, "0")).join(":");
}

export interface NextPrayer {
  entry: PrayerEntry;
  day: PrayerDay;
}

/** First prayer still to come. Sunrise ends Fajr but isn't a prayer, so it's skipped. */
export function findNext(days: PrayerDay[], now: Date): NextPrayer | null {
  for (const day of days) {
    const entries = PRAYERS.map((name) => day.prayers.find((p) => p.prayer === name));

    // Everything up to the last time that has already passed is behind us
    let start = 0;
    entries.forEach((entry, index) => {
      if (entry && new Date(entry.adhan).getTime() <= now.getTime()) start = index + 1;
    });

    for (const entry of entries.slice(start)) {
      if (!entry) return null; // unknown time: we can't say what comes next
      if (entry.prayer !== "sunrise") return { entry, day };
    }
  }
  return null;
}