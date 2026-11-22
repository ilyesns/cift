export type PrayerName = "fajr" | "sunrise" | "dhuhr" | "asr" | "maghrib" | "isha";
export type TimeSource = "official" | "calculated";

export const PRAYERS: PrayerName[] = ["fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha"];

// Florence only for now; a city picker can replace this later
export const DEFAULT_CITY = { slug: "firenze", timezone: "Europe/Rome" } as const;

export interface PrayerEntry {
  prayer: PrayerName;
  adhan: string; // ISO timestamp with offset
  iqama: string | null;
  source: TimeSource;
}

export interface HijriDate {
  day: number;
  month: number; // 1 = Muharram … 12 = Dhu al-Hijjah
  year: number;
}

export interface PrayerDay {
  day: string; // "2026-11-22"
  weekday: number; // 1 = Monday … 7 = Sunday
  hijri: HijriDate | null;
  complete: boolean;
  prayers: PrayerEntry[];
  jumuah: string[];
}

export interface PrayerCity {
  slug: string;
  name: string;
  timezone: string;
}

export interface Timetable {
  city: PrayerCity;
  days: PrayerDay[];
}