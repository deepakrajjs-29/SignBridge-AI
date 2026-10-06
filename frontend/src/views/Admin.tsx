import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function Admin() {
  const [models, setModels] = useState<{ model_id: string; version: string; status: string }[]>([]);
  const [note, setNote] = useState("");
  const [denied, setDenied] = useState(false);

  async function load() {
    setNote("");
    setDenied(false);
    try {
      const r = await api.adminModels();
      setModels(r.models);
    } catch (e) {
      if (e instanceof Error && (e.message.includes("401") || e.message.includes("Bearer"))) {
        setDenied(true);
        setNote("Admin requires a token: set it in Settings → API token.");
      } else setNote(e instanceof Error ? e.message : "Load failed.");
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function act(kind: "promote" | "rollback", model_id: string) {
    setNote("");
    try {
      if (kind === "promote") await api.promote(model_id, "production");
      else await api.rollback(model_id, "production");
      setNote(`${kind} recorded for ${model_id} (audit-logged).`);
      await load();
    } catch (e) {
      setNote(e instanceof Error ? e.message : "Action failed.");
    }
  }

  return (
    <section aria-label="admin">
      <h2>Model administration</h2>
      {denied && <p role="alert">Not authorized — admin is RBAC-gated.</p>}
      {note && <p role="status">{note}</p>}
      <button type="button" onClick={load}>
        Refresh
      </button>
      <ul>
        {models.map((m) => (
          <li key={m.model_id}>
            {m.model_id} ({m.version}, {m.status}){" "}
            <button type="button" onClick={() => act("promote", m.model_id)}>
              Promote
            </button>{" "}
            <button type="button" onClick={() => act("rollback", m.model_id)}>
              Rollback
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
