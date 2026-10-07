import { useEffect, useState } from "react";
import { api, type Prediction } from "../api/client";

export default function History() {
  const [sessions, setSessions] = useState<{ session_id: string }[]>([]);
  const [sid, setSid] = useState("");
  const [items, setItems] = useState<(Prediction & { status: string })[]>([]);
  const [note, setNote] = useState("");

  async function refresh() {
    setNote("");
    try {
      const s = await api.sessions();
      setSessions(s.sessions);
      if (s.sessions.length && !sid) setSid(s.sessions[0].session_id);
    } catch (e) {
      setNote(e instanceof Error ? e.message : "Load failed.");
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  useEffect(() => {
    if (!sid) return;
    api
      .sessionPredictions(sid)
      .then((r) => setItems(r.predictions))
      .catch((e: Error) => setNote(e.message));
  }, [sid, sessions]);

  async function remove(pid?: string) {
    if (!pid) return;
    await api.deletePrediction(pid);
    setItems((xs) => xs.filter((x) => x.prediction_id !== pid));
  }

  return (
    <section aria-label="history">
      <h2>Recognition history</h2>
      <p>Stored predictions per session. Delete any entry or clear the session. Raw video is never stored.</p>
      <label>
        Session{" "}
        <select value={sid} onChange={(e) => setSid(e.target.value)} aria-label="session-select">
          {sessions.map((s) => (
            <option key={s.session_id} value={s.session_id}>
              {s.session_id}
            </option>
          ))}
        </select>
      </label>{" "}
      <button type="button" onClick={refresh}>
        Refresh
      </button>
      {note && <p role="alert">{note}</p>}
      <ul>
        {items.map((p) => (
          <li key={p.prediction_id ?? `${p.class_id}-${p.confidence}`}>
            {p.label} ({p.class_id}, {p.confidence}) — {p.status}{" "}
            <button type="button" onClick={() => remove(p.prediction_id)} aria-label={`delete-${p.prediction_id}`}>
              Delete
            </button>
          </li>
        ))}
      </ul>
      {items.length === 0 && <p>No predictions in this session yet.</p>}
    </section>
  );
}
