import { AppShell } from "@/components/layout/app-shell";
import { SimulatorPanel } from "@/features/simulator/simulator-panel";

export default function SimulatorPage() {
  return (
    <AppShell>
      <h1 className="mb-4 text-2xl font-bold">시뮬레이터</h1>
      <SimulatorPanel />
    </AppShell>
  );
}
