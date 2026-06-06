"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { projectsApi } from "@/api/endpoints";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";

export default function ProjectsPage() {
  const qc = useQueryClient();
  const [name, setName] = useState("");
  const { data, isLoading } = useQuery({ queryKey: ["projects"], queryFn: projectsApi.list });
  const createMut = useMutation({
    mutationFn: () => projectsApi.create({ name }),
    onSuccess: () => {
      setName("");
      qc.invalidateQueries({ queryKey: ["projects"] });
    },
  });

  return (
    <AppShell>
      <h1 className="mb-4 text-2xl font-bold">프로젝트</h1>
      <Card className="mb-4">
        <form
          className="flex gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            if (name.trim()) createMut.mutate();
          }}
        >
          <Input placeholder="새 프로젝트 이름" value={name} onChange={(e) => setName(e.target.value)} />
          <Button type="submit" disabled={createMut.isPending}>
            생성
          </Button>
        </form>
      </Card>
      {isLoading ? (
        <Spinner />
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          {(data ?? []).map((p) => (
            <Link key={p.id} href={`/projects/${p.id}`}>
              <Card className="transition hover:border-brand-500">
                <h3 className="font-semibold">{p.name}</h3>
                <p className="mt-1 text-sm text-slate-500">{p.description ?? "설명 없음"}</p>
                <p className="mt-2 text-xs text-slate-400">{p.status}</p>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </AppShell>
  );
}
