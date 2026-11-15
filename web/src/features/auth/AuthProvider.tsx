import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  useSyncExternalStore,
  type ReactNode,
} from "react";
import { session } from "./session";
import type { User } from "./types";

type AuthStatus = "loading" | "authenticated" | "anonymous";

interface AuthContextValue {
  user: User | null;
  status: AuthStatus;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const user = useSyncExternalStore(session.subscribe, session.getUser);
  const [restored, setRestored] = useState(false);

  // On first load, try to restore the session from the refresh cookie
  useEffect(() => {
    void session.refresh().finally(() => setRestored(true));
  }, []);

  const status: AuthStatus = !restored ? "loading" : user ? "authenticated" : "anonymous";
  const value = useMemo(() => ({ user, status }), [user, status]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside <AuthProvider>");
  return context;
}