import { AppShell } from "@/components/layout/app-shell";
import { ChatPanel } from "@/features/chat/chat-panel";

export default function HomePage() {
  return (
    <AppShell>
      <h1 className="mb-4 text-2xl font-bold">메인 채팅</h1>
      <ChatPanel />
    </AppShell>
  );
}
