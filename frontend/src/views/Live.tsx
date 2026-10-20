import { useEffect, useRef, useState } from "react";
import { api, type AlternativeCandidate, type Prediction, type RecState } from "../api/client";
import { connectStream, type StreamCallbacks } from "../api/stream";
import { MediaPipeProvider, dispose as disposeLandmarker, isFiniteFrame } from "../landmarks";
import { interpretSignSequence, type SentenceMood } from "../api/gemini";
import { saveSentenceRecord } from "../api/sentenceHistory";
import {
  CameraIcon,
  VolumeUpIcon,
  RefreshIcon,
  CheckCircleIcon,
  AlertCircleIcon,
  SparklesIcon,
} from "../components/Icons";

export interface MoodProfile {
  id: SentenceMood;
  label: string;
  emoji: string;
  pitch: number;
  rate: number;
  volume: number;
  activeClass: string;
  badgeClass: string;
  description: string;
}

export const MOODS: MoodProfile[] = [
  {
    id: "normal",
    label: "Normal",
    emoji: "😐",
    pitch: 1.0,
    rate: 1.0,
    volume: 1.0,
    activeClass: "bg-slate-700 text-white ring-2 ring-slate-400 shadow-md",
    badgeClass: "bg-slate-800 text-slate-300 border border-slate-700",
    description: "Neutral & natural conversational tone",
  },
  {
    id: "happy",
    label: "Happy",
    emoji: "😊",
    pitch: 1.35,
    rate: 1.15,
    volume: 1.0,
    activeClass: "bg-emerald-600 text-white ring-2 ring-emerald-400 shadow-emerald-500/30 shadow-lg",
    badgeClass: "bg-emerald-950/80 text-emerald-300 border border-emerald-800",
    description: "Energetic, bright & upbeat tone",
  },
  {
    id: "sad",
    label: "Sad",
    emoji: "😔",
    pitch: 0.72,
    rate: 0.82,
    volume: 0.85,
    activeClass: "bg-blue-600 text-white ring-2 ring-blue-400 shadow-blue-500/30 shadow-lg",
    badgeClass: "bg-blue-950/80 text-blue-300 border border-blue-800",
    description: "Soft, slower & somber tone",
  },
  {
    id: "angry",
    label: "Angry",
    emoji: "😠",
    pitch: 0.85,
    rate: 1.25,
    volume: 1.0,
    activeClass: "bg-rose-600 text-white ring-2 ring-rose-400 shadow-rose-500/30 shadow-lg",
    badgeClass: "bg-rose-950/80 text-rose-300 border border-rose-800",
    description: "Firm, urgent & emphatic tone",
  },
];

const STATES: RecState[] = [
  "Ready",
  "Tracking",
  "Recognized",
  "Provisional",
  "Uncertain",
  "No-Sign",
  "Tracking-Lost",
  "Error",
];

export function toState(apiStatus: string, ok: boolean): RecState {
  if (!ok) return "Error";
  // REST sends lowercase "recognized"/"provisional"/"no-sign"; WS stream sends
  // the capitalized "Recognized"/"Provisional"/"No-Sign" variants.
  const s = apiStatus.toLowerCase();
  if (s === "recognized") return "Recognized";
  if (s === "provisional") return "Provisional";
  if (s === "no-sign") return "No-Sign";
  return "Uncertain";
}

/** Note shown under a non-recognized prediction (null when nothing to say:
 * recognized predictions speak for themselves). Provisional is deliberately
 * distinct from Uncertain — both are display-only (never committed), but
 * provisional is a plausible reading worth holding the sign for. */
export function confidenceNote(status: string, confidence: number): string | null {
  const s = status.toLowerCase();
  if (s === "recognized") return null;
  if (s === "provisional") {
    return `Provisional (${(confidence * 100).toFixed(1)}%) — plausible, needs more evidence. Not added to your sequence.`;
  }
  return `Low confidence (${(confidence * 100).toFixed(1)}%) — shown as Uncertain, not definitive.`;
}

export const STREAM_TIMEOUT_MS = 15000;

/** Evidence-based default confidence gate: on the SPLIT-4.0 test set a 0.60
 * gate accepts 78% of windows at 91% precision (0.70 accepted only 69%). */
export const DEFAULT_THRESHOLD_PERCENT = 60;

/** Non-accepted windows needed before the commit gate re-arms (a true
 * release); one soft/provisional window mid-hold does not re-arm. */
export const RELEASE_WINDOWS = 2;

/** Single-sign readiness countdown: 3 ticks x 400 ms = 1200 ms before capture. */
export const COUNTDOWN_TICKS = 3;
export const COUNTDOWN_MS = 400;

function countdownSleep(ms: number): Promise<void> {
  return new Promise((r) => setTimeout(r, ms));
}

/** Counts COUNTDOWN_TICKS..1 (one onTick per step), then onTick(0) to clear.
 * Resolves early with onTick(0) when `cancelled()` becomes true. */
export async function runCountdown(
  onTick: (remaining: number) => void,
  cancelled?: () => boolean,
  sleep: (ms: number) => Promise<void> = countdownSleep
): Promise<void> {
  for (let n = COUNTDOWN_TICKS; n >= 1; n--) {
    if (cancelled?.()) {
      onTick(0);
      return;
    }
    onTick(n);
    await sleep(COUNTDOWN_MS);
  }
  onTick(0);
}

/** Runs the readiness countdown, then the attempt — capture never starts
 * before the countdown has completed. */
export async function runSingleAttempt(
  countdown: () => Promise<void>,
  attempt: () => Promise<void>
): Promise<void> {
  await countdown();
  await attempt();
}

export interface CommitInput {
  accepted: boolean;
  label: string;
  lastLabel: string;
  armed: boolean;
  freshAttempt: boolean;
  /** consecutive non-accepted windows since the last accepted prediction */
  streak?: number;
  /** hard release evidence (e.g. No-Sign) re-arms in a single window */
  hardRelease?: boolean;
}

export interface CommitDecision {
  commit: boolean;
  armed: boolean;
  lastLabel: string;
}

