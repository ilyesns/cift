import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { ROUTES } from "@/app/routes";
import { useLang } from "@/shared/hooks/useLang";
import { withLang } from "@/shared/lib/paths";
import styles from "./HomePage.module.css";

const SECTIONS = [
  { key: "prayer", route: ROUTES.prayer },
  { key: "news", route: ROUTES.news },
  { key: "tourism", route: ROUTES.tourism },
  { key: "marketplace", route: ROUTES.marketplace },
] as const;

export function HomePage() {
  const { t } = useTranslation();
  const lang = useLang();

  return (
    <>
      <section className={styles.hero}>
        <p className={styles.eyebrow}>{t("home.eyebrow")}</p>
        <h1 className={styles.title}>{t("home.title")}</h1>
        <p className={styles.subtitle}>{t("home.subtitle")}</p>
      </section>

      <section className={styles.grid}>
        {SECTIONS.map((section) => (
          <Link key={section.key} to={withLang(lang, section.route)} className={styles.card}>
            <h2>{t(`home.sections.${section.key}.title`)}</h2>
            <p>{t(`home.sections.${section.key}.text`)}</p>
            <span className={styles.more}>
              {t("home.open")} <span className={styles.arrow} aria-hidden="true">→</span>
            </span>
          </Link>
        ))}
      </section>
    </>
  );
}