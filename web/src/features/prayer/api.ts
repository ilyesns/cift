import { api } from "@/shared/api/client";
import type { Timetable } from "./types";

export const prayerApi = {
  timetable: (city: string, from: string, to: string = from) =>
    api.get<Timetable>(`/prayer-times/${city}`, { query: { from, to }, skipAuth: true }),
};