/**
 * Release-based commit gate: one gesture performance -> exactly one commit.
 * Re-observing the same label while it is still held is suppressed until a
 * release window (two consecutive soft windows, a hard release such as
 * no-sign, a different sign, or a deliberate single-sign attempt) re-arms it.
 */
export function resolveCommit(input: CommitInput): CommitDecision {
  const label = input.label.trim().toUpperCase();
  if (!input.accepted) {
    const streak = input.streak ?? 0;
    const hardRelease = input.hardRelease ?? false;
    return {
      commit: false,
      armed: input.armed || hardRelease || streak >= RELEASE_WINDOWS,
      lastLabel: input.lastLabel,
    };
  }
  if (label === input.lastLabel && !input.armed && !input.freshAttempt) {
    return { commit: false, armed: false, lastLabel: input.lastLabel };
  }
  return { commit: true, armed: false, lastLabel: label };
}

/**
 * Explicit manual confidence gate (percent). null when the user has never
 * touched the Settings slider — acceptance is then decided purely by the
 * backend-calibrated thresholds (no implicit frontend floor).
 */
export function readThresholdGate(): number | null {
  try {
    const stored = localStorage.getItem("sb_threshold");
    if (stored === null) return null;
    const v = parseInt(stored, 10);
    return Number.isNaN(v) ? null : v;
  } catch {
    return null;
  }
}

export function apiBase(): string {
  if (typeof window !== "undefined") {
    const envBase = import.meta.env.VITE_API_BASE;
    return envBase && envBase.trim() !== "" ? envBase.trim() : "";
  }
  return import.meta.env.VITE_API_BASE || "http://localhost:8000";
}

export interface RecognizeDeps {
  base?: string;
  connect?: typeof connectStream;
  predict?: (
    frames: number[][],
    sessionId: string
  ) => Promise<{
    prediction: Prediction;
    alternatives?: AlternativeCandidate[];
    status: string;
    processing_time_ms?: number;
  }>;
  onState?: (s: RecState) => void;
  onNote?: (m: string) => void;
  onPrediction?: (
    p: Prediction,
    status: string,
    latencyMs?: number,
    alternatives?: AlternativeCandidate[]
  ) => void;
  onHandle?: (h: { stop: () => void } | null) => void;
  timeoutMs?: number;
}

/**
 * Stream-first recognition with one-shot REST fallback (Task 9).
 * Tries `connectStream` + ONE `sendWindow(frames)` with the full-T rows; a WS
 * prediction resolves `{ path: "stream" }`. Any stream error / exception /
 * timeout runs the unchanged REST `predict` block and resolves
 * `{ path: "rest" }`.
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
    let openTimer: ReturnType<typeof setTimeout> | undefined;
    const run = async () => {
      const finish = (ok: boolean) => {
        if (done) return;
        done = true;
        clearTimeout(timer);
        if (openTimer !== undefined) clearTimeout(openTimer);
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
        onPrediction: (p, st, alts) => {
          streamStatus = st;
          onPrediction(p, st, undefined, alts);
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
      // Wait for the WS handshake before sending frames. Sending on a
      // CONNECTING socket throws and used to doom every stream attempt to a
      // silent REST fallback. Mocks without `ready` proceed immediately.
      try {
        await Promise.race([
          handle.ready ?? Promise.resolve(),
          new Promise<never>((_, reject) => {
            openTimer = setTimeout(() => reject(new Error("open-timeout")), timeoutMs);
          }),
        ]);
      } catch {
        if (!done) onNote("Live stream timed out — used REST fallback.");
        finish(false);
        return;
      }
      handle.sendWindow(frames);
    } catch {
      finish(false);
    }
    };
    void run();
  });

  if (streamed) return { path: "stream", status: streamStatus };
  const r = await predict(frames, sessionId);
  onPrediction(r.prediction, r.status, r.processing_time_ms, r.alternatives);
  return { path: "rest", status: r.status };
}

/** Backend rejects stale session ids after restart/reset (in-memory SESSIONS). */
export function isUnknownSessionError(e: unknown): boolean {
  if (!(e instanceof Error)) return false;
  const code = (e as { code?: string }).code;
  if (code === "UNKNOWN_SESSION" || code === "HTTP_404") return true;
  return /unknown session/i.test(e.message);
}

/**
 * Append a user-confirmed word unless it is a no-sign or an immediate
 * duplicate of the last sentence token (repeated frames / double-click).
 */
export function appendConfirmedWord(seq: string[], label: string): string[] {
  const upper = (label || "").trim().toUpperCase();
  if (!upper || upper === "NO SIGN DETECTED") return seq;
  if (seq.length > 0 && seq[seq.length - 1] === upper) return seq;
  return [...seq, upper];
}

/** Cap session re-opens so recovery never becomes an infinite loop. */
export const MAX_SESSION_RECOVERIES = 2;

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

interface LiveProps {
  onResult?: (p: Prediction) => void;
  activeSessionId?: string;
}

