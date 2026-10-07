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
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-brand-950 to-slate-900 text-white p-8 md:p-12 shadow-2xl border border-slate-800 ai-glow">
        <div className="absolute top-0 right-0 w-96 h-96 bg-brand-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20"></div>
        <div className="absolute bottom-0 left-1/3 w-80 h-80 bg-isl-teal/10 rounded-full blur-3xl pointer-events-none"></div>

        <div className="relative z-10 max-w-3xl space-y-5">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-bold bg-brand-500/20 text-brand-300 border border-brand-500/30 backdrop-blur-md">
            <span className="w-2 h-2 rounded-full bg-brand-400 animate-pulse"></span>
            INDIAN SIGN LANGUAGE • BIDIRECTIONAL AI
          </div>
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-black tracking-tight leading-tight">
            Bridging Worlds Through <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-300 via-isl-cyan to-brand-400">Indian Sign Language</span> & AI
          </h1>
          <p className="text-slate-300 text-base md:text-lg leading-relaxed max-w-2xl font-normal">
            Real-time on-device computer vision and deterministic deep learning translation between Indian Sign Language (ISL), text, and synthesized speech.
          </p>
          <div className="flex flex-wrap gap-4 pt-3">
            <button
              type="button"
              onClick={() => onNavigate("live")}
              className="inline-flex items-center gap-2.5 px-6 py-3.5 rounded-xl bg-gradient-to-r from-brand-500 to-brand-600 hover:from-brand-600 hover:to-brand-700 text-white font-bold shadow-lg shadow-brand-500/25 transition-all hover:shadow-brand-500/40 hover:-translate-y-0.5"
            >
              <CameraIcon className="w-5 h-5" />
              Start Live Camera Translation
            </button>
            <button
              type="button"
              onClick={() => onNavigate("text-to-sign")}
              className="inline-flex items-center gap-2.5 px-6 py-3.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 text-white font-semibold border border-slate-700 shadow-md backdrop-blur-md transition-all hover:-translate-y-0.5"
            >
              <SparklesIcon className="w-5 h-5 text-brand-300" />
              Text & Voice to Sign
            </button>
            <button
              type="button"
              onClick={() => onNavigate("vocab")}
              className="inline-flex items-center gap-2.5 px-6 py-3.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 text-white font-semibold border border-slate-700 shadow-md backdrop-blur-md transition-all hover:-translate-y-0.5"
            >
              <BookOpenIcon className="w-5 h-5 text-isl-teal" />
              Explore Vocabulary
            </button>
          </div>
        </div>
      </div>

      {/* Metrics & Status Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Backend Status Card */}
        <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm hover:shadow-md transition space-y-4">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider">
            <span>FastAPI Backend Engine</span>
            <span
              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold ${
                backendOnline
                  ? "bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800/60"
                  : "bg-rose-50 dark:bg-rose-950/60 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-800/60"
              }`}
            >
              <span
                className={`w-2 h-2 rounded-full ${
                  backendOnline ? "bg-emerald-500 animate-pulse" : "bg-rose-500"
                }`}
              ></span>
              {backendOnline ? "Online & Healthy" : "Offline"}
            </span>
          </div>
          <div>
            <p className="text-2xl font-black text-slate-900 dark:text-white">
              {backendOnline ? "127.0.0.1:8000" : "Disconnected"}
            </p>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Serving inference, session management, and speech endpoints.
            </p>
          </div>
          <div className="pt-2 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between text-xs text-slate-500">
            <span>Rate Limit Tier:</span>
            <span className="font-mono font-semibold text-slate-700 dark:text-slate-300">120/min open</span>
          </div>
        </div>

        {/* Model Card */}
        <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm hover:shadow-md transition space-y-4">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider">
            <span>Production Neural Model</span>
            <span className="text-xs font-mono font-bold text-brand-600 dark:text-brand-400 bg-brand-50 dark:bg-brand-950/80 px-2 py-0.5 rounded">
              {model?.model_version || "SBAI-MDL-ISL-1.0.0"}
            </span>
          </div>
          <div>
            <p className="text-2xl font-black text-slate-900 dark:text-white">
              {model?.model_id || "signbridge-gru-v1"}
            </p>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Window: 45 frames × 189 landmarks. GRU128-GRU64-Dense64-Softmax50.
            </p>
          </div>
          <div className="pt-2 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between text-xs text-slate-500">
            <span>Inference Latency:</span>
            <span className="font-mono font-semibold text-emerald-600 dark:text-emerald-400">~20-50 ms</span>
          </div>
        </div>

        {/* Vocabulary Card */}
        <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm hover:shadow-md transition space-y-4 sm:col-span-2 lg:col-span-1">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider">
            <span>ISL Vocabulary</span>
            <span className="text-xs font-mono font-bold text-isl-teal bg-emerald-50 dark:bg-emerald-950/80 px-2 py-0.5 rounded">
              MVP-50
            </span>
          </div>
          <div>
            <p className="text-2xl font-black text-slate-900 dark:text-white">
              {vocabCount} Classes
            </p>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              30 Everyday Words + 10 Digits (0-9) + 10 Alphabet Signs (A-J).
            </p>
          </div>
          <div className="pt-2 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between text-xs text-slate-500">
            <span>Dictionary Coverage:</span>
            <span className="font-mono font-semibold text-brand-600 dark:text-brand-400">100% active</span>
          </div>
        </div>
      </div>

      {/* Interactive Quick-Action Cards */}
      <div className="space-y-4">
        <h2 className="text-xl font-bold text-slate-900 dark:text-white">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button
            type="button"
            onClick={() => onNavigate("live")}
            className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-brand-500 dark:hover:border-brand-500 shadow-xs hover:shadow-md text-left transition group space-y-3"
          >
            <div className="w-10 h-10 rounded-xl bg-brand-50 dark:bg-brand-950/60 text-brand-600 dark:text-brand-400 flex items-center justify-center group-hover:scale-110 transition-transform">
              <CameraIcon className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900 dark:text-white text-base group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors">
                Live Sign Recognition
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                Point your webcam, perform ISL signs, and receive instant text & speech outputs.
              </p>
            </div>
          </button>

          <button
            type="button"
            onClick={() => onNavigate("text-to-sign")}
            className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-brand-500 dark:hover:border-brand-500 shadow-xs hover:shadow-md text-left transition group space-y-3"
          >
            <div className="w-10 h-10 rounded-xl bg-isl-teal/10 text-isl-teal flex items-center justify-center group-hover:scale-110 transition-transform">
              <SparklesIcon className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900 dark:text-white text-base group-hover:text-isl-teal transition-colors">
                Text & Voice to Sign
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                Speak or type sentences to convert them into structured sign sequence cards.
              </p>
            </div>
          </button>

          <button
            type="button"
            onClick={() => onNavigate("history")}
            className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-brand-500 dark:hover:border-brand-500 shadow-xs hover:shadow-md text-left transition group space-y-3"
          >
            <div className="w-10 h-10 rounded-xl bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400 flex items-center justify-center group-hover:scale-110 transition-transform">
              <HistoryIcon className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900 dark:text-white text-base group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors">
                Session History & Export
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                Review past recognitions, filter by confidence, and export session logs to CSV or JSON.
              </p>
            </div>
          </button>

          <button
            type="button"
            onClick={() => onNavigate("vocab")}
            className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-brand-500 dark:hover:border-brand-500 shadow-xs hover:shadow-md text-left transition group space-y-3"
          >
            <div className="w-10 h-10 rounded-xl bg-purple-50 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400 flex items-center justify-center group-hover:scale-110 transition-transform">
              <BookOpenIcon className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900 dark:text-white text-base group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors">
                Vocabulary Explorer
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                Search all 50 registered sign classes across words, numbers, and alphabet letters.
              </p>
            </div>
          </button>
        </div>
      </div>

      {/* System Pipeline Architecture */}
      <div className="p-6 md:p-8 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-5">
        <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <span>End-to-End Deterministic Pipeline</span>
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800 space-y-2">
            <span className="text-xs font-mono font-bold text-brand-600 dark:text-brand-400">Step 1 • Edge</span>
            <h4 className="font-bold text-slate-900 dark:text-white text-sm">MediaPipe Vision</h4>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Webcam video frames are processed locally inside the browser. 21 hand landmarks per hand are extracted.
            </p>
          </div>
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800 space-y-2">
            <span className="text-xs font-mono font-bold text-brand-600 dark:text-brand-400">Step 2 • Buffer</span>
            <h4 className="font-bold text-slate-900 dark:text-white text-sm">45 × 189 Features</h4>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              A 45-frame rolling window accumulates normalized coordinates, gated by the no-sign energy detector.
            </p>
          </div>
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800 space-y-2">
            <span className="text-xs font-mono font-bold text-brand-600 dark:text-brand-400">Step 3 • AI</span>
            <h4 className="font-bold text-slate-900 dark:text-white text-sm">FastAPI Inference</h4>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Keras GRU neural model classifies the gesture sequence and returns confidence scores within 50 ms.
            </p>
          </div>
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800 space-y-2">
            <span className="text-xs font-mono font-bold text-brand-600 dark:text-brand-400">Step 4 • Voice</span>
            <h4 className="font-bold text-slate-900 dark:text-white text-sm">Text & Speech</h4>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Results are surfaced instantly, spoken via speech synthesis, and logged to session history.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
