"use client";

import { useQuery } from "@tanstack/react-query";
import { reportsApi } from "@/api/endpoints";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";

export default function DashboardPage() {
  const { data, isLoading } = useQuery({ queryKey: ["dashboard"], queryFn: reportsApi.dashboard });

  return (
    <AppShell>
      <h1 className="mb-4 text-2xl font-bold">대시보드</h1>
      {isLoading ? (
        <Spinner />
      ) : data ? (
        <div className="grid gap-4 sm:grid-cols-3">
          <Card>
            <p className="text-sm text-slate-500">프로젝트</p>
            <p className="text-3xl font-bold">{data.project_count}</p>
          </Card>
          <Card>
            <p className="text-sm text-slate-500">시뮬레이션</p>
            <p className="text-3xl font-bold">{data.simulation_count}</p>
          </Card>
          <Card>
            <p className="text-sm text-slate-500">완료</p>
            <p className="text-3xl font-bold">{data.completed_simulations}</p>
          </Card>
          <Card className="sm:col-span-3">
            <h2 className="mb-3 font-semibold">최근 리포트</h2>
            <ul className="space-y-2 text-sm">
              {data.recent_reports.map((r) => (
                <li key={r.id}>시뮬 {r.simulation_id.slice(0, 8)}… — {new Date(r.created_at).toLocaleDateString("ko-KR")}</li>
              ))}
            </ul>
          </Card>
        </div>
      ) : null}
    </AppShell>
  );
}
