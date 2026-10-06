import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useRef, useState } from "react";
import { api } from "../api/client";
import { MediaPipeProvider, isFiniteFrame } from "../landmarks";
const STATES = [
    "Ready",
    "Tracking",
    "Recognized",
    "Uncertain",
    "No-Sign",
    "Tracking-Lost",
    "Error",
];
function toState(apiStatus, ok) {
    if (!ok)
        return "Error";
    if (apiStatus === "recognized")
        return "Recognized";
    return "Uncertain";
}
export default function Live({ onResult }) {
    const [state, setState] = useState("Ready");
    const [session, setSession] = useState("");
    const [result, setResult] = useState(null);
    const [conf, setConf] = useState(0);
    const [note, setNote] = useState("");
    const [camOn, setCamOn] = useState(false);
    const [busy, setBusy] = useState("");
    const videoRef = useRef(null);
    const streamRef = useRef(null);
    const providerRef = useRef(null);
    function provider() {
        if (!providerRef.current)
            providerRef.current = new MediaPipeProvider();
        return providerRef.current;
    }
    useEffect(() => () => {
        streamRef.current?.getTracks().forEach((t) => t.stop());
    }, []);
    async function enableCamera() {
        setNote("");
        try {
            const s = await navigator.mediaDevices.getUserMedia({ video: { width: 640 } });
            streamRef.current = s;
            if (videoRef.current) {
                videoRef.current.srcObject = s;
                await videoRef.current.play().catch(() => { });
            }
            setCamOn(true);
            setState("Tracking");
        }
        catch {
            setState("Error");
            setNote("Camera denied or unavailable. Check browser permission and retry.");
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
        }
        catch (e) {
            setBusy("");
            const msg = e instanceof Error ? e.message : "Recognition failed.";
            if (/No hands detected/.test(msg)) {
                setState("Tracking-Lost");
            }
            else {
                setState("Error");
            }
            setNote(msg + " All video processing stays on this device.");
        }
    }
    async function speak() {
        if (!result)
            return;
        try {
            await api.tts(result.label);
        }
        catch (e) {
            setNote(e instanceof Error && e.code === "TTS_NOT_CONFIGURED"
                ? "Speech engine not configured yet (P5 wiring) — text result kept."
                : e instanceof Error
                    ? e.message
                    : "Speech failed.");
        }
    }
    return (_jsxs("section", { "aria-label": "live-recognition", children: [_jsx("h2", { children: "Live recognition" }), _jsxs("p", { role: "status", "aria-live": "polite", children: ["State: ", _jsx("strong", { children: state }), result && state === "Recognized" && (_jsxs("span", { style: { fontSize: 40, display: "block" }, children: [result.label, " (", conf.toFixed(2), ")"] }))] }), _jsx("video", { ref: videoRef, width: 320, muted: true, playsInline: true, "aria-label": "camera-preview" }), _jsxs("div", { style: { display: "flex", gap: 8, marginTop: 8, flexWrap: "wrap" }, children: [!camOn ? (_jsx("button", { type: "button", onClick: enableCamera, children: "Enable camera" })) : (_jsx("button", { type: "button", onClick: stopCamera, children: "Stop camera" })), _jsx("button", { type: "button", onClick: start, disabled: !camOn, children: "Start recognition" }), _jsx("button", { type: "button", onClick: speak, disabled: !result, children: "Speak" }), _jsx("button", { type: "button", onClick: () => {
                            setResult(null);
                            setState(camOn ? "Tracking" : "Ready");
                            setNote("");
                        }, children: "Clear" })] }), note && _jsx("p", { role: "alert", children: note }), busy && (_jsx("p", { role: "status", "aria-live": "polite", children: busy })), _jsxs("details", { children: [_jsx("summary", { children: "All states (for testers)" }), _jsx("ul", { children: STATES.map((s) => (_jsx("li", { children: s }, s))) })] })] }));
}
