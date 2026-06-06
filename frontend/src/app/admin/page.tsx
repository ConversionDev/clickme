"use client";

import { useQuery } from "@tanstack/react-query";
import { adminApi } from "@/api/endpoints";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import Link from "next/link";

export default function AdminHomePage() {
  const usage = useQuery({ queryKey: ["admin", "usage"], queryFn: adminApi.usage });

  return (
    <AppShell admin>
      <h1 className="mb-4 text-2xl font-bold">관리자</h1>
      {usage.isLoading ? (
        <Spinner />
      ) : usage.data ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <Card>
            <p className="text-sm text-slate-500">사용자</p>
            <p className="text-3xl font-bold">{usage.data.user_count}</p>
          </Card>
          <Card>
            <p className="text-sm text-slate-500">조직</p>
            <p className="text-3xl font-bold">{usage.data.organization_count}</p>
          </Card>
          <Card>
            <p className="text-sm text-slate-500">시뮬레이션</p>
            <p className="text-3xl font-bold">{usage.data.simulation_count}</p>
          </Card>
          <Card>
            <p className="text-sm text-slate-500">완료 시뮬</p>
            <p className="text-3xl font-bold">{usage.data.completed_simulations}</p>
          </Card>
          <Card>
            <p className="text-sm text-slate-500">채팅 세션</p>
            <p className="text-3xl font-bold">{usage.data.chat_session_count}</p>
          </Card>
        </div>
      ) : null}
      <div className="mt-6 flex gap-3">
        <Link href="/admin/users" className="text-brand-600 hover:underline">
          회원 관리 →
        </Link>
        <Link href="/admin/chats" className="text-brand-600 hover:underline">
          채팅 기록 →
        </Link>
      </div>
    </AppShell>
  );
}
