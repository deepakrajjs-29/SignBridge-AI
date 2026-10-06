import { useEffect, useRef, useState } from "react";
import { api, type Prediction, type RecState } from "../api/client";
import { MediaPipeProvider, isFiniteFrame } from "../landmarks";

const STATES: RecState[] = [
  "Ready",
  "Tracking",
  "Recognized",
  "Uncertain",
  "No-Sign",
  "Tracking-Lost",
  "Error",
];

function toState(apiStatus: string, ok: boolean): RecState {
  if (!ok) return "Error";
  if (apiStatus === "recognized") return "Recognized";
  return "Uncertain";
}

export const CAMERA_TIMEOUT_MS = 10000;
export const CAMERA_ERROR_NOTE =
  "Camera denied or unavailable. Check browser permission and retry.";

export function requestCameraStream(timeoutMs = CAMERA_TIMEOUT_MS): Promise<MediaStream> {
  const timeout = new Promise<never>((_, reject) => {
    setTimeout(() => {
      reject(new Error("Camera request timed out after 10 s. Check browser permission and retry."));
    }, timeoutMs);
  });
  return Promise.race([
    navigator.mediaDevices.getUserMedia({ video: { width: 640 } }),
    timeout,
  ]);
}

export default function Live({ onResult }: { onResult: (p: Prediction) => void }) {
  const [state, setState] = useState<RecState>("Ready");
  const [session, setSession] = useState("");
  const [result, setResult] = useState<Prediction | null>(null);
  const [conf, setConf] = useState(0);
  const [note, setNote] = useState("");
  const [camOn, setCamOn] = useState(false);
  const [busy, setBusy] = useState("");
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const providerRef = useRef<MediaPipeProvider | null>(null);

  function provider(): MediaPipeProvider {
    if (!providerRef.current) providerRef.current = new MediaPipeProvider();
    return providerRef.current;
  }

  useEffect(
    () => () => {
      streamRef.current?.getTracks().forEach((t) => t.stop());
    },
    []
  );

  async function enableCamera(timeoutMs = CAMERA_TIMEOUT_MS) {
    setNote("");
    setBusy("Requesting camera…");
    try {
      const s = await requestCameraStream(timeoutMs);
      streamRef.current = s;
      if (videoRef.current) {
        videoRef.current.srcObject = s;
        await videoRef.current.play().catch(() => {});
      }
      setCamOn(true);
      setState("Tracking");
    } catch {
      setState("Error");
      setNote(CAMERA_ERROR_NOTE);
    } finally {
      setBusy("");
    }
  }

  function stopCamera() {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    setCamOn(false);
    setState("Ready");
  }

  async function start() {
    setNote("");
    if (!videoRef.current) {
      setState("Error");
      setNote("Camera view missing — re-enable camera and retry.");
      return;
    }
    setBusy("Loading hand-tracking model (first run downloads ~10 MB)…");
    try {
      if (!session) {
        const s = await api.openSession();
        setSession(s.session_id);
      }
      setState("Tracking");
      setBusy("Capturing 45 frames — hold the sign steady…");
      const frames = await provider().capture(videoRef.current, 45);
      setBusy("");
      if (!isFiniteFrame(frames)) {
        setState("Tracking-Lost");
        setNote("Landmark stream invalid — reframe hands and retry.");
        return;
      }
      const r = await api.predict(frames, session);
      setResult(r.prediction);
      setConf(r.prediction.confidence);
      onResult(r.prediction);
      setState(toState(r.status, true));
      if (r.status !== "recognized")
        setNote(`Low confidence (${r.prediction.confidence}) — shown as Uncertain, not definitive.`);
    } catch (e) {
      setBusy("");
      const msg = e instanceof Error ? e.message : "Recognition failed.";
      if (/No hands detected/.test(msg)) {
        setState("Tracking-Lost");
      } else {
        setState("Error");
      }
      setNote(msg + " All video processing stays on this device.");
    }
  }

  async function speak() {
    if (!result) return;
    try {
      await api.tts(result.label);
    } catch (e) {
      setNote(
        e instanceof Error && (e as { code?: string }).code === "TTS_NOT_CONFIGURED"
          ? "Speech engine not configured yet (P5 wiring) — text result kept."
          : e instanceof Error
            ? e.message
            : "Speech failed."
      );
    }
  }

  return (
    <section aria-label="live-recognition">
      <h2>Live recognition</h2>
      <p role="status" aria-live="polite">
        State: <strong>{state}</strong>
        {result && state === "Recognized" && (
          <span style={{ fontSize: 40, display: "block" }}>
            {result.label} ({conf.toFixed(2)})
          </span>
        )}
      </p>
      <video ref={videoRef} width={320} muted playsInline aria-label="camera-preview" />
      <div style={{ display: "flex", gap: 8, marginTop: 8, flexWrap: "wrap" }}>
        {!camOn ? (
          <button type="button" onClick={() => enableCamera()}>
            Enable camera
          </button>
        ) : (
          <button type="button" onClick={stopCamera}>
            Stop camera
          </button>
        )}
        <button type="button" onClick={start} disabled={!camOn}>
          Start recognition
        </button>
        <button type="button" onClick={speak} disabled={!result}>
          Speak
        </button>
        <button
          type="button"
          onClick={() => {
            setResult(null);
            setState(camOn ? "Tracking" : "Ready");
            setNote("");
          }}
        >
          Clear
        </button>
      </div>
      {note && <p role="alert">{note}</p>}
      {busy && (
        <p role="status" aria-live="polite">
          {busy}
        </p>
      )}
      <details>
        <summary>All states (for testers)</summary>
        <ul>
          {STATES.map((s) => (
            <li key={s}>{s}</li>
          ))}
        </ul>
      </details>
    </section>
  );
}
