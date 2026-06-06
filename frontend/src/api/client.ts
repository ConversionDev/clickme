import type { ApiResponse } from "./types.gen";
import { useAuthStore } from "@/stores/auth-store";

export class ApiError extends Error {
  constructor(
    public code: string,
    message: string,
    public status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

type RequestOptions = Omit<RequestInit, "body"> & {
  body?: unknown;
  auth?: boolean;
};

async function parseJson<T>(res: Response): Promise<ApiResponse<T>> {
  const json = (await res.json()) as ApiResponse<T>;
  if (!res.ok || !json.success) {
    throw new ApiError(
      json.error?.code ?? "INTERNAL",
      json.error?.message ?? res.statusText,
      res.status,
    );
  }
  return json;
}

async function refreshTokens(): Promise<boolean> {
  const { refreshToken, setTokens, logout } = useAuthStore.getState();
  if (!refreshToken) return false;
  try {
    const res = await fetch("/api/auth/refresh", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    const json = (await res.json()) as ApiResponse<{
      access_token: string;
      refresh_token: string;
      user: { role: string };
    }>;
    if (!res.ok || !json.success || !json.data) {
      logout();
      return false;
    }
    setTokens(json.data.access_token, json.data.refresh_token, json.data.user.role);
    return true;
  } catch {
    logout();
    return false;
  }
}

export async function api<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { body, auth = true, headers, ...rest } = options;
  const init: RequestInit = {
    ...rest,
    headers: {
      ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
      ...headers,
    },
  };
  if (body !== undefined) init.body = JSON.stringify(body);
  if (auth) {
    const token = useAuthStore.getState().accessToken;
    if (token) {
      (init.headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
    }
  }

  let res = await fetch(path, init);
  if (res.status === 401 && auth) {
    const ok = await refreshTokens();
    if (ok) {
      const token = useAuthStore.getState().accessToken;
      (init.headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
      res = await fetch(path, init);
    }
  }

  const json = await parseJson<T>(res);
  return json.data as T;
}

export async function apiForm<T>(path: string, form: FormData): Promise<T> {
  const token = useAuthStore.getState().accessToken;
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;

  let res = await fetch(path, { method: "POST", headers, body: form });
  if (res.status === 401) {
    const ok = await refreshTokens();
    if (ok) {
      headers["Authorization"] = `Bearer ${useAuthStore.getState().accessToken}`;
      res = await fetch(path, { method: "POST", headers, body: form });
    }
  }
  const json = await parseJson<T>(res);
  return json.data as T;
}
