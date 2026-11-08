import type { Lang } from "@/i18n/languages";

/** withLang("ar", "news") -> "/ar/news"; withLang("it") -> "/it" */
export function withLang(lang: Lang, path = ""): string {
  const clean = path.replace(/^\/+/, "");
  return clean ? `/${lang}/${clean}` : `/${lang}`;
}

/** Same page in another language: swapLang("/it/news", "ar") -> "/ar/news" */
export function swapLang(pathname: string, lang: Lang): string {
  const rest = pathname.split("/").slice(2).join("/");
  return withLang(lang, rest);
}