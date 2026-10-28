import React, { useEffect, useState } from "react";
import { api, type ModelInfo } from "../api/client";
import { CameraIcon, SparklesIcon, BookOpenIcon, HistoryIcon, ArrowPathIcon, CheckCircleIcon } from "../components/Icons";

interface DashboardProps {
  onNavigate: (tab: "live" | "text-to-sign" | "history" | "vocab" | "admin" | "settings") => void;
  backendOnline: boolean;
}

export default function Dashboard({ onNavigate, backendOnline }: DashboardProps) {
  const [model, setModel] = useState<ModelInfo | null>(null);
  const [vocabCount, setVocabCount] = useState<number>(50);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [mRes, cRes] = await Promise.allSettled([api.model(), api.classes()]);
        if (mRes.status === "fulfilled" && mRes.value.success) {
          setModel(mRes.value.model);
        }
        if (cRes.status === "fulfilled" && cRes.value.success) {
          setVocabCount(cRes.value.count);
        }
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div className="space-y-8 animate-in fade-in duration-300 max-w-7xl mx-auto">
      {/* Welcoming Warm Banner */}
      <section className="rounded-2xl bg-white dark:bg-midnight border border-card-border p-7 sm:p-8 shadow-xs relative overflow-hidden">
        <div className="absolute right-0 top-0 bottom-0 w-80 bg-gradient-to-l from-seafoam-light/40 dark:from-seafoam/10 to-transparent pointer-events-none"></div>
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-seafoam-light dark:bg-seafoam/20 border border-seafoam/30 text-teal-deep dark:text-seafoam text-xs font-semibold mb-3">
              <span className="w-2 h-2 rounded-full bg-seafoam animate-pulse"></span>
              Indian Sign Language Assistant
            </div>
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-midnight dark:text-white tracking-tight mb-2">
              Welcome to SignBridge AI
            </h1>
            <p className="text-text-secondary dark:text-slate-300 text-sm sm:text-base leading-relaxed">
              Your real-time translation workspace is ready. Translate Indian Sign Language (ISL) gestures to text and natural speech with sub-50ms neural inference.
            </p>
          </div>

          {/* CTAs */}
          <div className="flex items-center gap-3 shrink-0 flex-wrap">
            <button
              type="button"
              onClick={() => onNavigate("live")}
              className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-teal-deep hover:bg-deep-teal-hover text-white font-semibold text-sm transition-all shadow-xs"
            >
              <CameraIcon className="w-5 h-5 text-seafoam" />
              <span>Start Live Translation</span>
            </button>
            <button
              type="button"
              onClick={() => onNavigate("text-to-sign")}
              className="inline-flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-soft-surface dark:bg-midnight-light hover:bg-[#eae6dc] dark:hover:bg-[#253f54] border border-card-border text-midnight dark:text-white font-medium text-sm transition-colors"
            >
              <SparklesIcon className="w-5 h-5 text-text-secondary dark:text-seafoam" />
              <span>Text to Sign</span>
            </button>
            <button
              type="button"
              onClick={() => onNavigate("vocab")}
              className="inline-flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-soft-surface dark:bg-midnight-light hover:bg-[#eae6dc] dark:hover:bg-[#253f54] border border-card-border text-midnight dark:text-white font-medium text-sm transition-colors"
            >
              <BookOpenIcon className="w-5 h-5 text-text-secondary dark:text-slate-300" />
              <span>Browse Signs</span>
            </button>
          </div>
        </div>
      </section>

      {/* 4 Essential Metric Cards */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Card 1: Supported Signs */}
        <div className="bg-white dark:bg-midnight rounded-xl border border-card-border p-5 flex flex-col justify-between shadow-xs">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-text-secondary uppercase tracking-wider">Supported Signs</span>
            <div className="w-8 h-8 rounded-lg bg-soft-surface dark:bg-midnight-light border border-card-border flex items-center justify-center text-teal-deep dark:text-seafoam">
              <span className="material-symbols-outlined text-lg">sign_language</span>
            </div>
          </div>
          <div>
            <p className="text-2xl font-bold text-midnight dark:text-white">{vocabCount || 109} Classes</p>
            <p className="text-xs text-text-secondary mt-1">Curated dynamic ISL vocabulary</p>
          </div>
          <div className="pt-3 mt-3 border-t border-card-border/60 flex items-center justify-between text-xs text-text-secondary">
            <span>Photo Coverage</span>
            <span className="font-semibold text-teal-deep dark:text-seafoam">100% verified</span>
          </div>
        </div>

        {/* Card 2: Engine State */}
        <div className="bg-white dark:bg-midnight rounded-xl border border-card-border p-5 flex flex-col justify-between shadow-xs">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-text-secondary uppercase tracking-wider">Engine State</span>
            <span
              className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                backendOnline
                  ? "bg-seafoam-light text-teal-deep border border-seafoam/30"
                  : "bg-rose-50 text-rose-700 border border-rose-200"
              }`}
            >
              <span className={`w-1.5 h-1.5 rounded-full ${backendOnline ? "bg-seafoam animate-pulse" : "bg-rose-500"}`}></span>
              {backendOnline ? "Ready" : "Offline"}
            </span>
          </div>
          <div>
            <p className="text-2xl font-bold text-midnight dark:text-white">
              {backendOnline ? "FastAPI Online" : "Engine Offline"}
            </p>
            <p className="text-xs text-text-secondary mt-1">127.0.0.1:8000 • WebSocket + REST</p>
          </div>
          <div className="pt-3 mt-3 border-t border-card-border/60 flex items-center justify-between text-xs text-text-secondary">
            <span>Rate Limit</span>
            <span className="font-semibold font-mono text-midnight dark:text-white">120/min open</span>
          </div>
        </div>

        {/* Card 3: Neural Architecture */}
        <div className="bg-white dark:bg-midnight rounded-xl border border-card-border p-5 flex flex-col justify-between shadow-xs">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-text-secondary uppercase tracking-wider">Model Architecture</span>
            <div className="w-8 h-8 rounded-lg bg-soft-surface dark:bg-midnight-light border border-card-border flex items-center justify-center text-teal-deep dark:text-seafoam">
              <span className="material-symbols-outlined text-lg">memory</span>
            </div>
          </div>
          <div>
            <p className="text-lg font-bold text-midnight dark:text-white truncate" title={model?.model_version || "SBAI-MDL-ISL-2.0.0"}>
              {model?.model_version || "SBAI-MDL-ISL-2.0.0"}
            </p>
            <p className="text-xs text-text-secondary mt-1 truncate" title={model?.architecture || "LSTM128-LSTM64-Dense64"}>
              {model?.architecture || "LSTM128-LSTM64-Dense64"}
            </p>
          </div>
          <div className="pt-3 mt-3 border-t border-card-border/60 flex items-center justify-between text-xs text-text-secondary">
            <span>Input Shape</span>
            <span className="font-semibold font-mono text-midnight dark:text-white">{model?.seq_len || 45}f × {model?.feat_dim || 189}d</span>
          </div>
        </div>

        {/* Card 4: Inference Latency */}
        <div className="bg-white dark:bg-midnight rounded-xl border border-card-border p-5 flex flex-col justify-between shadow-xs">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-text-secondary uppercase tracking-wider">Latency Budget</span>
            <div className="w-8 h-8 rounded-lg bg-soft-surface dark:bg-midnight-light border border-card-border flex items-center justify-center text-teal-deep dark:text-seafoam">
              <span className="material-symbols-outlined text-lg">bolt</span>
            </div>
          </div>
          <div>
            <p className="text-2xl font-bold text-midnight dark:text-white">&lt; 35 ms</p>
            <p className="text-xs text-text-secondary mt-1">Real-time on-device client + edge server</p>
          </div>
          <div className="pt-3 mt-3 border-t border-card-border/60 flex items-center justify-between text-xs text-text-secondary">
            <span>Target FPS</span>
            <span className="font-semibold text-teal-deep dark:text-seafoam">30 FPS Live</span>
          </div>
        </div>
      </section>


      {/* Featured 109-Sign Photo Showcase */}
      <section className="p-6 sm:p-7 rounded-2xl bg-white dark:bg-midnight border border-card-border shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
          <div>
            <h3 className="text-lg font-bold text-midnight dark:text-white flex items-center gap-2">
              <span className="material-symbols-outlined text-teal-deep dark:text-seafoam text-xl">menu_book</span>
              <span>ISL Reference Sign Photos</span>
            </h3>
            <p className="text-xs text-text-secondary mt-0.5">
              High-resolution demonstration keyframes captured for active dynamic vocabulary classes.
            </p>
          </div>
          <button
            type="button"
            onClick={() => onNavigate("vocab")}
            className="text-xs font-semibold text-teal-deep dark:text-seafoam hover:underline flex items-center gap-1 self-start sm:self-auto"
          >
            <span>Browse All {vocabCount || 109} Signs</span>
            <span className="material-symbols-outlined text-sm">arrow_forward</span>
          </button>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 pt-2">
          {[
            { id: "ISL_001", label: "Hello", category: "Greeting" },
            { id: "ISL_002", label: "Thank You", category: "Gratitude" },
            { id: "ISL_003", label: "Please", category: "Polite" },
            { id: "ISL_011", label: "Help", category: "Emergency" },
            { id: "ISL_012", label: "Water", category: "Daily Need" },
            { id: "ISL_017", label: "Doctor", category: "Medical" },
            { id: "ISL_022", label: "Happy", category: "Emotion" },
            { id: "ISL_028", label: "School", category: "Place" },
            { id: "ISL_051", label: "Good", category: "Adjective" },
            { id: "ISL_062", label: "Pain", category: "Medical" },
            { id: "ISL_063", label: "Road", category: "Transport" },
            { id: "ISL_069", label: "Yesterday", category: "Time" },
          ].map((item) => (
            <div
              key={item.id}
              onClick={() => onNavigate("vocab")}
              className="group cursor-pointer rounded-xl border border-card-border bg-soft-surface dark:bg-midnight-light p-2.5 hover:border-teal-deep dark:hover:border-seafoam transition text-center space-y-2 shadow-2xs"
            >
              <div className="aspect-[4/3] w-full rounded-lg overflow-hidden bg-white dark:bg-midnight relative border border-card-border/60">
                <img
                  src={`/assets/${item.id}.jpg`}
                  alt={`${item.label} ISL sign`}
                  loading="lazy"
                  className="w-full h-24 object-cover group-hover:scale-105 transition-transform duration-300"
                  onError={(e) => {
                    (e.target as HTMLElement).style.display = "none";
                  }}
                />
              </div>
              <div>
                <span className="font-semibold text-xs text-midnight dark:text-white block group-hover:text-teal-deep dark:group-hover:text-seafoam transition-colors truncate">
                  {item.label}
                </span>
                <span className="text-[10px] text-text-secondary font-mono">
                  {item.id} • {item.category}
                </span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Interactive Quick-Action Cards */}
      <section className="space-y-4">
        <h2 className="text-xl font-bold text-midnight dark:text-white tracking-tight">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button
            type="button"
            onClick={() => onNavigate("live")}
            className="p-5 rounded-2xl bg-white dark:bg-midnight border border-card-border hover:border-teal-deep dark:hover:border-seafoam shadow-xs text-left transition group space-y-3"
          >
            <div className="w-10 h-10 rounded-xl bg-seafoam-light dark:bg-seafoam/20 text-teal-deep dark:text-seafoam flex items-center justify-center group-hover:scale-105 transition-transform">
              <CameraIcon className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-midnight dark:text-white text-base group-hover:text-teal-deep dark:group-hover:text-seafoam transition-colors">
                Live Sign Recognition
              </h3>
              <p className="text-xs text-text-secondary mt-1 leading-relaxed">
                Point your webcam, perform ISL signs, and receive instant text & speech outputs.
              </p>
            </div>
          </button>

          <button
            type="button"
            onClick={() => onNavigate("text-to-sign")}
            className="p-5 rounded-2xl bg-white dark:bg-midnight border border-card-border hover:border-teal-deep dark:hover:border-seafoam shadow-xs text-left transition group space-y-3"
          >
            <div className="w-10 h-10 rounded-xl bg-seafoam-light dark:bg-seafoam/20 text-teal-deep dark:text-seafoam flex items-center justify-center group-hover:scale-105 transition-transform">
              <SparklesIcon className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-midnight dark:text-white text-base group-hover:text-teal-deep dark:group-hover:text-seafoam transition-colors">
                Text & Voice to Sign
              </h3>
              <p className="text-xs text-text-secondary mt-1 leading-relaxed">
                Speak or type sentences to convert them into structured sign sequence cards.
              </p>
            </div>
          </button>

          <button
            type="button"
            onClick={() => onNavigate("history")}
            className="p-5 rounded-2xl bg-white dark:bg-midnight border border-card-border hover:border-teal-deep dark:hover:border-seafoam shadow-xs text-left transition group space-y-3"
          >
            <div className="w-10 h-10 rounded-xl bg-soft-surface dark:bg-midnight-light border border-card-border text-amber-muted flex items-center justify-center group-hover:scale-105 transition-transform">
              <HistoryIcon className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-midnight dark:text-white text-base group-hover:text-teal-deep dark:group-hover:text-seafoam transition-colors">
                Session History & Logs
              </h3>
              <p className="text-xs text-text-secondary mt-1 leading-relaxed">
                Review past recognitions, filter by confidence, and export session logs to CSV or JSON.
              </p>
            </div>
          </button>

          <button
            type="button"
            onClick={() => onNavigate("vocab")}
            className="p-5 rounded-2xl bg-white dark:bg-midnight border border-card-border hover:border-teal-deep dark:hover:border-seafoam shadow-xs text-left transition group space-y-3"
          >
            <div className="w-10 h-10 rounded-xl bg-soft-surface dark:bg-midnight-light border border-card-border text-teal-deep dark:text-seafoam flex items-center justify-center group-hover:scale-105 transition-transform">
              <BookOpenIcon className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-midnight dark:text-white text-base group-hover:text-teal-deep dark:group-hover:text-seafoam transition-colors">
                Vocabulary Explorer
              </h3>
              <p className="text-xs text-text-secondary mt-1 leading-relaxed">
                Search all registered dynamic ISL sign classes with reference demonstration photos.
              </p>
            </div>
          </button>
        </div>
      </section>

      {/* System Pipeline Architecture */}
      <section className="p-6 md:p-8 rounded-2xl bg-white dark:bg-midnight border border-card-border shadow-xs space-y-5">
        <h2 className="text-lg font-bold text-midnight dark:text-white flex items-center gap-2">
          <span>End-to-End Deterministic Pipeline</span>
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl bg-soft-surface dark:bg-midnight-light border border-card-border space-y-2">
            <span className="text-xs font-mono font-bold text-teal-deep dark:text-seafoam">Step 1 • Vision</span>
            <h4 className="font-bold text-midnight dark:text-white text-sm">MediaPipe Vision</h4>
            <p className="text-xs text-text-secondary leading-relaxed">
              Webcam video frames are processed locally inside the browser. 21 hand landmarks per hand are extracted.
            </p>
          </div>
          <div className="p-4 rounded-xl bg-soft-surface dark:bg-midnight-light border border-card-border space-y-2">
            <span className="text-xs font-mono font-bold text-teal-deep dark:text-seafoam">Step 2 • Buffer</span>
            <h4 className="font-bold text-midnight dark:text-white text-sm">45 × 189 Features</h4>
            <p className="text-xs text-text-secondary leading-relaxed">
              A 45-frame rolling window accumulates normalized coordinates, gated by the no-sign energy detector.
            </p>
          </div>
          <div className="p-4 rounded-xl bg-soft-surface dark:bg-midnight-light border border-card-border space-y-2">
            <span className="text-xs font-mono font-bold text-teal-deep dark:text-seafoam">Step 3 • Neural</span>
            <h4 className="font-bold text-midnight dark:text-white text-sm">FastAPI Inference</h4>
            <p className="text-xs text-text-secondary leading-relaxed">
              Keras LSTM / GRU neural model classifies the gesture sequence across 109 classes within 50 ms.
            </p>
          </div>
          <div className="p-4 rounded-xl bg-soft-surface dark:bg-midnight-light border border-card-border space-y-2">
            <span className="text-xs font-mono font-bold text-teal-deep dark:text-seafoam">Step 4 • Voice</span>
            <h4 className="font-bold text-midnight dark:text-white text-sm">Text & Speech</h4>
            <p className="text-xs text-text-secondary leading-relaxed">
              Results are surfaced instantly, spoken via speech synthesis, and logged to session history.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

