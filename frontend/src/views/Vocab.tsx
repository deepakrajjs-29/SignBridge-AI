import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function Vocab() {
  const [classes, setClasses] = useState<{ class_id: string; label: string; sign_type: string }[]>([]);
  const [q, setQ] = useState("");
  const [text, setText] = useState("");
  const [out, setOut] = useState<
    { word: string; class_id: string; label: string; supported: boolean }[] | null
  >(null);
  const [unsupported, setUnsupported] = useState<string[]>([]);
  const [note, setNote] = useState("");

  useEffect(() => {
    api.classes().then((r) => setClasses(r.classes)).catch((e: Error) => setNote(e.message));
  }, []);

  const shown = classes.filter((c) => c.label.toLowerCase().includes(q.toLowerCase()));

  async function convert() {
    setNote("");
    try {
      const r = await api.textToSign(text);
      setOut(r.items);
      setUnsupported(r.unsupported_words);
    } catch (e) {
      setNote(e instanceof Error ? e.message : "Conversion failed.");
    }
  }

  return (
    <section aria-label="vocabulary">
      <h2>Supported signs ({classes.length})</h2>
      <label>
        Search <input value={q} onChange={(e) => setQ(e.target.value)} aria-label="vocab-search" />
      </label>
      <ul>
        {shown.slice(0, 50).map((c) => (
          <li key={c.class_id}>
            {c.label} ({c.class_id}, {c.sign_type})
          </li>
        ))}
      </ul>
      <h3>Text-to-sign</h3>
      <label>
        Text <input value={text} onChange={(e) => setText(e.target.value)} aria-label="t2s-input" />
      </label>{" "}
      <button type="button" onClick={convert}>
        Convert
      </button>
      {note && <p role="alert">{note}</p>}
      {out && (
        <ul>
          {out.map((o) => (
            <li key={o.word}>
              {o.word} → {o.label} ({o.supported ? "visual available" : "no visual yet"})
            </li>
          ))}
        </ul>
      )}
      {unsupported.length > 0 && <p>Unsupported words: {unsupported.join(", ")}</p>}
    </section>
  );
}
