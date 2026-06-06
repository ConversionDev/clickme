"use client";

import { useEffect } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { usersApi } from "@/api/endpoints";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { useThemeStore } from "@/stores/theme-store";

export default function SettingsPage() {
  const qc = useQueryClient();
  const { theme, setTheme } = useThemeStore();
  const profile = useQuery({ queryKey: ["me"], queryFn: usersApi.me });
  const settings = useQuery({ queryKey: ["settings"], queryFn: usersApi.settings });

  useEffect(() => {
    if (settings.data?.theme === "light" || settings.data?.theme === "dark") {
      setTheme(settings.data.theme);
    }
  }, [settings.data?.theme, setTheme]);

  const saveTheme = useMutation({
    mutationFn: (t: "light" | "dark") => usersApi.updateSettings({ theme: t }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["settings"] }),
  });

  return (
    <AppShell>
      <h1 className="mb-4 text-2xl font-bold">설정</h1>
      {profile.isLoading ? (
        <Spinner />
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <h2 className="mb-3 font-semibold">프로필</h2>
            <p className="text-sm">{profile.data?.name}</p>
            <p className="text-sm text-slate-500">{profile.data?.email}</p>
            <p className="mt-2 text-xs text-slate-400">역할: {profile.data?.role}</p>
          </Card>
          <Card>
            <h2 className="mb-3 font-semibold">테마 (다크모드)</h2>
            <div className="flex gap-2">
              <Button
                variant={theme === "light" ? "primary" : "secondary"}
                onClick={() => {
                  setTheme("light");
                  saveTheme.mutate("light");
                }}
              >
                라이트
              </Button>
              <Button
                variant={theme === "dark" ? "primary" : "secondary"}
                onClick={() => {
                  setTheme("dark");
                  saveTheme.mutate("dark");
                }}
              >
                다크
              </Button>
            </div>
          </Card>
        </div>
      )}
    </AppShell>
  );
}
