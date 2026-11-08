import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { useLang } from "@/shared/hooks/useLang";
import { withLang } from "@/shared/lib/paths";
import styles from "./StatusPage.module.css";

export function NotFoundPage() {
  const { t } = useTranslation();
  const lang = useLang();

  return (
    <section className={styles.page}>
      <h1>{t("notFound.title")}</h1>
      <p>{t("notFound.text")}</p>
      <Link to={withLang(lang)}>{t("common.backHome")}</Link>
    </section>
  );
}