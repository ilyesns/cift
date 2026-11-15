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

type QueryValue = string | number | boolean | null | undefined;

interface RequestOptions extends Omit<RequestInit, "body" | "method"> {
  body?: unknown;
  query?: Record<string, QueryValue>;
}

function buildUrl(path: string, query?: Record<string, QueryValue>): string {
  const url = new URL(`${env.apiUrl}${path}`);
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
  { body, query, headers, ...init }: RequestOptions = {},
): Promise<T> {
  const finalHeaders = new Headers(headers);
  finalHeaders.set("Accept", "application/json");
  finalHeaders.set("Accept-Language", i18n.language);
  // Sprint 1: finalHeaders.set("Authorization", `Bearer ${token}`) when signed in

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
      credentials: "include", // sends the refresh-token cookie from Sprint 1
    });
  } catch {
    throw new ApiError(0, "network_error", i18n.t("errors.network"));
  }

  if (res.status === 204) return undefined as T;

  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const err = data?.error;
    throw new ApiError(
      res.status,
      err?.code ?? "error",
      err?.message ?? i18n.t("errors.generic"),
      err?.details,
    );
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