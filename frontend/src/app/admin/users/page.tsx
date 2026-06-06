"use client";

import { useQuery } from "@tanstack/react-query";
import { adminApi } from "@/api/endpoints";
import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";

export default function AdminUsersPage() {
  const { data, isLoading } = useQuery({ queryKey: ["admin", "users"], queryFn: adminApi.users });

  return (
    <AppShell admin>
      <h1 className="mb-4 text-2xl font-bold">회원 관리</h1>
      {isLoading ? (
        <Spinner />
      ) : (
        <Card className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-700">
                <th className="py-2 pr-4">이름</th>
                <th className="py-2 pr-4">이메일</th>
                <th className="py-2 pr-4">역할</th>
                <th className="py-2">상태</th>
              </tr>
            </thead>
            <tbody>
              {(data ?? []).map((u) => (
                <tr key={u.id} className="border-b border-slate-100 dark:border-slate-800">
                  <td className="py-2 pr-4">{u.name}</td>
                  <td className="py-2 pr-4">{u.email}</td>
                  <td className="py-2 pr-4">
                    <Badge>{u.role}</Badge>
                  </td>
                  <td className="py-2">{u.is_active ? "활성" : "비활성"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
    </AppShell>
  );
}
