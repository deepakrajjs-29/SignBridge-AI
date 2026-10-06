/** T6.1 — WebSocket stream client (REST fallback kept in Live view). */
import type { Prediction } from "./client";

export type StreamState = string;

export interface StreamCallbacks {
  onStatus: (state: string, session_id: string) => void;
  onPrediction: (p: Prediction, state: string) => void;
  onError: (msg: string) => void;
}

export function connectStream(
  base: string,
  sessionId: string,
  cb: StreamCallbacks
): {
  sendFrame: (frame: number[]) => void;
  heartbeat: () => void;
  stop: () => void;
  socket: WebSocket;
} {
  const url = `${base.replace(/^http/, "ws")}/api/v1/stream?session_id=${sessionId}`;
  const socket = new WebSocket(url);
  socket.onopen = () => socket.send(JSON.stringify({ type: "start" }));
  socket.onmessage = (ev: MessageEvent) => {
    const m = JSON.parse(ev.data as string) as {
      type: string;
      state?: string;
      session_id?: string;
      prediction?: Prediction;
      message?: string;
    };
    if (m.type === "prediction" && m.prediction)
      cb.onPrediction(m.prediction, m.state ?? "Uncertain");
    else if (m.type === "status") cb.onStatus(m.state ?? "", m.session_id ?? "");
    else if (m.type === "error") cb.onError(m.message ?? "stream error");
  };
  socket.onerror = () => cb.onError("WebSocket error — use REST fallback.");
  return {
    sendFrame: (frame) => socket.send(JSON.stringify({ type: "frame", frame })),
    heartbeat: () => socket.send(JSON.stringify({ type: "heartbeat" })),
    stop: () => {
      try {
        socket.send(JSON.stringify({ type: "stop" }));
      } finally {
        socket.close();
      }
    },
    socket,
  };
}
