import { useParams } from "react-router-dom";
import { DEFAULT_LANG, isLang, type Lang } from "@/i18n/languages";

/** The language from the current URL (/it, /ar, /en). */
export function useLang(): Lang {
  const { lang } = useParams();
  return isLang(lang) ? lang : DEFAULT_LANG;
}