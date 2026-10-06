const BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

export function token(): string {
  return localStorage.getItem("sb_token") || "change-me";
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const t = token();
  if (t) headers["Authorization"] = `Bearer ${t}`;
  const r = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { ...headers, ...(init?.headers as Record<string, string> | undefined) },
  });
  const body = (await r.json()) as T & { success: boolean; error?: { code: string; message: string } };
  if (!r.ok || body.success === false) {
    const err = new Error(body.error?.message ?? `API ${r.status} on ${path}`);
    (err as { code?: string }).code = body.error?.code ?? `HTTP_${r.status}`;
    throw err;
  }
  return body;
}

export type RecState =
  | "Ready"
  | "Tracking"
  | "Recognized"
  | "Uncertain"
  | "No-Sign"
  | "Tracking-Lost"
  | "Error";

export interface Prediction {
  class_id: string;
  label: string;
  confidence: number;
  prediction_id?: string;
}

export const api = {
  health: () => req<{ status: string }>("/health"),
  model: () => req<{ model: { model_id: string; model_version: string } }>("/api/v1/model"),
  classes: () =>
    req<{ count: number; classes: { class_id: string; label: string; sign_type: string }[] }>(
      "/api/v1/classes"
    ),
  openSession: (user_id = "") =>
    req<{ session_id: string }>("/api/v1/session", {
      method: "POST",
      body: JSON.stringify({ user_id }),
    }),
  closeSession: (sid: string) =>
    req(`/api/v1/session/${sid}`, { method: "DELETE" }),
  predict: (frames: number[][], session_id = "", sequence_id = "") =>
    req<{
      prediction: Prediction;
      status: string;
      model_version: string;
      processing_time_ms: number;
    }>("/api/v1/predict", {
      method: "POST",
      body: JSON.stringify({ frames, session_id, sequence_id }),
    }),
  sessions: () => req<{ sessions: { session_id: string; status?: string }[] }>("/api/v1/sessions"),
  sessionPredictions: (sid: string) =>
    req<{ predictions: (Prediction & { status: string })[] }>(`/api/v1/sessions/${sid}/predictions`),
  deletePrediction: (pid: string) => req(`/api/v1/history/${pid}`, { method: "DELETE" }),
  tts: (text: string) =>
    req<{ audio_url?: string }>("/api/v1/tts", { method: "POST", body: JSON.stringify({ text }) }),
  textToSign: (text: string) =>
    req<{
      items: { word: string; class_id: string; label: string; supported: boolean }[];
      unsupported_words: string[];
    }>("/api/v1/text-to-sign", { method: "POST", body: JSON.stringify({ text }) }),
  adminModels: () =>
    req<{ models: { model_id: string; version: string; status: string }[] }>(
      "/api/v1/admin/models"
    ),
  promote: (model_id: string, environment: string) =>
    req("/api/v1/admin/promote", {
      method: "POST",
      body: JSON.stringify({ model_id, environment }),
    }),
  rollback: (model_id: string, environment: string) =>
    req("/api/v1/admin/rollback", {
      method: "POST",
      body: JSON.stringify({ model_id, environment }),
    }),
};
