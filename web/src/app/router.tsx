import { Navigate, createBrowserRouter } from "react-router-dom";
import { detectLang } from "@/i18n/storage";
import { AppLayout } from "@/layouts/AppLayout";
import { ComingSoonPage } from "@/pages/ComingSoonPage";
import { HomePage } from "@/pages/home/HomePage";
import { NotFoundPage } from "@/pages/NotFoundPage";
import { withLang } from "@/shared/lib/paths";
import { ROUTES } from "./routes";

function RootRedirect() {
  return <Navigate to={withLang(detectLang())} replace />;
}

export const router = createBrowserRouter([
  { path: "/", element: <RootRedirect /> },
  {
    path: "/:lang",
    element: <AppLayout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: ROUTES.prayer, element: <ComingSoonPage titleKey="nav.prayer" /> },
      { path: ROUTES.news, element: <ComingSoonPage titleKey="nav.news" /> },
      { path: ROUTES.tourism, element: <ComingSoonPage titleKey="nav.tourism" /> },
      { path: ROUTES.marketplace, element: <ComingSoonPage titleKey="nav.marketplace" /> },
      { path: "*", element: <NotFoundPage /> },
    ],
  },
]);