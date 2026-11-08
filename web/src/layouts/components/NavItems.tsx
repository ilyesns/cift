import { useTranslation } from "react-i18next";
import { NavLink } from "react-router-dom";
import { ROUTES } from "@/app/routes";
import { useLang } from "@/shared/hooks/useLang";
import { withLang } from "@/shared/lib/paths";
import classes from "./NavItems.module.css";

const NAV_ITEMS = [
  { route: ROUTES.home, labelKey: "nav.home" },
  { route: ROUTES.prayer, labelKey: "nav.prayer" },
  { route: ROUTES.news, labelKey: "nav.news" },
  { route: ROUTES.tourism, labelKey: "nav.tourism" },
  { route: ROUTES.marketplace, labelKey: "nav.marketplace" },
] as const;

export function NavItems({ variant }: { variant: "header" | "drawer" }) {
  const { t } = useTranslation();
  const lang = useLang();

  return (
    <>
      {NAV_ITEMS.map((item) => (
        <NavLink
          key={item.labelKey}
          to={withLang(lang, item.route)}
          end={item.route === ROUTES.home}
          className={classes.link}
          data-variant={variant}
        >
          {t(item.labelKey)}
        </NavLink>
      ))}
    </>
  );
}