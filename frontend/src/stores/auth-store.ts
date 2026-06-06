"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { TokenResponse, UserOut } from "@/api/types.gen";

const COOKIE_MAX_AGE = 60 * 60 * 24 * 14;

function setAuthCookies(role: string) {
  document.cookie = `clickme_auth=1; path=/; max-age=${COOKIE_MAX_AGE}; SameSite=Lax`;
  document.cookie = `clickme_role=${role}; path=/; max-age=${COOKIE_MAX_AGE}; SameSite=Lax`;
}

function clearAuthCookies() {
  document.cookie = "clickme_auth=; path=/; max-age=0";
  document.cookie = "clickme_role=; path=/; max-age=0";
}

type AuthState = {
  accessToken: string | null;
  refreshToken: string | null;
  user: UserOut | null;
  setSession: (data: TokenResponse) => void;
  setTokens: (access: string, refresh: string, role: string) => void;
  logout: () => void;
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      user: null,
      setSession: (data) => {
        setAuthCookies(data.user.role);
        set({
          accessToken: data.access_token,
          refreshToken: data.refresh_token,
          user: data.user,
        });
      },
      setTokens: (access, refresh, role) => {
        setAuthCookies(role);
        set({ accessToken: access, refreshToken: refresh });
      },
      logout: () => {
        clearAuthCookies();
        set({ accessToken: null, refreshToken: null, user: null });
      },
    }),
    { name: "clickme-auth" },
  ),
);
