"use client";

import { useQuery } from "@tanstack/react-query";
import { adminApi } from "@/api/endpoints";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";

export default function AdminChatsPage() {
  const { data, isLoading } = useQuery({ queryKey: ["admin", "chats"], queryFn: adminApi.chats });

  return (
    <AppShell admin>
      <h1 className="mb-4 text-2xl font-bold">채팅 기록</h1>
      {isLoading ? (
        <Spinner />
      ) : (
        <div className="space-y-2">
          {(data ?? []).map((c) => (
            <Card key={c.id} className="flex flex-wrap items-center justify-between gap-2">
              <div>
                <p className="font-medium">{c.title}</p>
                <p className="text-sm text-slate-500">{c.user_email}</p>
              </div>
              <p className="text-sm text-slate-400">
                메시지 {c.message_count} · {new Date(c.updated_at).toLocaleString("ko-KR")}
              </p>
            </Card>
          ))}
        </div>
      )}
    </AppShell>
  );
}
