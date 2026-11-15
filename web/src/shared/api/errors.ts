import i18n from "@/i18n";
import { ApiError } from "./client";

/** Translated text for an error: by backend code if we have one, else the backend message. */
export function errorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    const key = `errors.codes.${error.code}`;
    return i18n.exists(key) ? i18n.t(key) : error.message;
  }
  return i18n.t("errors.generic");
}