import React, { useState } from "react";
import { api, setToken as saveToken } from "../api/client";
import { CogIcon, CheckCircleIcon, AlertCircleIcon } from "../components/Icons";
import {
  getGeminiModelName,
  setGeminiModelName,
  listAvailableGeminiModels,
  interpretSignSequence,
  CANDIDATE_MODELS,
} from "../api/gemini";

interface SettingsProps {
  currentTheme: "dark" | "light" | "system";
  onThemeChange: (theme: "dark" | "light" | "system") => void;
}

export default function Settings({ currentTheme, onThemeChange }: SettingsProps) {
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
    return val ? parseInt(val, 10) : 70;
  });
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
    localStorage.setItem("sb_threshold", threshold.toString());
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
    <div className="space-y-8 max-w-3xl animate-in fade-in duration-200">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <CogIcon className="w-6 h-6 text-brand-600 dark:text-brand-400" />
          System Settings & Preferences
        </h2>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Configure API connection endpoints, authentication credentials, and interface options.
        </p>
      </div>

      {/* Backend & Connection */}
      <div className="p-6 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
        <h3 className="text-base font-bold text-slate-900 dark:text-white">Backend Connection</h3>
        <div className="space-y-2">
          <label htmlFor="api-base-input" className="block text-xs font-semibold uppercase text-slate-500 dark:text-slate-400">
            API Base Endpoint
          </label>
          <div className="flex gap-3">
            <input
              id="api-base-input"
              type="text"
              readOnly
              value={import.meta.env.VITE_API_BASE || "http://localhost:8000"}
              className="flex-1 px-4 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm font-mono text-slate-700 dark:text-slate-300"
            />
            <button
              type="button"
              onClick={testConnection}
              disabled={testingConnection}
              className="px-4 py-2.5 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-xs font-semibold text-slate-700 dark:text-slate-200 transition"
            >
              {testingConnection ? "Testing…" : "Test Connection"}
            </button>
          </div>
          {connectionStatus && (
            <p className={`text-xs font-medium mt-1 ${connectionStatus.includes("Connected") ? "text-emerald-600 dark:text-emerald-400" : "text-rose-600 dark:text-rose-400"}`}>
              {connectionStatus}
            </p>
          )}
        </div>
      </div>

      {/* Authentication Token */}
      <div className="p-6 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
        <h3 className="text-base font-bold text-slate-900 dark:text-white">Backend Authentication</h3>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Guarded endpoints (predict, sessions, TTS, admin) validate this Bearer token against the backend secret.
        </p>
        <div className="space-y-2">
          <label htmlFor="token-input" className="block text-xs font-semibold uppercase text-slate-500 dark:text-slate-400">
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
              className="flex-1 px-4 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm font-mono text-slate-900 dark:text-white focus:ring-2 focus:ring-brand-500"
            />
            <button
              type="button"
              onClick={() => setShowToken(!showToken)}
              className="px-3 py-2 text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
            >
              {showToken ? "Hide" : "Show"}
            </button>
            <button
              type="button"
              onClick={handleSaveToken}
              className="px-5 py-2.5 rounded-lg bg-brand-600 hover:bg-brand-700 text-white font-semibold text-xs transition"
            >
              Save
            </button>
          </div>
          {saved && (
            <p role="status" className="text-xs text-emerald-600 dark:text-emerald-400 font-medium flex items-center gap-1 mt-1">
              <CheckCircleIcon className="w-4 h-4" />
              Settings saved locally.
            </p>
          )}
        </div>
      </div>

      {/* Gemini Natural Language Interpretation */}
      <div className="p-6 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <span>Gemini AI (Sentence Interpretation)</span>
          </h3>
          <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-brand-100 dark:bg-brand-950 text-brand-700 dark:text-brand-300">
            Natural English
          </span>
        </div>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Used to interpret accumulated ISL sign sequences (e.g. &ldquo;GO WATER DRINK&rdquo;) into coherent English sentences (e.g. &ldquo;I am going to drink water.&rdquo;).
        </p>
        <div className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="gemini-key-input" className="block text-xs font-semibold uppercase text-slate-500 dark:text-slate-400">
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
                className="flex-1 px-4 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm font-mono text-slate-900 dark:text-white focus:ring-2 focus:ring-brand-500"
              />
              <button
                type="button"
                onClick={() => setShowGeminiKey(!showGeminiKey)}
                className="px-3 py-2 text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
              >
                {showGeminiKey ? "Hide" : "Show"}
              </button>
              <button
                type="button"
                onClick={handleSaveGeminiKey}
                className="px-5 py-2.5 rounded-lg bg-brand-600 hover:bg-brand-700 text-white font-semibold text-xs transition"
              >
                Save Key
              </button>
            </div>
            {geminiSaved && (
              <p role="status" className="text-xs text-emerald-600 dark:text-emerald-400 font-medium flex items-center gap-1 mt-1">
                <CheckCircleIcon className="w-4 h-4" />
                Gemini API key saved locally.
              </p>
            )}
            <p className="text-[11px] text-slate-400">
              Stored in your browser&apos;s localStorage (<code className="font-mono">sb_gemini_api_key</code>) or loaded from <code className="font-mono">VITE_GEMINI_API_KEY</code>. Never committed or sent to the backend.
            </p>
          </div>

          {/* Model Selection & Auto-Discovery */}
          <div className="pt-2 border-t border-slate-100 dark:border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <label htmlFor="gemini-model-select" className="block text-xs font-semibold uppercase text-slate-500 dark:text-slate-400">
                Gemini Model
              </label>
              <span className="text-[11px] text-slate-400">
                Active: <strong className="text-slate-700 dark:text-slate-200 font-mono">{geminiModel}</strong>
              </span>
            </div>
            <div className="flex gap-2">
              <select
                id="gemini-model-select"
                value={geminiModel}
                onChange={(e) => handleModelChange(e.target.value)}
                className="flex-1 px-4 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm font-medium text-slate-900 dark:text-white focus:ring-2 focus:ring-brand-500"
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
                className="px-4 py-2.5 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-xs font-semibold text-slate-700 dark:text-slate-200 transition disabled:opacity-50"
              >
                {detectingModels ? "Detecting…" : "Auto-Detect Models"}
              </button>
              <button
                type="button"
                onClick={handleTestGemini}
                disabled={testingGemini}
                className="px-4 py-2.5 rounded-lg bg-brand-50 dark:bg-brand-950/60 border border-brand-200 dark:border-brand-800 hover:bg-brand-100 dark:hover:bg-brand-900/60 text-xs font-semibold text-brand-700 dark:text-brand-300 transition disabled:opacity-50"
              >
                {testingGemini ? "Testing…" : "Test API"}
              </button>
            </div>
            {geminiTestResult && (
              <div
                className={`p-3 rounded-lg text-xs font-medium flex items-start gap-2 mt-2 ${
                  geminiTestResult.success
                    ? "bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800"
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
            <p className="text-[11px] text-slate-400">
              Auto-detects models enabled on your Google AI Studio key via <code className="font-mono">ListModels</code> to avoid 404 version mismatch.
            </p>
          </div>
        </div>
      </div>

      {/* Inference & Thresholds */}
      <div className="p-6 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-slate-900 dark:text-white">Inference & Speech</h3>
          <span className="text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
            <CheckCircleIcon className="w-3.5 h-3.5" />
            Auto-saved
          </span>
        </div>
        <div className="space-y-4">
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-semibold">
              <label htmlFor="threshold-slider" className="text-slate-700 dark:text-slate-300">
                Confidence Threshold Gate
              </label>
              <span className="font-mono text-brand-600 dark:text-brand-400 font-bold text-sm">{threshold}%</span>
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
                localStorage.setItem("sb_threshold", val.toString());
                window.dispatchEvent(new Event("storage"));
              }}
              className="w-full accent-brand-600 cursor-pointer"
            />
            <p className="text-[11px] text-slate-400">
              Predictions with confidence below <strong className="text-slate-700 dark:text-slate-200 font-mono">{threshold}%</strong> are flagged as &ldquo;Uncertain&rdquo; and excluded from confirmation.
            </p>
          </div>

          <div className="flex items-center justify-between pt-3 border-t border-slate-100 dark:border-slate-800">
            <div>
              <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">Auto Speak Predictions</p>
              <p className="text-xs text-slate-400">Automatically speak confirmed signs out loud through speaker.</p>
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
              className="w-5 h-5 accent-brand-600 rounded cursor-pointer"
            />
          </div>
        </div>
      </div>

      {/* Appearance */}
      <div className="p-6 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
        <h3 className="text-base font-bold text-slate-900 dark:text-white">Theme & Appearance</h3>
        <div className="flex gap-3">
          {(["light", "dark", "system"] as const).map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => onThemeChange(t)}
              className={`px-4 py-2 rounded-lg text-xs font-semibold capitalize transition ${
                currentTheme === t
                  ? "bg-brand-600 text-white shadow-sm"
                  : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700"
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* Help & Privacy */}
      <div className="p-6 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 space-y-3">
        <h3 className="text-sm font-bold text-slate-900 dark:text-white">Accessibility & Privacy Guidelines</h3>
        <ul className="text-xs text-slate-600 dark:text-slate-400 space-y-2 list-disc pl-4">
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
