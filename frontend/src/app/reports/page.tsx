"use client";

import { useQuery } from "@tanstack/react-query";
import { reportsApi } from "@/api/endpoints";
import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";

export default function ReportsPage() {
  const { data, isLoading } = useQuery({ queryKey: ["reports"], queryFn: reportsApi.list });

  return (
    <AppShell>
      <h1 className="mb-4 text-2xl font-bold">리포트 기록</h1>
      {isLoading ? (
        <Spinner />
      ) : (
        <div className="space-y-3">
          {(data ?? []).map((r) => {
            const summary = (r.report_data as { executiveSummary?: { overallScore?: number; verdict?: string } })
              ?.executiveSummary;
            return (
              <Card key={r.id}>
                <p className="font-medium">시뮬레이션 {r.simulation_id.slice(0, 8)}…</p>
                {summary && (
                  <p className="mt-1 text-sm">
                    점수 {summary.overallScore} — {summary.verdict}
                  </p>
                )}
                <p className="mt-2 text-xs text-slate-400">{new Date(r.created_at).toLocaleString("ko-KR")}</p>
              </Card>
            );
          })}
          {(data ?? []).length === 0 && <p className="text-slate-500">리포트가 없습니다.</p>}
        </div>
      )}
    </AppShell>
  );
}
