import { Navigate, createBrowserRouter } from "react-router-dom";
import { GuestOnly, RequireAuth } from "@/features/auth/guards";
import { detectLang } from "@/i18n/storage";
import { AppLayout } from "@/layouts/AppLayout";
import { AccountPage } from "@/pages/account/AccountPage";
import { ForgotPasswordPage } from "@/pages/auth/ForgotPasswordPage";
import { ResetPasswordPage } from "@/pages/auth/ResetPasswordPage";
import { SignInPage } from "@/pages/auth/SignInPage";
import { SignUpPage } from "@/pages/auth/SignUpPage";
import { VerifyEmailPage } from "@/pages/auth/VerifyEmailPage";
import { ComingSoonPage } from "@/pages/ComingSoonPage";
import { HomePage } from "@/pages/home/HomePage";
import { NotFoundPage } from "@/pages/NotFoundPage";
import { withLang } from "@/shared/lib/paths";
import { ROUTES } from "./routes";
import { PrayerPage } from "@/pages/prayer/PrayerPage";

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
      { path: ROUTES.prayer, element: <PrayerPage /> },
      { path: ROUTES.news, element: <ComingSoonPage titleKey="nav.news" /> },
      { path: ROUTES.tourism, element: <ComingSoonPage titleKey="nav.tourism" /> },
      { path: ROUTES.marketplace, element: <ComingSoonPage titleKey="nav.marketplace" /> },

      // Email links work whether or not you're signed in
      { path: ROUTES.verifyEmail, element: <VerifyEmailPage /> },
      { path: ROUTES.resetPassword, element: <ResetPasswordPage /> },

      {
        element: <GuestOnly />,
        children: [
          { path: ROUTES.signIn, element: <SignInPage /> },
          { path: ROUTES.signUp, element: <SignUpPage /> },
          { path: ROUTES.forgotPassword, element: <ForgotPasswordPage /> },
        ],
      },
      {
        element: <RequireAuth />,
        children: [{ path: ROUTES.account, element: <AccountPage /> }],
      },

      { path: "*", element: <NotFoundPage /> },
    ],
  },
]);