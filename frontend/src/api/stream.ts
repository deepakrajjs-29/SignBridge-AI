/** T6.1 — WebSocket stream client (REST fallback kept in Live view). */
import { token } from "./client";
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
  ready?: Promise<void>;
} {
  const t = token();
  const wsPrefix = base
    ? base.replace(/^http/, "ws")
    : typeof window !== "undefined"
    ? `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.host}`
    : "ws://127.0.0.1:8000";
  const url =
    `${wsPrefix}/api/v1/stream?session_id=${sessionId}` +
    `&token=${encodeURIComponent(t ?? "")}`;
  const socket = new WebSocket(url);
  // Frames sent before the handshake completes must wait: a synchronous
  // send() on a CONNECTING socket throws InvalidStateError, which used to
  // kill every stream-first attempt from Live (silent REST fallback).
  const pending: string[] = [];
  let resolveReady: () => void = () => {};
  let rejectReady: (e: Error) => void = () => {};
  const ready = new Promise<void>((res, rej) => {
    resolveReady = res;
    rejectReady = rej;
  });
  // Swallow late rejections when nobody awaits (e.g. immediate fallback).
  ready.catch(() => {});
  const sendRaw = (data: string) => {
    if (socket.readyState === WebSocket.OPEN) socket.send(data);
    else if (socket.readyState === WebSocket.CONNECTING) pending.push(data);
    // CLOSING/CLOSED: drop — the session is over, never throw into callers.
  };
  socket.onopen = () => {
    socket.send(JSON.stringify({ type: "start" }));
    for (const d of pending.splice(0)) socket.send(d);
    resolveReady();
  };
  socket.onmessage = (ev: MessageEvent) => {
    let m: {
      type: string;
      state?: string;
      session_id?: string;
      prediction?: Prediction;
      message?: string;
    };
    try {
      m = JSON.parse(ev.data as string);
    } catch {
      cb.onError("Malformed stream message — used REST fallback.");
      return;
    }
    if (m.type === "prediction" && m.prediction)
      cb.onPrediction(m.prediction, m.state ?? "Uncertain");
    else if (m.type === "status") cb.onStatus(m.state ?? "", m.session_id ?? "");
    else if (m.type === "error") cb.onError(m.message ?? "stream error");
  };
  socket.onerror = () => {
    rejectReady(new Error("WebSocket error — use REST fallback."));
    cb.onError("WebSocket error — use REST fallback.");
  };
  socket.onclose = (e) => {
    if (e.code === 4401) cb.onError("Unauthorized stream (bad token).");
    else if (e.code === 4404) cb.onError("Unknown session — re-open session and retry.");
    rejectReady(new Error(`stream closed (${e.code})`));
  };
  return {
    sendFrame: (frame) => sendRaw(JSON.stringify({ type: "frame", frame })),
    heartbeat: () => sendRaw(JSON.stringify({ type: "heartbeat" })),
    stop: () => {
      try {
        if (socket.readyState === WebSocket.OPEN)
          socket.send(JSON.stringify({ type: "stop" }));
      } finally {
        socket.close();
      }
    },
    socket,
    ready,
  };
}