export default function Live({ onResult = () => {}, activeSessionId = "" }: LiveProps) {
  const [state, setState] = useState<RecState>("Ready");
  const [session, setSession] = useState(activeSessionId);
  const [result, setResult] = useState<Prediction | null>(null);
  const [conf, setConf] = useState(0);
  const [latency, setLatency] = useState<number | null>(null);
  const [note, setNote] = useState("");
  const [camOn, setCamOn] = useState(false);
  const [busy, setBusy] = useState("");
  const [countdown, setCountdown] = useState<number | null>(null);
  const [feedbackSent, setFeedbackSent] = useState<"up" | "down" | null>(null);

  // Continuous Sequence & Gemini State
  const [recognizedSequence, setRecognizedSequence] = useState<string[]>([]);
  const [generatedSentence, setGeneratedSentence] = useState<string>("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [generationError, setGenerationError] = useState("");
  const [isContinuousRunning, setIsContinuousRunning] = useState(false);
  const [selectedMood, setSelectedMood] = useState<SentenceMood>("normal");
  /** Real model top-k from the last prediction (empty when unavailable). */
  const [candidates, setCandidates] = useState<AlternativeCandidate[]>([]);
  /** True while the uncertainty panel is open (user can confirm/dismiss). */
  const [showConfirmPanel, setShowConfirmPanel] = useState(false);
  /** Last word appended via explicit user confirm (not auto model commit). */
  const [lastUserConfirmed, setLastUserConfirmed] = useState(false);

  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const providerRef = useRef<MediaPipeProvider | null>(null);
  const wsRef = useRef<{ stop: () => void } | null>(null);

  // Stabilization & race-condition guards
  const lastSignLabelRef = useRef<string>("");
  const armedRef = useRef<boolean>(true); // release-based re-arm gate for same-sign repeats
  const freshAttemptRef = useRef<boolean>(false); // single-sign click = deliberate attempt
const releaseStreakRef = useRef<number>(0); // consecutive non-accepted windows
  const lastSpokenRef = useRef<string>("");
  const continuousRunningRef = useRef<boolean>(false);
  const abortControllerRef = useRef<AbortController | null>(null);
  const sequenceIdRef = useRef<number>(0);
  const autoGenerateTimerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (activeSessionId) setSession(activeSessionId);
  }, [activeSessionId]);

  function provider(): MediaPipeProvider {
    if (!providerRef.current) providerRef.current = new MediaPipeProvider();
    return providerRef.current;
  }

  useEffect(
    () => () => {
      continuousRunningRef.current = false;
      streamRef.current?.getTracks().forEach((t) => t.stop());
      try {
        wsRef.current?.stop();
      } catch {
        /* socket already closed */
      }
      wsRef.current = null;
      try {
        providerRef.current?.dispose();
      } catch {
        /* provider already disposed */
      }
      disposeLandmarker();
      if (autoGenerateTimerRef.current) {
        clearTimeout(autoGenerateTimerRef.current);
      }
      if (typeof window !== "undefined" && "speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }
      abortControllerRef.current?.abort();
    },
    []
  );

  function speakSentence(text: string, mood: SentenceMood = selectedMood, interrupt = true) {
    if (typeof window === "undefined" || !("speechSynthesis" in window) || !text.trim()) {
      return;
    }
    try {
      // Sign words queue (no interrupt) so a generated sentence can never chop
      // a word mid-flight; sentences/replay interrupt to supersede the queue.
      if (interrupt) window.speechSynthesis.cancel();
      lastSpokenRef.current = text.trim();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = "en-IN";

      const profile = MOODS.find((m) => m.id === mood) || MOODS[0];
      utterance.pitch = profile.pitch;
      utterance.rate = profile.rate;
      utterance.volume = profile.volume;

      setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);
      window.speechSynthesis.speak(utterance);
    } catch {
      setIsSpeaking(false);
    }
  }

  /** True when the generated sentence just re-says the last spoken word
   * (single-sign echo like "HELLO" -> "Hello." must not speak twice). */
  function isEchoOfLastSpoken(text: string): boolean {
    const norm = (s: string) => s.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
    const last = lastSpokenRef.current;
    return Boolean(last) && norm(text) === norm(last);
  }

  function applyPrediction(p: Prediction, status: string, latencyMs?: number, alts?: AlternativeCandidate[]) {
    setResult(p);
    setConf(p.confidence);
    if (latencyMs) setLatency(latencyMs);
    onResult(p);
    setFeedbackSent(null);
    const nextAlts = alts && alts.length > 0 ? alts : [];
    setCandidates(nextAlts);
    setLastUserConfirmed(false);

    // Explicit user gate only: the backend-calibrated thresholds decide
    // acceptance unless the user has explicitly set a manual gate via the
    // Settings slider (sb_threshold). Never fall back to an implicit floor.
    const gate = readThresholdGate();
    const meetsThreshold = gate === null || p.confidence >= gate / 100;

    // A prediction is only accepted if backend recognized it AND confidence meets the (optional) user gate:
    const isAccepted = status.toLowerCase() === "recognized" && meetsThreshold;
    const labelUpper = (p.label || "").trim().toUpperCase();
    const displayUncertain =
      !isAccepted &&
      (status.toLowerCase() === "uncertain" ||
        status.toLowerCase() === "provisional" ||
        (gate !== null && status.toLowerCase() === "recognized" && !meetsThreshold));

    // Uncertainty panel: only for non-accepted readings that still carry
    // real model candidates. Never invents labels. ISL_000 has none.
    setShowConfirmPanel(
      displayUncertain &&
        nextAlts.length > 0 &&
        p.class_id !== "ISL_000" &&
        labelUpper !== "NO SIGN DETECTED"
    );

    if (gate !== null && !meetsThreshold && status.toLowerCase() === "recognized") {
      setState("Uncertain");
      setNote(
        `Confidence (${(p.confidence * 100).toFixed(1)}%) is below your ${gate}% gate — flagged as Uncertain.`
      );
    } else {
      setState(toState(status, true));
      const noteText = confidenceNote(status, p.confidence);
      if (noteText) setNote(noteText);
    }

    const accepted =
      isAccepted &&
      Boolean(labelUpper) &&
      labelUpper !== "NO SIGN DETECTED" &&
      p.class_id !== "ISL_000";

    releaseStreakRef.current = accepted ? 0 : releaseStreakRef.current + 1;

    const decision = resolveCommit({
      accepted,
      label: labelUpper,
      lastLabel: lastSignLabelRef.current,
      armed: armedRef.current,
      freshAttempt: freshAttemptRef.current,
      streak: releaseStreakRef.current,
      hardRelease: status.toLowerCase() === "no-sign",
    });
    freshAttemptRef.current = false;
    armedRef.current = decision.armed;

    if (decision.commit) {
      lastSignLabelRef.current = decision.lastLabel;

      // Auto Speak Confirmed Prediction:
      // Automatically speak confirmed signs out loud through speaker!
      const autoSpeakEnabled = localStorage.getItem("sb_autospeak") !== "false";
      if (autoSpeakEnabled) {
        // Queue (no interrupt): never cancel an in-flight generated sentence.
        speakSentence(labelUpper, selectedMood, false);
      }

      setRecognizedSequence((prev) => {
        const nextSeq = [...prev, labelUpper];
        // Auto-summarize & speak: 1.8s silence window triggers hands-free translation!
        if (autoGenerateTimerRef.current) {
          clearTimeout(autoGenerateTimerRef.current);
        }
        autoGenerateTimerRef.current = setTimeout(() => {
          handleGenerateSentence(nextSeq, selectedMood);
        }, 1800);
        return nextSeq;
      });
      setGenerationError("");
    }
  }

  /**
   * User picked a genuine model candidate (or the primary) from the
   * uncertainty panel. Recorded as USER-CONFIRMED — not an automatic
   * model success. Duplicate last-label inserts are suppressed.
   */
  function confirmUserSelection(cand: AlternativeCandidate) {
    const labelUpper = cand.label.trim().toUpperCase();
    if (!labelUpper || labelUpper === "NO SIGN DETECTED" || cand.class_id === "ISL_000") return;
    setShowConfirmPanel(false);
    const nextSeq = appendConfirmedWord(recognizedSequence, labelUpper);
    if (nextSeq.length === recognizedSequence.length) {
      setNote(`Already in sentence: ${labelUpper} — duplicate skipped.`);
      return;
    }
    lastSignLabelRef.current = labelUpper;
    armedRef.current = false;
    setLastUserConfirmed(true);
    setNote(`User confirmed: ${labelUpper} (not an automatic model commit).`);
    setRecognizedSequence(nextSeq);
    if (autoGenerateTimerRef.current) clearTimeout(autoGenerateTimerRef.current);
    autoGenerateTimerRef.current = setTimeout(() => {
      handleGenerateSentence(nextSeq, selectedMood);
    }, 1800);
    setGenerationError("");
  }

  function dismissCandidates(reason: "retry" | "dismiss") {
    setShowConfirmPanel(false);
    setCandidates([]);
    if (reason === "retry") {
      setNote("Cleared uncertain result — perform the sign again.");
      armedRef.current = true;
    } else {
      setNote("Uncertain result dismissed — not added to your sentence.");
    }
  }

  async function enableCamera(timeoutMs = CAMERA_TIMEOUT_MS) {
    setNote("");
    setBusy("Requesting camera access…");
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
    continuousRunningRef.current = false;
    setIsContinuousRunning(false);
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    setCamOn(false);
    setState("Ready");
    setBusy("");
  }

  // Core capture and inference of one 45-frame window
  async function captureAndRecognizeOnce(sid: string): Promise<boolean> {
    if (!videoRef.current) return false;
    setBusy("Capturing sign (~3.5 s) — perform it now…");
    const frames = await provider().capture(videoRef.current);
    setBusy("");

    if (!isFiniteFrame(frames)) {
      setState("Tracking-Lost");
      setNote("Landmark stream invalid — reframe hands and retry.");
      return false;
    }

    setBusy("Processing sequence with AI model…");
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
    return true;
  }

  // Re-open a backend session when the previous id is unknown (restart/reset).
  async function openFreshSession(): Promise<string> {
    const s = await api.openSession();
    setSession(s.session_id);
    return s.session_id;
  }

  async function resolveSessionSid(current: string): Promise<string> {
    return current || openFreshSession();
  }

  // Single Sign Recognition
  async function startSingle() {
    setNote("");
    if (!videoRef.current) {
      setState("Error");
      setNote("Camera view missing — re-enable camera and retry.");
      return;
    }
    setBusy("Initializing on-device hand-tracking model…");
    try {
      let sid = await resolveSessionSid(session);
      let recovered = 0;
      setState("Tracking");
      freshAttemptRef.current = true;
      releaseStreakRef.current = 0;
      const readiness = () =>
        runCountdown((r) => setCountdown(r || null), () => !videoRef.current);
      await runSingleAttempt(readiness, async () => {
        try {
          await captureAndRecognizeOnce(sid);
        } catch (e) {
          if (isUnknownSessionError(e) && recovered < MAX_SESSION_RECOVERIES) {
            recovered += 1;
            sid = await openFreshSession();
            setNote("Session expired — recovered. Signing again…");
            await readiness();
            await captureAndRecognizeOnce(sid);
          } else {
            throw e;
          }
        }
      });
    } catch (e) {
      setBusy("");
      wsRef.current = null;
      // Failed attempt = release evidence; drop any unconsumed fresh flag.
      armedRef.current = true;
      freshAttemptRef.current = false;
      const msg = e instanceof Error ? e.message : "Recognition failed.";
      const code = e instanceof Error ? (e as { code?: string }).code : undefined;
      if (/No hands detected/.test(msg)) {
        setState("Tracking-Lost");
      } else {
        setState("Error");
      }
      setNote(
        code === "TIMEOUT"
          ? `${msg} Retry — the request timed out. All video processing stays on this device.`
          : isUnknownSessionError(e)
            ? `${msg} Open a new session and retry.`
            : msg + " All video processing stays on this device."
      );
    }
  }

  // Continuous Sign Recognition Loop
  async function startContinuous() {
    setNote("");
    if (!videoRef.current) {
      setState("Error");
      setNote("Camera view missing — re-enable camera and retry.");
      return;
    }

    let sid: string;
    try {
      sid = await resolveSessionSid(session);
    } catch {
      setState("Error");
      setNote("Could not initialize session with backend.");
      return;
    }

    continuousRunningRef.current = true;
    setIsContinuousRunning(true);
    setState("Tracking");
    freshAttemptRef.current = false;
    releaseStreakRef.current = 0;

    let consecutiveFailures = 0;
    let sessionRecoveries = 0;
    try {
      while (continuousRunningRef.current) {
        let ok = false;
        try {
          ok = await captureAndRecognizeOnce(sid);
        } catch (e) {
          // Stale session (backend restart/reset): re-open once and retry
          // without counting toward the 3-failure stop limit.
          if (isUnknownSessionError(e) && sessionRecoveries < MAX_SESSION_RECOVERIES) {
            sessionRecoveries += 1;
            setBusy("");
            wsRef.current = null;
            try {
              sid = await openFreshSession();
              setNote("Session expired — recovered. Continue signing…");
              setState("Tracking");
              continue;
            } catch {
              // fall through to generic failure handling below
            }
          }
          // One bad window (hands lost, backend hiccup) must not end the
          // session: surface it, treat it as a release, retry up to 3x.
          consecutiveFailures++;
          setBusy("");
          wsRef.current = null;
          armedRef.current = true;
          const msg = e instanceof Error ? e.message : "Recognition failed.";
          setNote(msg + " All video processing stays on this device.");
          setState(/No hands detected/.test(msg) ? "Tracking-Lost" : "Error");
          if (consecutiveFailures >= 3) {
            setNote(`${msg} Continuous recognition stopped after repeated failures.`);
            break;
          }
          await new Promise((resolve) => setTimeout(resolve, 600));
          continue;
        }
        if (!ok || !continuousRunningRef.current) break;
        consecutiveFailures = 0;

        // Brief inter-sign buffer window to allow physical hand transition
        setBusy("Sign logged — release your hands, then perform the next sign…");
        await new Promise((resolve) => setTimeout(resolve, 600));
        if (!continuousRunningRef.current) break;
      }
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Continuous recognition interrupted.";
      setNote(
        isUnknownSessionError(e)
          ? `${msg} Continuous recognition stopped — open a new session and retry.`
          : msg
      );
    } finally {
      continuousRunningRef.current = false;
      setIsContinuousRunning(false);
      setBusy("");
      wsRef.current = null;
    }
  }

  function stopContinuous() {
    continuousRunningRef.current = false;
    setIsContinuousRunning(false);
    setBusy("");
  }

  // Gemini Natural Language Sentence Generation
  async function handleGenerateSentence(
    seqToUse?: string[],
    moodToUse: SentenceMood = selectedMood
  ) {
    const targetSeq = seqToUse || recognizedSequence;
    if (targetSeq.length === 0) {
      setGenerationError("Please perform at least one sign first.");
      return;
    }

    // Cancel prior in-flight request
    abortControllerRef.current?.abort();
    const controller = new AbortController();
    abortControllerRef.current = controller;

    const currentSeqId = ++sequenceIdRef.current;
    setIsGenerating(true);
    setGenerationError("");

    try {
      const sentence = await interpretSignSequence(targetSeq, moodToUse, controller.signal);
      if (currentSeqId !== sequenceIdRef.current) return;

      setGeneratedSentence(sentence);

      // Persist full sentence to sentence history
      try {
        saveSentenceRecord({
          sentence,
          signs: targetSeq,
          mood: moodToUse,
          timestamp: new Date().toLocaleString(),
          sessionId: session || undefined,
          source: "live",
        });
      } catch {
        /* ignore */
      }

      // Defaultly speak automatically without user needing to press speak button!
      const autoSpeakEnabled = localStorage.getItem("sb_autospeak") !== "false";
      if (autoSpeakEnabled && !isEchoOfLastSpoken(sentence)) {
        speakSentence(sentence, moodToUse);
      }
    } catch (err: unknown) {
      if (currentSeqId !== sequenceIdRef.current) return;
      const message =
        err instanceof Error ? err.message : "Unable to generate sentence right now.";
      setGenerationError(message);
    } finally {
      if (currentSeqId === sequenceIdRef.current) {
        setIsGenerating(false);
      }
    }
  }

  function handleMoodSelect(newMood: SentenceMood) {
    setSelectedMood(newMood);
    if (generatedSentence) {
      // Immediately speak the sentence in the new mood's tone:
      speakSentence(generatedSentence, newMood);
      // And adapt the phrasing to match the emotional context:
      if (recognizedSequence.length > 0) {
        handleGenerateSentence(recognizedSequence, newMood);
      }
    }
  }

  function handleClearSentence() {
    if (autoGenerateTimerRef.current) {
      clearTimeout(autoGenerateTimerRef.current);
      autoGenerateTimerRef.current = null;
    }
    sequenceIdRef.current++;
    abortControllerRef.current?.abort();
    abortControllerRef.current = null;
    setRecognizedSequence([]);
    setGeneratedSentence("");
    setGenerationError("");
    lastSignLabelRef.current = "";
    armedRef.current = true;
    freshAttemptRef.current = false;
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
    setIsSpeaking(false);
  }

  function removeSignAtIndex(index: number) {
    setRecognizedSequence((prev) => prev.filter((_, i) => i !== index));
    lastSignLabelRef.current = "";
  }

  async function submitFeedback(rating: number) {
    if (!result?.prediction_id) return;
    try {
      await api.feedback(result.prediction_id, undefined, rating);
      setFeedbackSent(rating > 0 ? "up" : "down");
    } catch {
      // non-blocking feedback
    }
  }

  const confidencePercentage = Math.round(conf * 100);

  return (
    <div className="space-y-6 max-w-5xl animate-in fade-in duration-200">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <CameraIcon className="w-6 h-6 text-brand-600 dark:text-brand-400" />
          Continuous Sign Language Recognition & Translation
        </h2>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Perform multiple consecutive ISL signs to accumulate a sentence sequence, then generate natural English through Gemini AI and hear it spoken aloud.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Camera Viewport (8 cols, ~14% wider than before) */}
        <div className="lg:col-span-8 space-y-4">
          <div className="relative aspect-video rounded-2xl overflow-hidden bg-slate-900 border-2 border-slate-200 dark:border-slate-800 shadow-lg flex items-center justify-center">
            <video
              ref={videoRef}
              className={`w-full h-full object-cover transform -scale-x-100 ${camOn ? "block" : "hidden"}`}
              muted
              playsInline
              aria-label="camera-preview"
            />
            {!camOn && (
              <div className="text-center p-6 space-y-3">
                <div className="w-16 h-16 rounded-full bg-slate-800 text-slate-400 mx-auto flex items-center justify-center">
                  <CameraIcon className="w-8 h-8" />
                </div>
                <p className="text-slate-400 text-sm font-medium">Camera is currently inactive</p>
                <button
                  type="button"
                  onClick={() => enableCamera()}
                  className="px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-semibold text-sm shadow-md transition"
                >
                  Enable Camera
                </button>
              </div>
            )}

            {/* Live Indicator Overlay */}
            {camOn && (
              <>
                <div className="absolute top-3 left-3 flex items-center gap-2 px-3 py-1 rounded-full bg-black/60 backdrop-blur-md text-xs font-semibold text-white border border-white/10 z-10">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
                  <span>{isContinuousRunning ? "Continuous Mode Active" : "Camera Live"}</span>
                </div>

                {/* Hand Position Guide Overlay */}
                <div className="absolute inset-0 pointer-events-none flex items-center justify-center p-6">
                  <div className="w-4/5 h-4/5 border border-dashed border-brand-400/40 rounded-2xl flex flex-col justify-between p-3">
                    <div className="flex justify-between">
                      <span className="w-4 h-4 border-t-2 border-l-2 border-brand-400"></span>
                      <span className="w-4 h-4 border-t-2 border-r-2 border-brand-400"></span>
                    </div>
                    <div className="text-center">
                      <span className="text-[10px] font-mono tracking-wider text-brand-300 bg-black/50 px-3 py-1 rounded-full backdrop-blur-xs border border-brand-500/20">
                        POSITION HANDS IN FRAME
                      </span>
                    </div>
                <div className="flex justify-between">
                  <span className="w-4 h-4 border-b-2 border-l-2 border-brand-400"></span>
                  <span className="w-4 h-4 border-b-2 border-r-2 border-brand-400"></span>
                </div>
              </div>
            </div>

            {/* Single-sign readiness countdown */}
            {countdown !== null && countdown > 0 && (
              <div
                className="absolute inset-0 z-20 flex flex-col items-center justify-center bg-black/55 backdrop-blur-sm pointer-events-none"
                role="status"
                aria-live="polite"
                aria-label={`Get ready — capturing in ${countdown}`}
              >
                <span className="text-7xl font-black text-white drop-shadow-lg tabular-nums">
                  {countdown}
                </span>
                <span className="mt-2 text-sm font-semibold tracking-wider text-brand-200 uppercase">
                  Get ready — hold your sign
                </span>
              </div>
            )}
          </>
        )}

            {/* State pill */}
            <div className="absolute top-3 right-3 px-3 py-1 rounded-full bg-black/60 backdrop-blur-md text-xs font-bold text-white border border-white/10 z-10">
              State: <span className="text-brand-400">{state}</span>
            </div>
          </div>

          {/* Action Toolbar */}
          <div className="flex flex-wrap items-center gap-3">
            {!camOn ? (
              <button
                type="button"
                onClick={() => enableCamera()}
                className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-medium text-sm transition"
              >
                Enable Camera
              </button>
            ) : (
              <button
                type="button"
                onClick={stopCamera}
                className="px-4 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-medium text-sm transition"
              >
                Stop Camera
              </button>
            )}

            {/* Continuous Recognition Toggle */}
            {!isContinuousRunning ? (
              <button
                type="button"
                onClick={startContinuous}
                disabled={!camOn || Boolean(busy)}
                className="px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 disabled:opacity-40 text-white font-bold text-sm shadow-md transition flex items-center gap-2"
              >
                <CameraIcon className="w-4 h-4" />
                Start Continuous
              </button>
            ) : (
              <button
                type="button"
                onClick={stopContinuous}
                className="px-5 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-700 text-white font-bold text-sm shadow-md transition flex items-center gap-2 animate-pulse"
              >
                <span>⏹ Stop Recognition</span>
              </button>
            )}

            {/* Single Sign Capture */}
            <button
              type="button"
              onClick={startSingle}
              disabled={!camOn || Boolean(busy) || isContinuousRunning}
              className="px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 disabled:opacity-40 text-slate-800 dark:text-slate-200 font-medium text-sm transition"
              title="Perform one sign during a 3.5 s capture window"
            >
              Single Sign
            </button>

            <button
              type="button"
              onClick={() => {
                setResult(null);
                setState(camOn ? "Tracking" : "Ready");
                setNote("");
                setLatency(null);
              }}
              className="px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 font-medium text-sm transition flex items-center gap-1.5"
              title="Clear single frame output"
            >
              <RefreshIcon className="w-4 h-4" />
            </button>
          </div>

          {busy && (
            <div
              className="p-3 rounded-lg bg-brand-50 dark:bg-brand-950/60 border border-brand-200 dark:border-brand-800 text-brand-800 dark:text-brand-300 text-sm flex items-center gap-2"
              role="status"
              aria-live="polite"
            >
              <span className="w-4 h-4 border-2 border-brand-600 border-t-transparent rounded-full animate-spin shrink-0"></span>
              <span>{busy}</span>
            </div>
          )}

          {note && (
            <div
              role="alert"
              className="p-3 rounded-lg bg-amber-50 dark:bg-amber-950/60 border border-amber-200 dark:border-amber-800 text-amber-800 dark:text-amber-300 text-sm flex items-center gap-2"
            >
              <AlertCircleIcon className="w-4 h-4 shrink-0" />
              <span>{note}</span>
            </div>
          )}
        </div>

        {/* Prediction Results & Translation Cards (4 cols) */}
        <div className="lg:col-span-4 space-y-4">
          {/* Section: Continuous Recognized Signs Buffer */}
          <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center gap-2">
                <span>Recognized Signs Sequence</span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-brand-100 dark:bg-brand-950 text-brand-700 dark:text-brand-300 font-mono font-bold">
                  {recognizedSequence.length}
                </span>
              </h3>
              {recognizedSequence.length > 0 && (
                <button
                  type="button"
                  onClick={handleClearSentence}
                  className="text-xs text-rose-600 dark:text-rose-400 hover:underline font-semibold"
                >
                  Clear Sequence
                </button>
              )}
            </div>

            {recognizedSequence.length > 0 ? (
              <div className="flex flex-wrap gap-2 pt-1 max-h-36 overflow-y-auto">
                {recognizedSequence.map((sign, idx) => (
                  <span
                    key={`${sign}-${idx}`}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-sm font-extrabold uppercase bg-brand-500 text-white shadow-sm"
                  >
                    <span>{sign}</span>
                    <button
                      type="button"
                      onClick={() => removeSignAtIndex(idx)}
                      className="hover:opacity-75 text-xs font-normal"
                      title="Remove sign"
                      aria-label={`Remove sign ${sign}`}
                    >
                      ✕
                    </button>
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-400 italic py-2">
                Perform signs to accumulate a continuous sequence (e.g. GO → WATER → DRINK).
              </p>
            )}
          </div>

          {/* Section: Natural English Sentence (Gemini AI) */}
          <div className="p-6 rounded-2xl bg-gradient-to-br from-slate-900 via-slate-900 to-brand-950 text-white border border-slate-800 shadow-lg space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold uppercase tracking-wider text-brand-300 flex items-center gap-2">
                <SparklesIcon className="w-4 h-4 text-brand-400" />
                <span>Generated Sentence (Gemini AI)</span>
              </h3>
              <div className="flex items-center gap-2">
                {isGenerating && (
                  <span className="text-xs font-semibold text-brand-300 flex items-center gap-1.5">
                    <span className="w-3 h-3 border-2 border-brand-400 border-t-transparent rounded-full animate-spin"></span>
                    Auto-Translating...
                  </span>
                )}
                {isSpeaking && (
                  <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1.5 animate-pulse">
                    <span>🔊</span>
                    Speaking ({MOODS.find((m) => m.id === selectedMood)?.label})...
                  </span>
                )}
              </div>
            </div>

            <div className="min-h-[50px] flex items-center">
              {generatedSentence ? (
                <div className="space-y-1.5 w-full">
                  <p className="text-xl md:text-2xl font-bold tracking-tight text-white leading-snug">
                    &ldquo;{generatedSentence}&rdquo;
                  </p>
                  <div className="flex items-center gap-2 pt-1">
                    <span
                      className={`inline-flex items-center gap-1 text-[10px] uppercase font-bold px-2.5 py-0.5 rounded-full ${
                        MOODS.find((m) => m.id === selectedMood)?.badgeClass || ""
                      }`}
                    >
                      <span>{MOODS.find((m) => m.id === selectedMood)?.emoji}</span>
                      <span>{MOODS.find((m) => m.id === selectedMood)?.label} Tone</span>
                    </span>
                    <span className="text-[11px] text-slate-400">
                      ⚡ Hands-free auto-speak enabled
                    </span>
                  </div>
                </div>
              ) : (
                <p className="text-slate-400 text-xs">
                  {recognizedSequence.length > 0
                    ? "✨ Hands-free active: translating and speaking automatically as you sign..."
                    : "Accumulate recognized signs above. Sentence interpretation and speech happen automatically."}
                </p>
              )}
            </div>

            {/* Quick Actions (Replay / Manual Generate / Clear) */}
            <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-white/10">
              <button
                type="button"
                onClick={() => handleGenerateSentence()}
                disabled={recognizedSequence.length === 0 || isGenerating}
                className="px-4 py-2 rounded-xl bg-brand-500 hover:bg-brand-600 disabled:opacity-40 text-white text-xs font-bold shadow-md transition flex items-center gap-2"
              >
                <SparklesIcon className="w-4 h-4" />
                {isGenerating ? "Translating..." : "Regenerate"}
              </button>

              {generatedSentence && (
                <button
                  type="button"
                  onClick={() => speakSentence(generatedSentence, selectedMood)}
                  disabled={isSpeaking}
                  className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold border border-slate-700 transition flex items-center gap-2"
                >
                  <VolumeUpIcon className="w-4 h-4" />
                  {isSpeaking ? "Speaking..." : "🔊 Replay Speech"}
                </button>
              )}

              <button
                type="button"
                onClick={handleClearSentence}
                disabled={recognizedSequence.length === 0 && !generatedSentence}
                className="px-3 py-2 rounded-xl bg-slate-800/60 hover:bg-slate-700/60 text-slate-300 hover:text-white text-xs font-semibold transition"
              >
                Clear Sentence
              </button>
            </div>

            {/* Emotional Mood Selection (Normal, Happy, Sad, Angry) */}
            <div className="pt-3 border-t border-white/10 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                  Select Speech Mood & Emotion:
                </span>
                <span className="text-[11px] text-brand-300 font-medium">
                  {MOODS.find((m) => m.id === selectedMood)?.description}
                </span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {MOODS.map((m) => (
                  <button
                    key={m.id}
                    type="button"
                    onClick={() => handleMoodSelect(m.id)}
                    className={`px-3 py-2.5 rounded-xl text-xs font-bold transition flex items-center justify-center gap-2 border ${
                      selectedMood === m.id
                        ? `${m.activeClass} border-transparent scale-[1.02]`
                        : "bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 border-slate-700/60"
                    }`}
                    title={m.description}
                  >
                    <span className="text-base">{m.emoji}</span>
                    <span>{m.label} Mood</span>
                  </button>
                ))}
              </div>
            </div>

            {generationError && (
              <div className="p-3 rounded-lg bg-rose-950/80 border border-rose-800 text-rose-200 text-xs flex items-center justify-between">
                <span>{generationError}</span>
                <button
                  type="button"
                  onClick={() => handleGenerateSentence()}
                  className="underline hover:no-underline font-semibold ml-2"
                >
                  Retry
                </button>
              </div>
            )}
          </div>

          {/* Section: Latest Single-Frame Output Details */}
          <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
            <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              <span>Latest Sign Frame</span>
              {latency !== null && (
                <span className="font-mono text-emerald-600 dark:text-emerald-400">{latency} ms</span>
              )}
            </div>

            <div className="py-3 text-center rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800/80">
              {result && state === "Recognized" ? (
                <div className="space-y-2">
                  <span className="text-2xl font-black text-slate-900 dark:text-white uppercase block">
                    {result.label}
                  </span>
                  <p className="text-xs text-slate-400 font-mono">Class: {result.class_id}</p>
                  {result.class_id && (
                    <div className="pt-1">
                      <img
                        src={`/assets/${result.class_id}.jpg`}
                        alt={`${result.label} ISL sign`}
                        loading="lazy"
                        className="w-20 h-20 object-cover rounded-xl border border-slate-200 dark:border-slate-700 mx-auto shadow-sm"
                        onError={(e) => {
                          (e.target as HTMLElement).style.display = "none";
                        }}
                      />
                      <span className="text-[10px] text-slate-400 mt-1 block">Reference Sign Demonstration</span>
                    </div>
                  )}
                </div>
              ) : result && state === "Provisional" ? (
                <div>
                  <span className="text-xl font-extrabold text-sky-600 dark:text-sky-400 uppercase">
                    {result.label} …
                  </span>
                  <p className="text-xs text-sky-500">Provisional Prediction — not added</p>
                </div>
              ) : result && state === "Uncertain" ? (
                <div>
                  <span className="text-xl font-extrabold text-amber-600 dark:text-amber-400 uppercase">
                    {result.label} ?
                  </span>
                  <p className="text-xs text-amber-500">Uncertain Prediction</p>
                </div>
              ) : (
                <div className="text-slate-400 py-2 text-xs">
                  {camOn ? "Waiting for sign gesture..." : "Enable camera to start"}
                </div>
              )}
            </div>


            {result && (
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-slate-500">Confidence</span>
                  <span className="text-brand-600 dark:text-brand-400">{confidencePercentage}%</span>
                </div>
                <div className="w-full h-2 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-300 ${
                      confidencePercentage >= 70
                        ? "bg-emerald-500"
                        : confidencePercentage >= 40
                        ? "bg-amber-500"
                        : "bg-rose-500"
                    }`}
                    style={{ width: `${confidencePercentage}%` }}
                  ></div>
                </div>
              </div>
            )}

            {/* Uncertainty panel — real model top-k only, never invented. */}
            {showConfirmPanel && candidates.length > 0 && (
              <div className="rounded-xl border border-amber-300 dark:border-amber-700 bg-amber-50 dark:bg-amber-950/40 p-3 space-y-2">
                <p className="text-xs font-bold uppercase tracking-wider text-amber-700 dark:text-amber-300">
                  Recognition uncertain
                </p>
                <p className="text-[11px] text-amber-800/90 dark:text-amber-200/90">
                  Primary: <strong>{candidates[0].label}</strong> ({(candidates[0].confidence * 100).toFixed(1)}%)
                </p>
                {candidates.length > 1 && (
                  <div>
                    <p className="text-[11px] font-semibold text-slate-600 dark:text-slate-300 mb-1">
                      Other possible candidates:
                    </p>
                    <ul className="space-y-1">
                      {candidates.slice(1, 4).map((c) => (
                        <li key={c.class_id}>
                          <button
                            type="button"
                            onClick={() => confirmUserSelection(c)}
                            className="w-full flex items-center justify-between px-2 py-1.5 rounded-lg text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 hover:border-brand-500 hover:shadow-sm transition"
                          >
                            <span className="font-semibold text-slate-800 dark:text-slate-100">
                              {c.label}
                            </span>
                            <span className="font-mono text-slate-400">
                              {(c.confidence * 100).toFixed(1)}%
                            </span>
                          </button>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                <div className="flex gap-2 pt-1">
                  <button
                    type="button"
                    onClick={() => confirmUserSelection(candidates[0])}
                    className="flex-1 px-2 py-1.5 rounded-lg text-xs font-bold bg-brand-500 text-white hover:bg-brand-600 transition"
                  >
                    Confirm {candidates[0].label}
                  </button>
                  <button
                    type="button"
                    onClick={() => dismissCandidates("retry")}
                    className="flex-1 px-2 py-1.5 rounded-lg text-xs font-semibold border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-200 hover:bg-white dark:hover:bg-slate-800 transition"
                  >
                    Try again
                  </button>
                  <button
                    type="button"
                    onClick={() => dismissCandidates("dismiss")}
                    className="flex-1 px-2 py-1.5 rounded-lg text-xs font-semibold border border-slate-300 dark:border-slate-600 text-slate-500 dark:text-slate-400 hover:bg-white dark:hover:bg-slate-800 transition"
                  >
                    Dismiss
                  </button>
                </div>
                <p className="text-[10px] text-slate-500 dark:text-slate-400">
                  A confirmed word is a user selection, not proof the model auto-recognized it.
                </p>
              </div>
            )}

            {lastUserConfirmed && recognizedSequence.length > 0 && (
              <p className="text-[11px] text-sky-600 dark:text-sky-400">
                Last word added by user confirmation.
              </p>
            )}

            {result && result.prediction_id && (
              <div className="pt-2 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs">
                <span className="text-slate-400">Frame feedback:</span>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => submitFeedback(1)}
                    disabled={feedbackSent !== null}
                    className={`px-2 py-0.5 rounded border text-xs ${
                      feedbackSent === "up"
                        ? "bg-emerald-100 dark:bg-emerald-900 text-emerald-700"
                        : "hover:bg-slate-100 dark:hover:bg-slate-800"
                    }`}
                  >
                    👍
                  </button>
                  <button
                    type="button"
                    onClick={() => submitFeedback(-1)}
                    disabled={feedbackSent !== null}
                    className={`px-2 py-0.5 rounded border text-xs ${
                      feedbackSent === "down"
                        ? "bg-rose-100 dark:bg-rose-900 text-rose-700"
                        : "hover:bg-slate-100 dark:hover:bg-slate-800"
                    }`}
                  >
                    👎
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
