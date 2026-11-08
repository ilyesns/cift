import { useLayoutEffect } from "react";
import { Navigate, Outlet, useLocation, useParams } from "react-router-dom";
import { applyLang } from "@/i18n";
import { isLang } from "@/i18n/languages";
import { detectLang } from "@/i18n/storage";
import { swapLang } from "@/shared/lib/paths";
import styles from "./AppLayout.module.css";
import { Footer } from "./components/Footer";
import { Header } from "./components/Header";

export function AppLayout() {
  const { lang } = useParams();
  const { pathname } = useLocation();

  // Layout effect: switch lang/dir before the browser paints, so Arabic never flashes LTR
  useLayoutEffect(() => {
    if (isLang(lang)) applyLang(lang);
  }, [lang]);

  if (!isLang(lang)) {
    return <Navigate to={swapLang(pathname, detectLang())} replace />;
  }

  return (
    <div className={styles.shell}>
      <Header />
      <main className={styles.main}>
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}