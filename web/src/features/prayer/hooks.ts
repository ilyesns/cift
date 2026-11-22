import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { useNow } from "@/shared/hooks/useNow";
import { prayerApi } from "./api";
import { addDays, isoDateIn } from "./time";
import { DEFAULT_CITY } from "./types";

export const prayerKeys = {
  all: ["prayer"] as const,
  // Language is part of the key because the city name comes back translated
  range: (city: string, from: string, to: string, lang: string) =>
    [...prayerKeys.all, city, from, to, lang] as const,
};

export function usePrayerRange(city: string, from: string, to: string) {
  const { i18n } = useTranslation();
  return useQuery({
    queryKey: prayerKeys.range(city, from, to, i18n.language),
    queryFn: () => prayerApi.timetable(city, from, to),
    staleTime: 5 * 60_000,
    placeholderData: keepPreviousData, // keep the old month visible while the next one loads
  });
}

/** Today and tomorrow on the city's clock. Moves to the next day by itself at midnight. */
export function usePrayerWindow(city: { slug: string; timezone: string } = DEFAULT_CITY) {
  const now = useNow();
  const today = isoDateIn(city.timezone, now);
  const query = usePrayerRange(city.slug, today, addDays(today, 1));
  return { query, now, today };
}