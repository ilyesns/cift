import { setAuthAdapter } from "@/shared/api/client";
import { authApi } from "./api";
import type { Session, User } from "./types";

// The access token lives only in memory. The refresh token is an httpOnly cookie JS can't read.
let accessToken: string | null = null;
let currentUser: User | null = null;
let refreshing: Promise<boolean> | null = null;
const listeners = new Set<() => void>();

function setUser(user: User | null) {
  currentUser = user;
  listeners.forEach((listener) => listener());
}

export const session = {
  getUser: (): User | null => currentUser,
  getAccessToken: (): string | null => accessToken,

  subscribe(listener: () => void): () => void {
    listeners.add(listener);
    return () => {
      listeners.delete(listener);
    };
  },

  start(data: Session): void {
    accessToken = data.access_token;
    setUser(data.user);
  },

  setUser,

  clear(): void {
    accessToken = null;
    setUser(null);
  },

  /** Get a new access token from the refresh cookie. Parallel callers share one request. */
  refresh(): Promise<boolean> {
    if (!refreshing) {
      refreshing = authApi
        .refresh()
        .then((data) => {
          session.start(data);
          return true;
        })
        .catch(() => {
          session.clear();
          return false;
        })
        .finally(() => {
          refreshing = null;
        });
    }
    return refreshing;
  },
};

setAuthAdapter({
  getAccessToken: session.getAccessToken,
  refresh: session.refresh,
});