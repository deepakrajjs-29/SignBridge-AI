export function getBaseUrl(): string {
  if (typeof window !== "undefined") {
    const envBase = import.meta.env.VITE_API_BASE;
    return envBase && envBase.trim() !== "" ? envBase.trim() : "";
  }
  return import.meta.env.VITE_API_BASE || "http://localhost:8000";
}

export const BASE = getBaseUrl();

export const PREDICT_TIMEOUT_MS = 120_000;
export const DEFAULT_TIMEOUT_MS = 15_000;

export function token(): string {
  return localStorage.getItem("sb_token") || "change-me";
}

export function setToken(newToken: string): void {
  localStorage.setItem("sb_token", newToken);
}

export async function fetchWithTimeout(
  url: string,
  init: RequestInit | undefined,
  ms: number
): Promise<Response> {
  const controller = new AbortController();
  const userSignal = init?.signal as AbortSignal | undefined;
  if (userSignal) {
    if (userSignal.aborted) controller.abort();
    else userSignal.addEventListener("abort", () => controller.abort(), { once: true });
  }
  let timer: ReturnType<typeof setTimeout> | undefined;
  const timeout = new Promise<never>((_, reject) => {
    timer = setTimeout(() => {
      controller.abort();
      const err = new Error(`Request timed out after ${ms} ms — retry.`);
      (err as { code?: string }).code = "TIMEOUT";
      reject(err);
    }, ms);
  });
  try {
    return await Promise.race([fetch(url, { ...init, signal: controller.signal }), timeout]);
  } finally {
    if (timer !== undefined) clearTimeout(timer);
  }
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const t = token();
  if (t) headers["Authorization"] = `Bearer ${t}`;
  const ms = path.startsWith("/api/v1/predict") ? PREDICT_TIMEOUT_MS : DEFAULT_TIMEOUT_MS;
  const r = await fetchWithTimeout(
    `${BASE}${path}`,
    {
      ...init,
      headers: { ...headers, ...(init?.headers as Record<string, string> | undefined) },
    },
    ms
  );
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

export interface ModelInfo {
  model_id: string;
  model_version: string;
  seq_len: number;
  feat_dim: number;
  architecture: string;
}

export interface ClassItem {
  class_id: string;
  label: string;
  sign_type: string;
}

export interface SessionItem {
  session_id: string;
  user_id?: string;
  created?: number;
  status?: string;
  live_predictions?: number;
}

export interface AdminModelItem {
  model_id: string;
  version: string;
  status: string;
}

export const api = {
  health: () => req<{ success: boolean; status: string; model_version: string; request_id: string }>("/health"),
  model: () => req<{ success: boolean; model: ModelInfo; request_id: string }>("/api/v1/model"),
  classes: () =>
    req<{ success: boolean; count: number; classes: ClassItem[]; request_id: string }>(
      "/api/v1/classes"
    ),
  openSession: (user_id = "") =>
    req<{ success: boolean; session_id: string; request_id: string }>("/api/v1/session", {
      method: "POST",
      body: JSON.stringify({ user_id }),
    }),
  resetSession: () =>
    req<{ success: boolean; request_id: string }>("/api/v1/session/reset", {
      method: "POST",
    }),
  closeSession: (sid: string) =>
    req<{ success: boolean; session_id: string; request_id: string }>(`/api/v1/session/${sid}`, {
      method: "DELETE",
    }),
  purgeSession: (sid: string) =>
    req<{ success: boolean; session_id: string; request_id: string }>(`/api/v1/sessions/${sid}/purge`, {
      method: "DELETE",
    }),
  predict: (frames: number[][], session_id = "", sequence_id = "") =>
    req<{
      success: boolean;
      prediction: Prediction;
      status: string;
      model_version: string;
      processing_time_ms: number;
      sequence_id?: string;
      request_id?: string;
    }>("/api/v1/predict", {
      method: "POST",
      body: JSON.stringify({ frames, session_id, sequence_id }),
    }),
  sessions: (limit = 50) =>
    req<{ success: boolean; sessions: SessionItem[]; request_id?: string }>(`/api/v1/sessions?limit=${limit}`),
  sessionPredictions: (sid: string, limit = 50) =>
    req<{ success: boolean; predictions: (Prediction & { status: string; timestamp?: number; created?: string })[]; request_id?: string }>(
      `/api/v1/sessions/${sid}/predictions?limit=${limit}`
    ),
  deletePrediction: (pid: string) =>
    req<{ success: boolean; request_id?: string }>(`/api/v1/history/${pid}`, { method: "DELETE" }),
  feedback: (prediction_id: string, actual_class_id?: string, rating?: number) =>
    req<{ success: boolean; request_id?: string }>("/api/v1/feedback", {
      method: "POST",
      body: JSON.stringify({ prediction_id, actual_class_id, rating }),
    }),
  tts: (text: string) =>
    req<{ success: boolean; audio_url?: string; request_id?: string }>("/api/v1/tts", {
      method: "POST",
      body: JSON.stringify({ text }),
    }),
  textToSign: (text: string) =>
    req<{
      success: boolean;
      items: { word: string; class_id: string; label: string; supported: boolean }[];
      unsupported_words: string[];
      request_id?: string;
    }>("/api/v1/text-to-sign", { method: "POST", body: JSON.stringify({ text }) }),
  adminModels: () =>
    req<{ success: boolean; models: AdminModelItem[]; request_id?: string }>(
      "/api/v1/admin/models"
    ),
  promote: (model_id: string, environment = "production") =>
    req<{ success: boolean; request_id?: string }>("/api/v1/admin/promote", {
      method: "POST",
      body: JSON.stringify({ model_id, environment }),
    }),
  rollback: (model_id: string, environment = "production") =>
    req<{ success: boolean; request_id?: string }>("/api/v1/admin/rollback", {
      method: "POST",
      body: JSON.stringify({ model_id, environment }),
    }),
};
