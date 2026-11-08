import { useTranslation } from "react-i18next";
import { Link, useLocation } from "react-router-dom";
import { LANGUAGES, LANGUAGE_LABELS } from "@/i18n/languages";
import { useLang } from "@/shared/hooks/useLang";
import { swapLang } from "@/shared/lib/paths";
import styles from "./LanguageSwitcher.module.css";

export function LanguageSwitcher() {
  const { t } = useTranslation();
  const current = useLang();
  const { pathname } = useLocation();

  return (
    <div className={styles.switcher} role="group" aria-label={t("nav.language")}>
      {LANGUAGES.map((lang) => (
        <Link
          key={lang}
          to={swapLang(pathname, lang)}
          lang={lang}
          hrefLang={lang}
          aria-current={lang === current ? "true" : undefined}
          className={styles.option}
        >
          {LANGUAGE_LABELS[lang]}
        </Link>
      ))}
    </div>
  );
}