import { Center, Loader } from "@mantine/core";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { ROUTES } from "@/app/routes";
import { useLang } from "@/shared/hooks/useLang";
import { withLang } from "@/shared/lib/paths";
import { useAuth } from "./AuthProvider";

interface FromState {
  from?: string;
}

function PageLoader() {
  return (
    <Center py={80}>
      <Loader />
    </Center>
  );
}

/** Pages for signed-in users. Others go to sign-in and come back afterwards. */
export function RequireAuth() {
  const { status } = useAuth();
  const lang = useLang();
  const location = useLocation();

  if (status === "loading") return <PageLoader />;
  if (status === "anonymous") {
    const from = location.pathname + location.search;
    return <Navigate to={withLang(lang, ROUTES.signIn)} replace state={{ from } satisfies FromState} />;
  }
  return <Outlet />;
}

/** Sign-in / sign-up pages. Signed-in users are sent to where they were going, or home. */
export function GuestOnly() {
  const { status } = useAuth();
  const lang = useLang();
  const location = useLocation();

  if (status === "loading") return <PageLoader />;
  if (status === "authenticated") {
    const from = (location.state as FromState | null)?.from;
    return <Navigate to={from ?? withLang(lang)} replace />;
  }
  return <Outlet />;
}