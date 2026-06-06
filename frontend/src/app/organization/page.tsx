"use client";

import { useQuery } from "@tanstack/react-query";
import { usersApi } from "@/api/endpoints";
import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { useAuthStore } from "@/stores/auth-store";

export default function OrganizationPage() {
  const user = useAuthStore((s) => s.user);
  const orgId = user?.organization_id;
  const { data, isLoading } = useQuery({
    queryKey: ["org", orgId],
    queryFn: () => usersApi.organization(orgId!),
    enabled: !!orgId,
  });

  return (
    <AppShell>
      <h1 className="mb-4 text-2xl font-bold">조직</h1>
      {isLoading ? (
        <Spinner />
      ) : data ? (
        <Card>
          <h2 className="text-xl font-semibold">{data.name}</h2>
          <Badge className="mt-2">{data.plan_type}</Badge>
          <p className="mt-4 text-sm text-slate-500">
            생성일: {new Date(data.created_at).toLocaleDateString("ko-KR")}
          </p>
        </Card>
      ) : (
        <p className="text-slate-500">조직 정보를 불러올 수 없습니다.</p>
      )}
    </AppShell>
  );
}
