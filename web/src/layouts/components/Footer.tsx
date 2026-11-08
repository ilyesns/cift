import { useTranslation } from "react-i18next";
import styles from "./Footer.module.css";

export function Footer() {
  const { t } = useTranslation();
  const year = new Date().getFullYear();

  return (
    <footer className={styles.footer}>
      <div className={styles.inner}>
        <span>
          © {year} {t("brand.name")}
        </span>
        <span>{t("footer.rights")}</span>
      </div>
    </footer>
  );
}