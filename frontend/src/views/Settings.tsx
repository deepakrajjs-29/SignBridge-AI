import { useState } from "react";

export default function Settings() {
  const [tok, setTok] = useState(localStorage.getItem("sb_token") || "change-me");
  const [saved, setSaved] = useState(false);
  return (
    <section aria-label="settings-help">
      <h2>Settings</h2>
      <label>
        API token (Bearer for predict/session/admin; open endpoints need none){" "}
        <input
          value={tok}
          onChange={(e) => setTok(e.target.value)}
          aria-label="api-token"
          autoComplete="off"
        />
      </label>{" "}
      <button
        type="button"
        onClick={() => {
          localStorage.setItem("sb_token", tok);
          setSaved(true);
        }}
      >
        Save
      </button>
      {saved && <p role="status">Token saved locally.</p>}
      <h3>Help</h3>
      <ul>
        <li>Allow camera → Start recognition → review result → Speak/repeat → Clear.</li>
        <li>Uncertain means low confidence — never treated as definitive.</li>
        <li>History entries can be deleted anytime; raw video is never stored.</li>
        <li>Verify high-stakes outputs with a human.</li>
      </ul>
    </section>
  );
}
