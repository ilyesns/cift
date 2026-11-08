import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link, NavLink, useLocation } from "react-router-dom";
import { ROUTES } from "@/app/routes";
import { useLang } from "@/shared/hooks/useLang";
import { withLang } from "@/shared/lib/paths";
import styles from "./Header.module.css";
import { LanguageSwitcher } from "./LanguageSwitcher";

const NAV_ITEMS = [
  { route: ROUTES.home, labelKey: "nav.home" },
  { route: ROUTES.prayer, labelKey: "nav.prayer" },
  { route: ROUTES.news, labelKey: "nav.news" },
  { route: ROUTES.tourism, labelKey: "nav.tourism" },
  { route: ROUTES.marketplace, labelKey: "nav.marketplace" },
] as const;

export function Header() {
  const { t } = useTranslation();
  const lang = useLang();
  const { pathname } = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);

  // Close the phone menu after navigating
  useEffect(() => {
    setMenuOpen(false);
  }, [pathname]);

  return (
    <header className={styles.header}>
      <div className={styles.inner}>
        <Link to={withLang(lang)} className={styles.brand}>
          <img src="/logo.jpg" alt="" width={44} height={44} />
          <span className={styles.brandText}>
            <strong>{t("brand.name")}</strong>
            <small>{t("brand.tagline")}</small>
          </span>
        </Link>

        <button
          type="button"
          className={styles.menuButton}
          aria-expanded={menuOpen}
          aria-controls="main-nav"
          onClick={() => setMenuOpen((open) => !open)}
        >
          {t("nav.menu")}
        </button>

        <nav id="main-nav" className={styles.nav} data-open={menuOpen} aria-label={t("nav.main")}>
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.labelKey}
              to={withLang(lang, item.route)}
              end={item.route === ROUTES.home}
              className={({ isActive }) =>
                isActive ? `${styles.link} ${styles.active}` : styles.link
              }
            >
              {t(item.labelKey)}
            </NavLink>
          ))}
        </nav>

        <LanguageSwitcher />
      </div>
    </header>
  );
}