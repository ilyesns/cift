import { env } from "@/config/env";
import i18n from "@/i18n";

/** Every backend error has the shape {"error": {"code", "message", "details"}}. */
export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
    public readonly details?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }

  get isClientError() {
    return this.status >= 400 && this.status < 500;
  }
}

/** Implemented by the auth feature; lets the client attach tokens and recover from expiry. */
export interface AuthAdapter {
  getAccessToken(): string | null;
  refresh(): Promise<boolean>;
}

let authAdapter: AuthAdapter | null = null;

export function setAuthAdapter(adapter: AuthAdapter): void {
  authAdapter = adapter;
}

// 401 codes that a fresh access token can fix
const RECOVERABLE_AUTH_CODES = new Set(["token_expired", "invalid_token", "not_authenticated"]);

type QueryValue = string | number | boolean | null | undefined;

export interface RequestOptions extends Omit<RequestInit, "body" | "method"> {
  body?: unknown;
  query?: Record<string, QueryValue>;
  /** Send no access token and never refresh (sign-in, refresh itself, public auth forms). */
  skipAuth?: boolean;
}

function buildUrl(path: string, query?: Record<string, QueryValue>): string {
  const url = new URL(`${env.apiUrl}${path}`, window.location.origin);
  for (const [key, value] of Object.entries(query ?? {})) {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, String(value));
    }
  }
  return url.toString();
}

async function request<T>(
  method: string,
  path: string,
  options: RequestOptions = {},
  isRetry = false,
): Promise<T> {
  const { body, query, headers, skipAuth, ...init } = options;

  const finalHeaders = new Headers(headers);
  finalHeaders.set("Accept", "application/json");
  finalHeaders.set("Accept-Language", i18n.language);

  const token = skipAuth ? null : (authAdapter?.getAccessToken() ?? null);
  if (token) finalHeaders.set("Authorization", `Bearer ${token}`);

  let payload: BodyInit | undefined;
  if (body instanceof FormData) {
    payload = body; // the browser sets the multipart boundary itself
  } else if (body !== undefined) {
    finalHeaders.set("Content-Type", "application/json");
    payload = JSON.stringify(body);
  }

  let res: Response;
  try {
    res = await fetch(buildUrl(path, query), {
      ...init,
      method,
      headers: finalHeaders,
      body: payload,
      credentials: "include", // sends the refresh cookie to /auth endpoints
    });
  } catch {
    throw new ApiError(0, "network_error", i18n.t("errors.network"));
  }

  if (res.status === 204) return undefined as T;

  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const err = data?.error;
    const code: string = err?.code ?? "error";

    if (
      res.status === 401 &&
      !skipAuth &&
      !isRetry &&
      authAdapter &&
      RECOVERABLE_AUTH_CODES.has(code) &&
      (await authAdapter.refresh())
    ) {
      return request<T>(method, path, options, true);
    }

    throw new ApiError(res.status, code, err?.message ?? i18n.t("errors.generic"), err?.details);
  }
  return data as T;
}

export const api = {
  get: <T>(path: string, options?: RequestOptions) => request<T>("GET", path, options),
  post: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>("POST", path, { ...options, body }),
  put: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>("PUT", path, { ...options, body }),
  patch: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>("PATCH", path, { ...options, body }),
  delete: <T = void>(path: string, options?: RequestOptions) =>
    request<T>("DELETE", path, options),
};