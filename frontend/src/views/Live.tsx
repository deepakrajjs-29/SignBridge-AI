import { useEffect, useRef, useState } from "react";
import { api, type Prediction, type RecState } from "../api/client";
import { connectStream, type StreamCallbacks } from "../api/stream";
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
  // REST sends lowercase "recognized"; WS stream sends "Recognized".
  if (apiStatus.toLowerCase() === "recognized") return "Recognized";
  return "Uncertain";
}

export const STREAM_TIMEOUT_MS = 15000;

export function apiBase(): string {
  return import.meta.env.VITE_API_BASE ?? "http://localhost:8000";
}

export interface RecognizeDeps {
  base?: string;
  connect?: typeof connectStream;
  predict?: (
    frames: number[][],
    sessionId: string
  ) => Promise<{ prediction: Prediction; status: string }>;
  onState?: (s: RecState) => void;
  onNote?: (m: string) => void;
  onPrediction?: (p: Prediction, status: string) => void;
  onHandle?: (h: { stop: () => void } | null) => void;
  timeoutMs?: number;
}

/**
 * Stream-first recognition with one-shot REST fallback (Task 9).
 * Tries `connectStream` + `sendFrame` per row; a WS prediction resolves
 * `{ path: "stream" }`. Any stream error / exception / timeout runs the
 * unchanged REST `predict` block and resolves `{ path: "rest" }`.
 * REST failures propagate to the caller (mapped to Error/Tracking-Lost there).
 */
export async function recognizeFrames(
  frames: number[][],
  sessionId: string,
  deps: RecognizeDeps = {}
): Promise<{ path: "stream" | "rest"; status: string }> {
  const {
    base = apiBase(),
    connect = connectStream,
    predict = (f, sid) => api.predict(f, sid),
    onState = () => {},
    onNote = () => {},
    onPrediction = () => {},
    onHandle = () => {},
    timeoutMs = STREAM_TIMEOUT_MS,
  } = deps;

  let streamStatus = "";
  const streamed = await new Promise<boolean>((resolve) => {
    let done = false;
    let handle: ReturnType<typeof connectStream> | null = null;
    const finish = (ok: boolean) => {
      if (done) return;
      done = true;
      clearTimeout(timer);
      try {
        handle?.stop();
      } catch {
        /* socket already closed */
      }
      onHandle(null);
      resolve(ok);
    };
    const timer = setTimeout(() => {
      onNote("Live stream timed out — used REST fallback.");
      finish(false);
    }, timeoutMs);
    try {
      onState("Tracking");
      const cb: StreamCallbacks = {
        onStatus: (st) => {
          if (st === "Tracking") onState("Tracking");
          else if (st === "Tracking-Lost") {
            onState("Tracking-Lost");
            onNote("Landmark stream lost — reframe hands and retry.");
          }
        },
        onPrediction: (p, st) => {
          streamStatus = st;
          onPrediction(p, st);
          finish(true);
        },
        onError: (msg) => {
          onState("Tracking-Lost");
          onNote(`${msg} Used REST fallback.`);
          finish(false);
        },
      };
      handle = connect(base, sessionId, cb);
      onHandle(handle);
      for (const f of frames) handle.sendFrame(f);
    } catch {
      finish(false);
    }
  });

  if (streamed) return { path: "stream", status: streamStatus };
  const r = await predict(frames, sessionId);
  onPrediction(r.prediction, r.status);
  return { path: "rest", status: r.status };
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
  const wsRef = useRef<{ stop: () => void } | null>(null);

  function provider(): MediaPipeProvider {
    if (!providerRef.current) providerRef.current = new MediaPipeProvider();
    return providerRef.current;
  }

  useEffect(
    () => () => {
      streamRef.current?.getTracks().forEach((t) => t.stop());
      try {
        wsRef.current?.stop();
      } catch {
        /* socket already closed */
      }
      wsRef.current = null;
    },
    []
  );

  function applyPrediction(p: Prediction, status: string) {
    setResult(p);
    setConf(p.confidence);
    onResult(p);
    setState(toState(status, true));
    if (status.toLowerCase() !== "recognized")
      setNote(`Low confidence (${p.confidence}) — shown as Uncertain, not definitive.`);
  }

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
      let sid = session;
      if (!sid) {
        const s = await api.openSession();
        sid = s.session_id;
        setSession(sid);
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
      setBusy("Streaming frames — hold the sign steady…");
      await recognizeFrames(frames, sid, {
        onState: setState,
        onNote: setNote,
        onPrediction: applyPrediction,
        onHandle: (h) => {
          wsRef.current = h;
        },
      });
      wsRef.current = null;
      setBusy("");
    } catch (e) {
      setBusy("");
      wsRef.current = null;
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
