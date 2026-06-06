"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { chatApi } from "@/api/endpoints";
import type { ChatMessageOut } from "@/api/types.gen";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { cn } from "@/lib/cn";

export function ChatPanel({ sessionId }: { sessionId?: string }) {
  const router = useRouter();
  const qc = useQueryClient();
  const bottomRef = useRef<HTMLDivElement>(null);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState("");
  const [sending, setSending] = useState(false);
  const [localMessages, setLocalMessages] = useState<ChatMessageOut[]>([]);

  const sessionsQuery = useQuery({
    queryKey: ["chat", "sessions"],
    queryFn: chatApi.sessions,
  });

  const messagesQuery = useQuery({
    queryKey: ["chat", "messages", sessionId],
    queryFn: () => chatApi.messages(sessionId!),
    enabled: !!sessionId,
  });

  useEffect(() => {
    if (messagesQuery.data) setLocalMessages(messagesQuery.data);
  }, [messagesQuery.data]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [localMessages, streaming]);

  async function createSession() {
    const s = await chatApi.createSession({ title: "새 채팅" });
    await qc.invalidateQueries({ queryKey: ["chat", "sessions"] });
    router.push(`/chat/${s.id}`);
  }

  async function sendMessage() {
    if (!sessionId || !input.trim() || sending) return;
    setSending(true);
    setStreaming("");
    const content = input.trim();
    setInput("");

    const token = (await import("@/stores/auth-store")).useAuthStore.getState().accessToken;
    const res = await fetch(chatApi.sendMessagePath(sessionId), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(chatApi.sendMessageBody({ content })),
    });
    if (!res.ok || !res.body) {
      setSending(false);
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let eventName = "message";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const parts = buffer.split("\n\n");
      buffer = parts.pop() ?? "";
      for (const block of parts) {
        if (!block.trim() || block.startsWith(":")) continue;
        let dataLine = "";
        for (const line of block.split("\n")) {
          if (line.startsWith("event:")) eventName = line.slice(6).trim();
          if (line.startsWith("data:")) dataLine += line.slice(5).trim();
        }
        if (!dataLine) continue;
        const data = JSON.parse(dataLine) as Record<string, unknown>;
        if (data.type === "token") setStreaming((p) => p + String(data.content ?? ""));
        if (data.type === "user_message") {
          setLocalMessages((p) => [...p, data.message as ChatMessageOut]);
        }
        if (data.type === "done") {
          setLocalMessages((p) => [...p, data.message as ChatMessageOut]);
          setStreaming("");
        }
      }
    }
    setSending(false);
    qc.invalidateQueries({ queryKey: ["chat", "messages", sessionId] });
  }

  return (
    <div className="grid gap-4 lg:grid-cols-[240px_1fr]">
      <Card className="h-fit">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="font-semibold">세션</h2>
          <Button size="sm" onClick={createSession}>
            새 채팅
          </Button>
        </div>
        {sessionsQuery.isLoading ? (
          <Spinner />
        ) : (
          <ul className="space-y-1">
            {(sessionsQuery.data ?? []).map((s) => (
              <li key={s.id}>
                <button
                  type="button"
                  onClick={() => router.push(`/chat/${s.id}`)}
                  className={cn(
                    "w-full rounded-lg px-2 py-1.5 text-left text-sm hover:bg-slate-100 dark:hover:bg-slate-800",
                    sessionId === s.id && "bg-brand-50 text-brand-700 dark:bg-brand-700/20",
                  )}
                >
                  {s.title}
                </button>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <Card className="flex min-h-[480px] flex-col">
        {!sessionId ? (
          <div className="flex flex-1 flex-col items-center justify-center text-slate-500">
            <p>메인 RAG 채팅 — 세션을 선택하거나 새 채팅을 시작하세요.</p>
            <Button className="mt-4" onClick={createSession}>
              새 채팅 시작
            </Button>
          </div>
        ) : (
          <>
            <div className="flex-1 space-y-3 overflow-y-auto pr-2">
              {messagesQuery.isLoading && <Spinner />}
              {localMessages.map((m) => (
                <div
                  key={m.id}
                  className={cn(
                    "max-w-[85%] rounded-xl px-3 py-2 text-sm",
                    m.role === "user"
                      ? "ml-auto bg-brand-600 text-white"
                      : "bg-slate-100 dark:bg-slate-800",
                  )}
                >
                  <p className="whitespace-pre-wrap">{m.content}</p>
                </div>
              ))}
              {streaming && (
                <div className="max-w-[85%] rounded-xl bg-slate-100 px-3 py-2 text-sm dark:bg-slate-800">
                  <p className="whitespace-pre-wrap">{streaming}</p>
                </div>
              )}
              <div ref={bottomRef} />
            </div>
            <form
              className="mt-4 flex gap-2"
              onSubmit={(e) => {
                e.preventDefault();
                sendMessage();
              }}
            >
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="광고 시뮬 결과에 대해 질문하세요..."
                disabled={sending}
              />
              <Button type="submit" disabled={sending || !input.trim()}>
                {sending ? "..." : "전송"}
              </Button>
            </form>
          </>
        )}
      </Card>
    </div>
  );
}
