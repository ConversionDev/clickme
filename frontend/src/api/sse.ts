import { useAuthStore } from "@/stores/auth-store";

export type SseHandler = (event: string, data: Record<string, unknown>) => void;

/** fetch 기반 SSE — Authorization 헤더 지원 (EventSource 대체). */
export async function subscribeSse(
  path: string,
  onEvent: SseHandler,
  signal?: AbortSignal,
): Promise<void> {
  const token = useAuthStore.getState().accessToken;
  const res = await fetch(path, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    signal,
  });
  if (!res.ok || !res.body) {
    throw new Error(`SSE 연결 실패: ${res.status}`);
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
      if (dataLine) {
        try {
          onEvent(eventName, JSON.parse(dataLine) as Record<string, unknown>);
        } catch {
          onEvent(eventName, { raw: dataLine });
        }
      }
    }
  }
}
