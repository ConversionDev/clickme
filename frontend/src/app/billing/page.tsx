"use client";

import { useQuery } from "@tanstack/react-query";
import { billingApi } from "@/api/endpoints";
import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";

export default function BillingPage() {
  const { data, isLoading } = useQuery({ queryKey: ["billing"], queryFn: billingApi.plans });

  return (
    <AppShell>
      <h1 className="mb-2 text-2xl font-bold">요금제</h1>
      <p className="mb-6 text-sm text-slate-500">결제 연동 없음 — UI 스텁 (베이스라인)</p>
      {isLoading ? (
        <Spinner />
      ) : (
        <div className="grid gap-4 md:grid-cols-3">
          {(data ?? []).map((plan) => (
            <Card key={plan.plan_type} className={plan.is_current ? "border-brand-500" : ""}>
              <div className="flex items-center justify-between">
                <h3 className="font-semibold">{plan.display_name}</h3>
                {plan.is_current && <Badge className="bg-brand-100 text-brand-700">현재</Badge>}
              </div>
              <p className="mt-2 text-2xl font-bold">
                {plan.price_krw === 0 ? "무료" : `₩${plan.price_krw.toLocaleString()}/월`}
              </p>
              <ul className="mt-4 space-y-1 text-sm text-slate-600 dark:text-slate-300">
                {plan.features.map((f, i) => (
                  <li key={i}>· {String(f)}</li>
                ))}
              </ul>
              <Button className="mt-4 w-full" variant={plan.is_current ? "secondary" : "primary"} disabled>
                {plan.is_current ? "사용 중" : "업그레이드 (준비 중)"}
              </Button>
            </Card>
          ))}
        </div>
      )}
    </AppShell>
  );
}
