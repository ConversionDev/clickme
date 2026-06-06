import { AppShell } from "@/components/layout/app-shell";
import { ChatPanel } from "@/features/chat/chat-panel";

export default async function ChatSessionPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <AppShell>
      <h1 className="mb-4 text-2xl font-bold">채팅</h1>
      <ChatPanel sessionId={id} />
    </AppShell>
  );
}
