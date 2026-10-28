import React, { useState } from "react";
import { api, setToken as saveToken } from "../api/client";
import { CogIcon, CheckCircleIcon, AlertCircleIcon } from "../components/Icons";
import { DEFAULT_THRESHOLD_PERCENT } from "./Live";
import {
  getGeminiModelName,
  setGeminiModelName,
  listAvailableGeminiModels,
  interpretSignSequence,
  CANDIDATE_MODELS,
} from "../api/gemini";

export const THEME_PRESETS = [
  { name: "Ocean Teal", hue: 188, color: "#14b8a6" },
  { name: "Royal Violet", hue: 260, color: "#8b5cf6" },
  { name: "Sapphire Blue", hue: 215, color: "#3b82f6" },
  { name: "Emerald Mint", hue: 155, color: "#10b981" },
  { name: "Sunset Orange", hue: 30, color: "#f97316" },
  { name: "Ruby Rose", hue: 345, color: "#f43f5e" },
];

interface SettingsProps {
  currentTheme: "dark" | "light" | "system";
  onThemeChange: (theme: "dark" | "light" | "system") => void;
  currentHue?: number;
  onHueChange?: (hue: number) => void;
}

export default function Settings({
  currentTheme,
  onThemeChange,
  currentHue = 188,
  onHueChange,
}: SettingsProps) {
  const [tok, setTok] = useState(localStorage.getItem("sb_token") || "change-me");
  const [showToken, setShowToken] = useState(false);
  const [saved, setSaved] = useState(false);
  const [geminiKey, setGeminiKey] = useState(
    () => localStorage.getItem("sb_gemini_api_key") || import.meta.env.VITE_GEMINI_API_KEY || ""
  );
  const [showGeminiKey, setShowGeminiKey] = useState(false);
  const [geminiSaved, setGeminiSaved] = useState(false);
  const [geminiModel, setGeminiModel] = useState<string>(() => getGeminiModelName());
  const [modelOptions, setModelOptions] = useState<string[]>(() => {
    return Array.from(new Set(["auto", getGeminiModelName(), ...CANDIDATE_MODELS]));
  });
  const [detectingModels, setDetectingModels] = useState(false);
  const [testingGemini, setTestingGemini] = useState(false);
  const [geminiTestResult, setGeminiTestResult] = useState<{
    success: boolean;
    message: string;
  } | null>(null);
  const [threshold, setThreshold] = useState<number>(() => {
    const val = localStorage.getItem("sb_threshold");
    return val ? parseInt(val, 10) : DEFAULT_THRESHOLD_PERCENT;
  });
  // Manual gate is engaged only when the slider itself writes sb_threshold;
  // saving other settings must never silently create a frontend floor.
  const [manualGate, setManualGate] = useState<boolean>(
    () => localStorage.getItem("sb_threshold") !== null
  );
  const [autoSpeak, setAutoSpeak] = useState<boolean>(() => {
    return localStorage.getItem("sb_autospeak") !== "false";
  });
  const [testingConnection, setTestingConnection] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<string | null>(null);

  async function handleSaveGeminiKey() {
    const key = geminiKey.trim();
    localStorage.setItem("sb_gemini_api_key", key);
    setGeminiSaved(true);
    setTimeout(() => setGeminiSaved(false), 3000);
    if (key) {
      await handleDetectModels();
    }
  }

  function handleModelChange(model: string) {
    setGeminiModel(model);
    setGeminiModelName(model);
  }

  async function handleDetectModels() {
    if (!geminiKey.trim()) {
      setGeminiTestResult({
        success: false,
        message: "Please enter your Gemini API key first.",
      });
      return;
    }
    setDetectingModels(true);
    setGeminiTestResult(null);
    try {
      const models = await listAvailableGeminiModels(geminiKey.trim());
      if (models.length > 0) {
        const merged = Array.from(new Set(["auto", ...models, ...CANDIDATE_MODELS]));
        setModelOptions(merged);
        const best = models[0];
        setGeminiTestResult({
          success: true,
          message: `Universal compatibility active! Found ${models.length} supported models on your key (top: ${best}).`,
        });
      } else {
        setGeminiTestResult({
          success: true,
          message: "Key saved. Universal fallback active across all Gemini 2.5, 2.0, 1.5, and Pro models.",
        });
      }
    } catch (err: unknown) {
      setGeminiTestResult({
        success: false,
        message: err instanceof Error ? err.message : "Failed to detect models.",
      });
    } finally {
      setDetectingModels(false);
    }
  }

  async function handleTestGemini() {
    if (!geminiKey.trim()) {
      setGeminiTestResult({
        success: false,
        message: "Please enter your Gemini API key first.",
      });
      return;
    }
    setTestingGemini(true);
    setGeminiTestResult(null);
    try {
      const output = await interpretSignSequence(["HELLO", "WELCOME", "FRIEND"]);
      setGeminiTestResult({
        success: true,
        message: `Success with ${geminiModel}! Output: "${output}"`,
      });
    } catch (err: unknown) {
      setGeminiTestResult({
        success: false,
        message: err instanceof Error ? err.message : "Gemini test failed.",
      });
    } finally {
      setTestingGemini(false);
    }
  }

  function handleSaveToken() {
    saveToken(tok);
    localStorage.setItem("sb_autospeak", autoSpeak.toString());
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  }

  async function testConnection() {
    setTestingConnection(true);
    setConnectionStatus(null);
    try {
      const res = await api.health();
      setConnectionStatus(`Connected! Model: ${res.model_version || "ready"}`);
    } catch {
      setConnectionStatus("Connection failed. Make sure backend is running on port 8000.");
    } finally {
      setTestingConnection(false);
    }
  }

  return (
    <div className="space-y-8 max-w-3xl mx-auto animate-in fade-in duration-200">
      <div>
        <h2 className="text-2xl font-bold text-midnight dark:text-white tracking-tight flex items-center gap-2">
          <CogIcon className="w-6 h-6 text-teal-deep dark:text-seafoam" />
          System Settings &amp; Preferences
        </h2>
        <p className="text-sm text-text-secondary mt-1">
          Configure API connection endpoints, authentication credentials, and interface options.
        </p>
      </div>

      {/* Backend & Connection */}
      <div className="p-6 rounded-2xl bg-white dark:bg-midnight border border-card-border shadow-xs space-y-4">
        <h3 className="text-base font-bold text-midnight dark:text-white">Backend Connection</h3>
        <div className="space-y-2">
          <label htmlFor="api-base-input" className="block text-xs font-semibold uppercase text-text-secondary">
            API Base Endpoint
          </label>
          <div className="flex gap-3">
            <input
              id="api-base-input"
              type="text"
              readOnly
              value={import.meta.env.VITE_API_BASE || "http://localhost:8000"}
              className="flex-1 px-4 py-2.5 rounded-xl border border-card-border bg-soft-surface dark:bg-midnight-light text-sm font-mono text-midnight dark:text-white"
            />
            <button
              type="button"
              onClick={testConnection}
              disabled={testingConnection}
              className="px-4 py-2.5 rounded-xl bg-soft-surface dark:bg-midnight-light hover:bg-[#eae6dc] dark:hover:bg-[#253f54] border border-card-border text-xs font-semibold text-midnight dark:text-white transition shadow-2xs"
            >
              {testingConnection ? "Testing…" : "Test Connection"}
            </button>
          </div>
          {connectionStatus && (
            <p className={`text-xs font-medium mt-1 ${connectionStatus.includes("Connected") ? "text-teal-deep dark:text-seafoam font-semibold" : "text-rose-600 dark:text-rose-400 font-semibold"}`}>
              {connectionStatus}
            </p>
          )}
        </div>
      </div>

      {/* Authentication Token */}
      <div className="p-6 rounded-2xl bg-white dark:bg-midnight border border-card-border shadow-xs space-y-4">
        <h3 className="text-base font-bold text-midnight dark:text-white">Backend Authentication</h3>
        <p className="text-xs text-text-secondary">
          Guarded endpoints (predict, sessions, TTS, admin) validate this Bearer token against the backend secret.
        </p>
        <div className="space-y-2">
          <label htmlFor="token-input" className="block text-xs font-semibold uppercase text-text-secondary">
            Bearer Token
          </label>
          <div className="flex gap-2">
            <input
              id="token-input"
              type={showToken ? "text" : "password"}
              value={tok}
              onChange={(e) => setTok(e.target.value)}
              aria-label="api-token"
              autoComplete="off"
              className="flex-1 px-4 py-2.5 rounded-xl border border-card-border bg-soft-surface dark:bg-midnight-light text-sm font-mono text-midnight dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-deep/30 focus:border-teal-deep"
            />
            <button
              type="button"
              onClick={() => setShowToken(!showToken)}
              className="px-3 py-2 text-xs font-medium text-text-secondary hover:text-midnight dark:hover:text-white"
            >
              {showToken ? "Hide" : "Show"}
            </button>
            <button
              type="button"
              onClick={handleSaveToken}
              className="px-5 py-2.5 rounded-xl bg-teal-deep hover:bg-deep-teal-hover text-white font-semibold text-xs transition shadow-xs"
            >
              Save
            </button>
          </div>
          {saved && (
            <p role="status" className="text-xs text-teal-deep dark:text-seafoam font-semibold flex items-center gap-1 mt-1">
              <CheckCircleIcon className="w-4 h-4" />
              Settings saved locally.
            </p>
          )}
        </div>
      </div>

      {/* Gemini Natural Language Interpretation */}
      <div className="p-6 rounded-2xl bg-white dark:bg-midnight border border-card-border shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-midnight dark:text-white flex items-center gap-2">
            <span>Gemini AI (Sentence Interpretation)</span>
          </h3>
          <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-seafoam-light dark:bg-seafoam/20 text-teal-deep dark:text-seafoam border border-seafoam/30">
            Natural English
          </span>
        </div>
        <p className="text-xs text-text-secondary">
          Used to interpret accumulated ISL sign sequences (e.g. &ldquo;GO WATER DRINK&rdquo;) into coherent English sentences (e.g. &ldquo;I am going to drink water.&rdquo;).
        </p>
        <div className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="gemini-key-input" className="block text-xs font-semibold uppercase text-text-secondary">
              Google Gemini API Key
            </label>
            <div className="flex gap-2">
              <input
                id="gemini-key-input"
                type={showGeminiKey ? "text" : "password"}
                value={geminiKey}
                onChange={(e) => setGeminiKey(e.target.value)}
                placeholder="AIzaSy..."
                aria-label="gemini-api-key"
                autoComplete="off"
                className="flex-1 px-4 py-2.5 rounded-xl border border-card-border bg-soft-surface dark:bg-midnight-light text-sm font-mono text-midnight dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-deep/30 focus:border-teal-deep"
              />
              <button
                type="button"
                onClick={() => setShowGeminiKey(!showGeminiKey)}
                className="px-3 py-2 text-xs font-medium text-text-secondary hover:text-midnight dark:hover:text-white"
              >
                {showGeminiKey ? "Hide" : "Show"}
              </button>
              <button
                type="button"
                onClick={handleSaveGeminiKey}
                className="px-5 py-2.5 rounded-xl bg-teal-deep hover:bg-deep-teal-hover text-white font-semibold text-xs transition shadow-xs"
              >
                Save Key
              </button>
            </div>
            {geminiSaved && (
              <p role="status" className="text-xs text-teal-deep dark:text-seafoam font-semibold flex items-center gap-1 mt-1">
                <CheckCircleIcon className="w-4 h-4" />
                Gemini API key saved locally.
              </p>
            )}
            <p className="text-[11px] text-text-secondary">
              Stored in your browser&apos;s localStorage (<code className="font-mono">sb_gemini_api_key</code>) or loaded from <code className="font-mono">VITE_GEMINI_API_KEY</code>. Never committed or sent to the backend.
            </p>
          </div>

          {/* Model Selection & Auto-Discovery */}
          <div className="pt-2 border-t border-card-border/60 space-y-2">
            <div className="flex items-center justify-between">
              <label htmlFor="gemini-model-select" className="block text-xs font-semibold uppercase text-text-secondary">
                Gemini Model
              </label>
              <span className="text-[11px] text-text-secondary">
                Active: <strong className="text-midnight dark:text-white font-mono">{geminiModel}</strong>
              </span>
            </div>
            <div className="flex gap-2">
              <select
                id="gemini-model-select"
                value={geminiModel}
                onChange={(e) => handleModelChange(e.target.value)}
                className="flex-1 px-4 py-2.5 rounded-xl border border-card-border bg-soft-surface dark:bg-midnight-light text-sm font-medium text-midnight dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-deep/30 focus:border-teal-deep"
              >
                {modelOptions.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt === "auto"
                      ? "⚡ Auto-Detect (Universal: Works with ANY Gemini model)"
                      : `${opt} ${opt === "gemini-2.0-flash" ? "(Fastest)" : ""}`}
                  </option>
                ))}
              </select>
              <button
                type="button"
                onClick={handleDetectModels}
                disabled={detectingModels}
                className="px-4 py-2.5 rounded-xl bg-soft-surface dark:bg-midnight-light hover:bg-[#eae6dc] dark:hover:bg-[#253f54] border border-card-border text-xs font-semibold text-midnight dark:text-white transition disabled:opacity-50 shadow-2xs"
              >
                {detectingModels ? "Detecting…" : "Auto-Detect Models"}
              </button>
              <button
                type="button"
                onClick={handleTestGemini}
                disabled={testingGemini}
                className="px-4 py-2.5 rounded-xl bg-seafoam-light dark:bg-seafoam/20 border border-seafoam/30 hover:bg-seafoam/30 text-xs font-semibold text-teal-deep dark:text-seafoam transition disabled:opacity-50 shadow-2xs"
              >
                {testingGemini ? "Testing…" : "Test API"}
              </button>
            </div>
            {geminiTestResult && (
              <div
                className={`p-3 rounded-xl text-xs font-medium flex items-start gap-2 mt-2 ${
                  geminiTestResult.success
                    ? "bg-seafoam-light dark:bg-seafoam/20 text-teal-deep dark:text-seafoam border border-seafoam/30"
                    : "bg-rose-50 dark:bg-rose-950/40 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-800"
                }`}
              >
                {geminiTestResult.success ? (
                  <CheckCircleIcon className="w-4 h-4 shrink-0 mt-0.5" />
                ) : (
                  <AlertCircleIcon className="w-4 h-4 shrink-0 mt-0.5" />
                )}
                <div className="flex-1">{geminiTestResult.message}</div>
              </div>
            )}
            <p className="text-[11px] text-text-secondary">
              Auto-detects models enabled on your Google AI Studio key via <code className="font-mono">ListModels</code> to avoid 404 version mismatch.
            </p>
          </div>
        </div>
      </div>

      {/* Inference & Thresholds */}
      <div className="p-6 rounded-2xl bg-white dark:bg-midnight border border-card-border shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-midnight dark:text-white">Inference &amp; Speech</h3>
          <span className="text-[11px] font-semibold text-teal-deep dark:text-seafoam flex items-center gap-1">
            <CheckCircleIcon className="w-3.5 h-3.5" />
            Auto-saved
          </span>
        </div>
        <div className="space-y-4">
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-semibold">
              <label htmlFor="threshold-slider" className="text-text-secondary">
                Confidence Threshold Gate
              </label>
              <span className="font-mono text-teal-deep dark:text-seafoam font-bold text-sm">{threshold}%</span>
            </div>
            <input
              id="threshold-slider"
              type="range"
              min="30"
              max="95"
              step="5"
              value={threshold}
              onChange={(e) => {
                const val = parseInt(e.target.value, 10);
                setThreshold(val);
                setManualGate(true);
                localStorage.setItem("sb_threshold", val.toString());
                window.dispatchEvent(new Event("storage"));
              }}
              className="w-full accent-teal-deep cursor-pointer"
            />
            <p className="text-[11px] text-text-secondary">
              {manualGate ? (
                <>
                  Predictions with confidence below <strong className="text-midnight dark:text-white font-mono">{threshold}%</strong> are flagged as &ldquo;Uncertain&rdquo; and excluded from confirmation.
                </>
              ) : (
                <>
                  Automatic mode: backend-calibrated thresholds decide acceptance. Move the slider to set a manual override.
                </>
              )}
            </p>
            <p className="text-[11px] text-text-secondary" data-testid="server-threshold-note">
              Server accept threshold: 0.57 (model policy). Predictions below this appear as Provisional and are never auto-added; your slider can only add a stricter personal gate on top.
            </p>
          </div>

          <div className="flex items-center justify-between pt-3 border-t border-card-border/60">
            <div>
              <p className="text-sm font-semibold text-midnight dark:text-white">Auto Speak Predictions</p>
              <p className="text-xs text-text-secondary">Automatically speak confirmed signs out loud through speaker.</p>
            </div>
            <input
              type="checkbox"
              checked={autoSpeak}
              onChange={(e) => {
                const val = e.target.checked;
                setAutoSpeak(val);
                localStorage.setItem("sb_autospeak", val.toString());
                window.dispatchEvent(new Event("storage"));
              }}
              className="w-5 h-5 accent-teal-deep rounded cursor-pointer"
            />
          </div>
        </div>
      </div>

      {/* Appearance */}
      <div className="p-6 rounded-2xl bg-white dark:bg-midnight border border-card-border shadow-xs space-y-5">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-midnight dark:text-white">Theme &amp; Appearance</h3>
          <span className="text-xs text-text-secondary font-medium">Personalize visual comfort</span>
        </div>

        {/* Mode Selector */}
        <div>
          <label className="text-xs font-semibold text-text-secondary mb-2 block">Display Mode</label>
          <div className="flex gap-3">
            {(["light", "dark", "system"] as const).map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => onThemeChange(t)}
                className={`px-4 py-2 rounded-xl text-xs font-semibold capitalize transition ${
                  currentTheme === t
                    ? "bg-teal-deep text-white shadow-xs border border-seafoam/30"
                    : "bg-soft-surface dark:bg-midnight-light border border-card-border text-text-secondary hover:text-midnight dark:hover:text-white"
                }`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        {/* Accent Color Slider */}
        <div className="pt-3 border-t border-card-border/60 space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-xs font-semibold text-midnight dark:text-white flex items-center gap-2">
              <span>Accent Color Picker</span>
              <span
                className="w-4 h-4 rounded-full border-2 border-white dark:border-midnight-light inline-block shadow-xs transition-colors"
                style={{ backgroundColor: `hsl(${currentHue}, 70%, 50%)` }}
              ></span>
            </label>
            <div className="flex items-center gap-2.5">
              <span className="text-[11px] font-mono font-medium text-text-secondary">
                Hue: {currentHue}°
              </span>
              <button
                type="button"
                onClick={() => onHueChange?.(188)}
                className="text-[11px] text-seafoam hover:underline font-semibold"
              >
                Reset Default
              </button>
            </div>
          </div>

          {/* Rainbow Hue Slider */}
          <div className="relative flex items-center pt-1">
            <input
              type="range"
              min="0"
              max="360"
              value={currentHue}
              onChange={(e) => onHueChange?.(parseInt(e.target.value, 10))}
              className="w-full h-3 rounded-lg appearance-none cursor-pointer focus:outline-hidden"
              style={{
                background:
                  "linear-gradient(to right, #ef4444 0%, #f97316 14%, #eab308 28%, #22c55e 42%, #06b6d4 57%, #3b82f6 71%, #8b5cf6 85%, #ec4899 93%, #ef4444 100%)",
              }}
            />
          </div>

          {/* Preset Color Swatches */}
          <div className="flex items-center gap-2 pt-1 flex-wrap">
            <span className="text-[11px] text-text-secondary font-medium mr-1">Quick Presets:</span>
            {THEME_PRESETS.map((p) => (
              <button
                key={p.name}
                type="button"
                title={p.name}
                onClick={() => onHueChange?.(p.hue)}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-medium border transition ${
                  Math.abs(currentHue - p.hue) < 10
                    ? "border-teal-deep dark:border-seafoam bg-soft-surface dark:bg-midnight-light text-midnight dark:text-white font-bold shadow-2xs"
                    : "border-card-border/60 hover:border-card-border text-text-secondary bg-transparent"
                }`}
              >
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: p.color }}></span>
                <span>{p.name}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Help & Privacy */}
      <div className="p-6 rounded-2xl bg-soft-surface dark:bg-midnight border border-card-border space-y-3 shadow-xs">
        <h3 className="text-sm font-bold text-midnight dark:text-white">Accessibility &amp; Privacy Guidelines</h3>
        <ul className="text-xs text-text-secondary space-y-2 list-disc pl-4 leading-relaxed">
          <li>Allow camera access → Start recognition → review output → Speak aloud or provide feedback.</li>
          <li>Uncertain means low confidence — never treated as definitive confirmation.</li>
          <li>History entries can be deleted individually or purged at any time.</li>
          <li>Raw video is processed purely on-device via MediaPipe and is never sent to any server.</li>
          <li>High-stakes medical or legal translations should always be verified with a certified interpreter.</li>
        </ul>
      </div>
    </div>
  );
}
