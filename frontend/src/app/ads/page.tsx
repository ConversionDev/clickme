"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { adsApi, projectsApi } from "@/api/endpoints";
import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";

const SEED_PROJECT = "10000000-0000-0000-0000-000000000001";

export default function AdsPage() {
  const qc = useQueryClient();
  const [projectId, setProjectId] = useState(SEED_PROJECT);
  const [headline, setHeadline] = useState("");
  const [body, setBody] = useState("");
  const [cta, setCta] = useState("지금 구매하기");

  const projects = useQuery({ queryKey: ["projects"], queryFn: projectsApi.list });
  const ads = useQuery({
    queryKey: ["ads", projectId],
    queryFn: () => adsApi.list(projectId),
    enabled: !!projectId,
  });

  const createText = useMutation({
    mutationFn: () =>
      adsApi.createText({
        project_id: projectId,
        name: headline || "텍스트 광고",
        headline,
        body,
        cta,
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["ads", projectId] }),
  });

  return (
    <AppShell>
      <h1 className="mb-4 text-2xl font-bold">광고</h1>
      <Card className="mb-4 space-y-3">
        <select
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-900"
          value={projectId}
          onChange={(e) => setProjectId(e.target.value)}
        >
          {(projects.data ?? []).map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
        <Input placeholder="헤드라인" value={headline} onChange={(e) => setHeadline(e.target.value)} />
        <Input placeholder="본문" value={body} onChange={(e) => setBody(e.target.value)} />
        <Input placeholder="CTA" value={cta} onChange={(e) => setCta(e.target.value)} />
        <Button
          onClick={() => createText.mutate()}
          disabled={createText.isPending || !headline || !body}
        >
          텍스트 광고 생성
        </Button>
      </Card>
      {ads.isLoading ? (
        <Spinner />
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          {(ads.data ?? []).map((a) => (
            <Card key={a.id}>
              <div className="flex items-start justify-between">
                <h3 className="font-semibold">{a.name}</h3>
                <Badge>{a.input_type}</Badge>
              </div>
              {a.storage_url && (
                <img src={a.storage_url} alt={a.name} className="mt-2 max-h-32 rounded-lg object-cover" />
              )}
              {a.text_content && (
                <pre className="mt-2 overflow-auto text-xs text-slate-500">
                  {JSON.stringify(a.text_content, null, 2)}
                </pre>
              )}
            </Card>
          ))}
        </div>
      )}
    </AppShell>
  );
}
