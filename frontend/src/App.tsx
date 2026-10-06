import { useState } from "react";
import type { Prediction } from "./api/client";
import Admin from "./views/Admin";
import History from "./views/History";
import Live from "./views/Live";
import Settings from "./views/Settings";
import Vocab from "./views/Vocab";

type Tab = "live" | "history" | "vocab" | "admin" | "settings";

export default function App() {
  const [tab, setTab] = useState<Tab>("live");
  const [last, setLast] = useState<Prediction | null>(null);
  return (
    <main style={{ fontFamily: "system-ui", padding: 24, maxWidth: 860 }}>
      <h1>SignBridge AI</h1>
      <nav aria-label="primary" style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        {(["live", "history", "vocab", "admin", "settings"] as Tab[]).map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            aria-current={tab === t ? "page" : undefined}
            style={{ fontWeight: tab === t ? "bold" : "normal" }}
          >
            {t[0].toUpperCase() + t.slice(1)}
          </button>
        ))}
      </nav>
      {tab === "live" && <Live onResult={setLast} />}
      {tab === "history" && <History />}
      {tab === "vocab" && <Vocab />}
      {tab === "admin" && <Admin />}
      {tab === "settings" && <Settings />}
      {last && tab === "live" && (
        <p aria-live="polite">
          Last result: {last.label} ({last.confidence})
        </p>
      )}
      <footer style={{ marginTop: 24, fontSize: 12 }}>
        <p>Camera-active indicator shown in Live tab. No video stored by default.</p>
      </footer>
    </main>
  );
}
