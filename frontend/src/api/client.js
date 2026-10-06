const BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";
export function token() {
    return localStorage.getItem("sb_token") ?? "";
}
async function req(path, init) {
    const headers = { "Content-Type": "application/json" };
    const t = token();
    if (t)
        headers["Authorization"] = `Bearer ${t}`;
    const r = await fetch(`${BASE}${path}`, {
        ...init,
        headers: { ...headers, ...init?.headers },
    });
    const body = (await r.json());
    if (!r.ok || body.success === false) {
        const err = new Error(body.error?.message ?? `API ${r.status} on ${path}`);
        err.code = body.error?.code ?? `HTTP_${r.status}`;
        throw err;
    }
    return body;
}
export const api = {
    health: () => req("/health"),
    model: () => req("/api/v1/model"),
    classes: () => req("/api/v1/classes"),
    openSession: (user_id = "") => req("/api/v1/session", {
        method: "POST",
        body: JSON.stringify({ user_id }),
    }),
    closeSession: (sid) => req(`/api/v1/session/${sid}`, { method: "DELETE" }),
    predict: (frames, session_id = "", sequence_id = "") => req("/api/v1/predict", {
        method: "POST",
        body: JSON.stringify({ frames, session_id, sequence_id }),
    }),
    sessions: () => req("/api/v1/sessions"),
    sessionPredictions: (sid) => req(`/api/v1/sessions/${sid}/predictions`),
    deletePrediction: (pid) => req(`/api/v1/history/${pid}`, { method: "DELETE" }),
    tts: (text) => req("/api/v1/tts", { method: "POST", body: JSON.stringify({ text }) }),
    textToSign: (text) => req("/api/v1/text-to-sign", { method: "POST", body: JSON.stringify({ text }) }),
    adminModels: () => req("/api/v1/admin/models"),
    promote: (model_id, environment) => req("/api/v1/admin/promote", {
        method: "POST",
        body: JSON.stringify({ model_id, environment }),
    }),
    rollback: (model_id, environment) => req("/api/v1/admin/rollback", {
        method: "POST",
        body: JSON.stringify({ model_id, environment }),
    }),
};
