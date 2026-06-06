"use client";

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { adsApi, projectsApi, reportsApi, simulationsApi } from "@/api/endpoints";
import { subscribeSse } from "@/api/sse";
import type { SimulationDetailOut, SimulationEvent } from "@/api/types.gen";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";

const SEED_PROJECT = "10000000-0000-0000-0000-000000000001";
const SEED_AD = "20000000-0000-0000-0000-000000000001";

export function SimulatorPanel() {
  const qc = useQueryClient();
  const [projectId, setProjectId] = useState(SEED_PROJECT);
  const [adId, setAdId] = useState(SEED_AD);
  const [simId, setSimId] = useState<string | null>(null);
  const [events, setEvents] = useState<SimulationEvent[]>([]);
  const [running, setRunning] = useState(false);
  const [detail, setDetail] = useState<SimulationDetailOut | null>(null);
  const [uploading, setUploading] = useState(false);

  const projectsQuery = useQuery({ queryKey: ["projects"], queryFn: projectsApi.list });
  const adsQuery = useQuery({
    queryKey: ["ads", projectId],
    queryFn: () => adsApi.list(projectId),
    enabled: !!projectId,
  });

  async function startSimulation() {
    setRunning(true);
    setEvents([]);
    setDetail(null);
    const created = await simulationsApi.create(projectId, { ad_id: adId, persona_count: 20 });
    setSimId(created.id);

    await subscribeSse(`/api/simulations/${created.id}/events`, (_event, data) => {
      const ev = data as unknown as SimulationEvent;
      setEvents((prev) => [...prev, ev]);
      if (ev.type === "completed" || ev.type === "error") {
        setRunning(false);
        simulationsApi.get(created.id).then(setDetail);
        qc.invalidateQueries({ queryKey: ["dashboard"] });
      }
    });
    setRunning(false);
  }

  async function uploadImage(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    const form = new FormData();
    form.append("project_id", projectId);
    form.append("name", file.name);
    form.append("file", file);
    const ad = await adsApi.createMultipart(form);
    setAdId(ad.id);
    await qc.invalidateQueries({ queryKey: ["ads", projectId] });
    setUploading(false);
  }

  async function loadReport() {
    if (!simId) return;
    const d = await simulationsApi.get(simId);
    setDetail(d);
  }

  return (
    <div className="space-y-4">
      <Card>
        <h2 className="mb-4 text-lg font-semibold">광고 시뮬레이션</h2>
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <label className="mb-1 block text-sm font-medium">프로젝트</label>
            <select
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-900"
              value={projectId}
              onChange={(e) => setProjectId(e.target.value)}
            >
              {(projectsQuery.data ?? []).map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">광고</label>
            <select
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-900"
              value={adId}
              onChange={(e) => setAdId(e.target.value)}
            >
              {(adsQuery.data ?? []).map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name} ({a.input_type})
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          <label className="cursor-pointer">
            <span className="inline-flex rounded-lg border border-slate-300 px-4 py-2 text-sm hover:bg-slate-50 dark:border-slate-600">
              {uploading ? "업로드 중..." : "이미지 업로드"}
            </span>
            <input type="file" accept="image/jpeg,image/png,image/webp" className="hidden" onChange={uploadImage} />
          </label>
          <Button onClick={startSimulation} disabled={running || !projectId || !adId}>
            {running ? "실행 중..." : "시뮬레이션 시작"}
          </Button>
          {simId && (
            <Button variant="secondary" onClick={loadReport}>
              결과 새로고침
            </Button>
          )}
        </div>
      </Card>

      {(running || events.length > 0) && (
        <Card>
          <h3 className="mb-3 font-semibold">SSE 진행률</h3>
          {running && <Spinner className="mb-2" />}
          <ul className="max-h-48 space-y-1 overflow-y-auto text-sm">
            {events.map((ev, i) => (
              <li key={i} className="flex gap-2">
                <Badge>{ev.type}</Badge>
                <span>{ev.node ?? "-"}</span>
                <span className="text-slate-500">{ev.percent ?? 0}%</span>
                <span className="text-slate-500">{ev.message}</span>
              </li>
            ))}
          </ul>
        </Card>
      )}

      {detail && (
        <Card>
          <h3 className="mb-3 font-semibold">시뮬레이션 결과</h3>
          <p className="text-sm text-slate-500">상태: {detail.status}</p>
          {detail.prediction && (
            <div className="mt-3 grid gap-2 sm:grid-cols-2">
              <div className="rounded-lg bg-brand-50 p-4 dark:bg-brand-900/20">
                <p className="text-3xl font-bold">{detail.prediction.overall_score}</p>
                <p className="text-sm">{detail.prediction.verdict}</p>
              </div>
              <div className="text-sm">
                <p>클릭 의도: {(detail.prediction.kpi.click_intent_rate * 100).toFixed(0)}%</p>
                <p>전환 의도: {(detail.prediction.kpi.conversion_intent_rate * 100).toFixed(0)}%</p>
                <p>이해도: {(detail.prediction.kpi.comprehension_score * 100).toFixed(0)}%</p>
              </div>
            </div>
          )}
          {detail.recommendation && (
            <div className="mt-4 text-sm">
              <p className="font-medium">개선 제안</p>
              <ul className="mt-1 list-disc pl-5 text-slate-600 dark:text-slate-300">
                {detail.recommendation.copy_suggestions?.map((s, i) => (
                  <li key={i}>{String(s)}</li>
                ))}
              </ul>
            </div>
          )}
          {detail.report_id && (
            <ReportLink simulationId={detail.id} />
          )}
        </Card>
      )}
    </div>
  );
}

function ReportLink({ simulationId }: { simulationId: string }) {
  const { data, isLoading } = useQuery({
    queryKey: ["report", simulationId],
    queryFn: () => reportsApi.get(simulationId),
  });
  if (isLoading) return <Spinner className="mt-2" />;
  if (!data) return null;
  const summary = (data.report_data as { executiveSummary?: { overallScore?: number; verdict?: string } })
    ?.executiveSummary;
  return (
    <div className="mt-4 rounded-lg border border-slate-200 p-3 text-sm dark:border-slate-700">
      <p className="font-medium">리포트</p>
      {summary && (
        <p>
          점수 {summary.overallScore} — {summary.verdict}
        </p>
      )}
      <p className="mt-1 text-xs text-slate-400">{data.disclaimer}</p>
    </div>
  );
}
