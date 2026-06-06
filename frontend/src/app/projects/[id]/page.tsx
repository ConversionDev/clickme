"use client";

import { use } from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { adsApi, projectsApi, simulationsApi } from "@/api/endpoints";
import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";

export default function ProjectDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const project = useQuery({ queryKey: ["project", id], queryFn: () => projectsApi.get(id) });
  const ads = useQuery({ queryKey: ["ads", id], queryFn: () => adsApi.list(id) });
  const sims = useQuery({ queryKey: ["sims", id], queryFn: () => simulationsApi.list(id) });

  if (project.isLoading) return <AppShell><Spinner /></AppShell>;

  return (
    <AppShell>
      <h1 className="mb-2 text-2xl font-bold">{project.data?.name}</h1>
      <p className="mb-6 text-slate-500">{project.data?.description}</p>
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <h2 className="mb-3 font-semibold">광고</h2>
          <ul className="space-y-2 text-sm">
            {(ads.data ?? []).map((a) => (
              <li key={a.id} className="flex items-center justify-between">
                <span>{a.name}</span>
                <Badge>{a.input_type}</Badge>
              </li>
            ))}
          </ul>
          <Link href="/simulator" className="mt-3 inline-block text-sm text-brand-600">
            시뮬레이터에서 실행 →
          </Link>
        </Card>
        <Card>
          <h2 className="mb-3 font-semibold">시뮬레이션</h2>
          <ul className="space-y-2 text-sm">
            {(sims.data ?? []).map((s) => (
              <li key={s.id} className="flex items-center justify-between">
                <span>{s.id.slice(0, 8)}…</span>
                <Badge>{s.status}</Badge>
              </li>
            ))}
          </ul>
        </Card>
      </div>
    </AppShell>
  );
}
