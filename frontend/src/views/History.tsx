import React, { useEffect, useState } from "react";
import { api, type Prediction } from "../api/client";
import {
  getSentenceHistory,
  deleteSentenceRecord,
  clearSentenceHistory,
  type SentenceRecord,
} from "../api/sentenceHistory";
import { type SentenceMood } from "../api/gemini";
import {
  HistoryIcon,
  TrashIcon,
  RefreshIcon,
  AlertCircleIcon,
  SparklesIcon,
  CheckCircleIcon,
  VolumeUpIcon,
} from "../components/Icons";
import ConfirmModal from "../components/ConfirmModal";

const MOOD_CONFIG: Record<
  SentenceMood,
  { emoji: string; label: string; badge: string; border: string; pitch: number; rate: number }
> = {
  normal: {
    emoji: "😐",
    label: "Normal",
    badge: "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-300 dark:border-slate-700",
    border: "border-slate-200 dark:border-slate-800",
    pitch: 1.0,
    rate: 1.0,
  },
  happy: {
    emoji: "😊",
    label: "Happy",
    badge: "bg-emerald-100 dark:bg-emerald-950/80 text-emerald-800 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800",
    border: "border-emerald-200 dark:border-emerald-900/60",
    pitch: 1.35,
    rate: 1.15,
  },
  sad: {
    emoji: "😔",
    label: "Sad",
    badge: "bg-blue-100 dark:bg-blue-950/80 text-blue-800 dark:text-blue-300 border-blue-300 dark:border-blue-800",
    border: "border-blue-200 dark:border-blue-900/60",
    pitch: 0.72,
    rate: 0.82,
  },
  angry: {
    emoji: "😠",
    label: "Angry",
    badge: "bg-rose-100 dark:bg-rose-950/80 text-rose-800 dark:text-rose-300 border-rose-300 dark:border-rose-800",
    border: "border-rose-200 dark:border-rose-900/60",
    pitch: 0.85,
    rate: 1.25,
  },
};

export default function History() {
  const [activeTab, setActiveTab] = useState<"sentences" | "rawWords">("sentences");
  const [sentences, setSentences] = useState<SentenceRecord[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedMoodFilter, setSelectedMoodFilter] = useState<string>("all");
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [speakingId, setSpeakingId] = useState<string | null>(null);
  const [clearModalOpen, setClearModalOpen] = useState(false);

  // Raw Word Predictions (Secondary Tab)
  const [rawItems, setRawItems] = useState<
    (Prediction & { status: string; timestamp?: number; created?: string })[]
  >([]);
  const [loadingRaw, setLoadingRaw] = useState(false);
  const [rawFilter, setRawFilter] = useState("all");

  function loadSentences() {
    setSentences(getSentenceHistory());
  }

  async function loadRawPredictions() {
    setLoadingRaw(true);
    try {
      const s = await api.sessions(100);
      const sessList = s.sessions || [];
      const activeSessions = sessList.filter((x) => (x.live_predictions || 0) > 0);
      const toFetch = (activeSessions.length > 0 ? activeSessions : sessList.slice(0, 10)).map(
        (x) => x.session_id
      );

      const all = await Promise.all(
        toFetch.map(async (id) => {
          try {
            const res = await api.sessionPredictions(id);
            return res.predictions || [];
          } catch {
            return [];
          }
        })
      );
      const flat = all.flat();
      flat.sort((a, b) => {
        const tA = a.created || "";
        const tB = b.created || "";
        return tB.localeCompare(tA);
      });
      setRawItems(flat);
    } catch {
      /* ignore */
    } finally {
      setLoadingRaw(false);
    }
  }

  useEffect(() => {
    loadSentences();
    const handleUpdate = () => loadSentences();
    window.addEventListener("sentence_history_updated", handleUpdate);
    window.addEventListener("storage", handleUpdate);
    return () => {
      window.removeEventListener("sentence_history_updated", handleUpdate);
      window.removeEventListener("storage", handleUpdate);
    };
  }, []);

  useEffect(() => {
    if (activeTab === "rawWords" && rawItems.length === 0) {
      loadRawPredictions();
    }
  }, [activeTab]);

  function speakSentence(id: string, text: string, mood: SentenceMood = "normal") {
    if (typeof window === "undefined" || !("speechSynthesis" in window) || !text.trim()) return;
    try {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = "en-IN";

      const cfg = MOOD_CONFIG[mood] || MOOD_CONFIG.normal;
      utterance.pitch = cfg.pitch;
      utterance.rate = cfg.rate;

      setSpeakingId(id);
      utterance.onend = () => setSpeakingId(null);
      utterance.onerror = () => setSpeakingId(null);
      window.speechSynthesis.speak(utterance);
    } catch {
      setSpeakingId(null);
    }
  }

  function handleCopy(id: string, text: string) {
    if (typeof navigator !== "undefined" && navigator.clipboard) {
      navigator.clipboard.writeText(text);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    }
  }

  function handleDelete(id: string) {
    deleteSentenceRecord(id);
    loadSentences();
  }

  function handleClearAll() {
    clearSentenceHistory();
    loadSentences();
    setClearModalOpen(false);
  }

  function exportSentencesJSON() {
    const dataStr =
      "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(sentences, null, 2));
    const dl = document.createElement("a");
    dl.setAttribute("href", dataStr);
    dl.setAttribute("download", `signbridge_sentences_${Date.now()}.json`);
    dl.click();
  }

  function exportSentencesCSV() {
    const headers = ["ID", "Sentence", "Signs", "Mood", "Timestamp", "Source"];
    const rows = sentences.map((s) => [
      s.id,
      `"${s.sentence.replace(/"/g, '""')}"`,
      `"${s.signs.join(" > ")}"`,
      s.mood,
      `"${s.timestamp}"`,
      s.source,
    ]);
    const csvContent =
      "data:text/csv;charset=utf-8," +
      [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
    const dl = document.createElement("a");
    dl.setAttribute("href", encodeURI(csvContent));
    dl.setAttribute("download", `signbridge_sentences_${Date.now()}.csv`);
    dl.click();
  }

  // Filtered sentences
  const filteredSentences = sentences.filter((s) => {
    const matchesSearch =
      searchTerm.trim() === "" ||
      s.sentence.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.signs.some((sign) => sign.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesMood = selectedMoodFilter === "all" || s.mood === selectedMoodFilter;
    return matchesSearch && matchesMood;
  });

  const totalSignsCount = sentences.reduce((acc, s) => acc + s.signs.length, 0);

  return (
    <div className="space-y-6 max-w-5xl animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <HistoryIcon className="w-6 h-6 text-brand-600 dark:text-brand-400" />
            Sentence Translation History
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Complete natural language sentences interpreted by AI from Indian Sign Language sequences.
          </p>
        </div>

        {/* View Switcher Tabs */}
        <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800/80 p-1 rounded-xl border border-slate-200 dark:border-slate-700/80 self-start sm:self-auto">
          <button
            type="button"
            onClick={() => setActiveTab("sentences")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition flex items-center gap-1.5 ${
              activeTab === "sentences"
                ? "bg-white dark:bg-slate-900 text-brand-600 dark:text-brand-400 shadow-sm"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
            }`}
          >
            <SparklesIcon className="w-3.5 h-3.5" />
            Complete Sentences ({sentences.length})
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("rawWords")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition flex items-center gap-1.5 ${
              activeTab === "rawWords"
                ? "bg-white dark:bg-slate-900 text-brand-600 dark:text-brand-400 shadow-sm"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
            }`}
          >
            <HistoryIcon className="w-3.5 h-3.5" />
            Raw Word Logs
          </button>
        </div>
      </div>

      {/* PRIMARY TAB: SENTENCE HISTORY */}
      {activeTab === "sentences" && (
        <div className="space-y-6">
          {/* Top Metrics Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold uppercase text-slate-400 tracking-wider">
                  Total Sentences
                </p>
                <p className="text-3xl font-extrabold text-slate-900 dark:text-white mt-1">
                  {sentences.length}
                </p>
              </div>
              <div className="w-10 h-10 rounded-xl bg-brand-50 dark:bg-brand-950/60 text-brand-600 dark:text-brand-400 flex items-center justify-center">
                <SparklesIcon className="w-5 h-5" />
              </div>
            </div>

            <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold uppercase text-slate-400 tracking-wider">
                  Signs Interpreted
                </p>
                <p className="text-3xl font-extrabold text-emerald-600 dark:text-emerald-400 mt-1">
                  {totalSignsCount}
                </p>
              </div>
              <div className="w-10 h-10 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
                <CheckCircleIcon className="w-5 h-5" />
              </div>
            </div>

            <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold uppercase text-slate-400 tracking-wider">
                  Voice Synthesis
                </p>
                <p className="text-xl font-bold text-slate-800 dark:text-slate-100 mt-1 flex items-center gap-1.5">
                  <span>🔊 4 Emotional Tones</span>
                </p>
              </div>
              <div className="w-10 h-10 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center">
                <VolumeUpIcon className="w-5 h-5" />
              </div>
            </div>
          </div>

          {/* Filter Bar & Export Actions */}
          <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
            <div className="flex-1 flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search sentences or signs (e.g. doctor, family, water)..."
                className="flex-1 px-3.5 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-brand-500"
              />
              <select
                value={selectedMoodFilter}
                onChange={(e) => setSelectedMoodFilter(e.target.value)}
                className="px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white text-sm"
              >
                <option value="all">All Moods</option>
                <option value="normal">😐 Normal Tone</option>
                <option value="happy">😊 Happy Tone</option>
                <option value="sad">😔 Sad Tone</option>
                <option value="angry">😠 Angry Tone</option>
              </select>
            </div>

            <div className="flex items-center gap-2 self-end sm:self-auto">
              <button
                type="button"
                onClick={exportSentencesCSV}
                className="px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 text-xs font-semibold text-slate-700 dark:text-slate-200 transition"
              >
                Export CSV
              </button>
              <button
                type="button"
                onClick={exportSentencesJSON}
                className="px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 text-xs font-semibold text-slate-700 dark:text-slate-200 transition"
              >
                Export JSON
              </button>
              {sentences.length > 0 && (
                <button
                  type="button"
                  onClick={() => setClearModalOpen(true)}
                  className="px-3 py-2 rounded-lg border border-rose-300 dark:border-rose-900/60 bg-rose-50 dark:bg-rose-950/40 hover:bg-rose-100 dark:hover:bg-rose-900/60 text-xs font-semibold text-rose-600 dark:text-rose-400 transition"
                >
                  Clear All
                </button>
              )}
            </div>
          </div>

          {/* Sentence Cards List */}
          {filteredSentences.length === 0 ? (
            <div className="p-12 text-center rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
              <SparklesIcon className="w-10 h-10 text-slate-300 dark:text-slate-600 mx-auto" />
              <p className="text-base font-semibold text-slate-700 dark:text-slate-200">
                No matching sentences found.
              </p>
              <p className="text-xs text-slate-400 max-w-md mx-auto">
                Perform signs in the Live Translator to accumulate sentence sequences, or translate phrases in Text to Sign to build your sentence history.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredSentences.map((rec) => {
                const moodCfg = MOOD_CONFIG[rec.mood] || MOOD_CONFIG.normal;
                const isSpeakingThis = speakingId === rec.id;

                return (
                  <div
                    key={rec.id}
                    className={`p-5 rounded-2xl bg-white dark:bg-slate-900 border ${moodCfg.border} shadow-sm transition hover:shadow-md space-y-3`}
                  >
                    {/* Top Row: Meta & Badges */}
                    <div className="flex items-center justify-between gap-2 flex-wrap">
                      <div className="flex items-center gap-2">
                        <span
                          className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${moodCfg.badge}`}
                        >
                          <span>{moodCfg.emoji}</span>
                          <span>{moodCfg.label} Tone</span>
                        </span>
                        <span className="text-xs text-slate-400 font-mono">
                          {rec.source === "live"
                            ? "🎥 Live Camera"
                            : rec.source === "text-to-sign"
                            ? "✍️ Text to Sign"
                            : "✨ Interpreted"}
                        </span>
                      </div>
                      <span className="text-xs text-slate-400 font-mono">{rec.timestamp}</span>
                    </div>

                    {/* Complete Sentence */}
                    <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800">
                      <p className="text-lg font-bold text-slate-900 dark:text-white leading-relaxed">
                        &ldquo;{rec.sentence}&rdquo;
                      </p>
                    </div>

                    {/* ISL Signs Sequence Pills */}
                    {rec.signs && rec.signs.length > 0 && (
                      <div className="flex items-center gap-1.5 flex-wrap pt-1">
                        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider mr-1">
                          Signs:
                        </span>
                        {rec.signs.map((sign, sIdx) => (
                          <React.Fragment key={`${rec.id}-sign-${sIdx}`}>
                            <span className="px-2.5 py-1 rounded-lg text-xs font-extrabold bg-brand-50 dark:bg-brand-950/60 text-brand-700 dark:text-brand-300 border border-brand-200 dark:border-brand-900/60 font-mono">
                              {sign}
                            </span>
                            {sIdx < rec.signs.length - 1 && (
                              <span className="text-slate-300 dark:text-slate-600 text-xs font-bold">
                                ➔
                              </span>
                            )}
                          </React.Fragment>
                        ))}
                      </div>
                    )}

                    {/* Bottom Action Row */}
                    <div className="flex items-center justify-between pt-2 border-t border-slate-100 dark:border-slate-800/80">
                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          onClick={() => speakSentence(rec.id, rec.sentence, rec.mood)}
                          className={`px-3 py-1.5 rounded-lg border text-xs font-semibold transition flex items-center gap-1.5 ${
                            isSpeakingThis
                              ? "bg-brand-600 text-white border-brand-600 animate-pulse"
                              : "bg-slate-100 dark:bg-slate-800 border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-700"
                          }`}
                        >
                          <VolumeUpIcon className="w-3.5 h-3.5" />
                          <span>{isSpeakingThis ? "Speaking…" : "Speak Sentence"}</span>
                        </button>

                        <button
                          type="button"
                          onClick={() => handleCopy(rec.id, rec.sentence)}
                          className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-xs font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition"
                        >
                          {copiedId === rec.id ? "✓ Copied!" : "Copy"}
                        </button>
                      </div>

                      <button
                        type="button"
                        onClick={() => handleDelete(rec.id)}
                        className="text-xs text-rose-500 hover:text-rose-700 dark:hover:text-rose-400 p-1.5 rounded-lg hover:bg-rose-50 dark:hover:bg-rose-950/40 transition flex items-center gap-1"
                        title="Delete sentence"
                      >
                        <TrashIcon className="w-3.5 h-3.5" />
                        <span className="hidden sm:inline">Delete</span>
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* SECONDARY TAB: RAW WORD PREDICTIONS (FOR DEVELOPER / MODEL DEBUGGING) */}
      {activeTab === "rawWords" && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-700 flex items-center justify-between text-xs text-slate-600 dark:text-slate-300">
            <span>
              Showing raw frame-by-frame sign detections from SQLite backend database.
            </span>
            <button
              type="button"
              onClick={loadRawPredictions}
              disabled={loadingRaw}
              className="px-3 py-1 rounded-md bg-white dark:bg-slate-700 border border-slate-300 dark:border-slate-600 font-semibold flex items-center gap-1"
            >
              <RefreshIcon className={`w-3.5 h-3.5 ${loadingRaw ? "animate-spin" : ""}`} />
              Reload
            </button>
          </div>

          <div className="overflow-hidden rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 dark:bg-slate-800/80 text-xs font-bold uppercase tracking-wider text-slate-500 border-b border-slate-200 dark:border-slate-800">
                <tr>
                  <th className="px-4 py-3">Sign Word</th>
                  <th className="px-4 py-3">Class ID</th>
                  <th className="px-4 py-3">Confidence</th>
                  <th className="px-4 py-3">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {rawItems.map((item, idx) => (
                  <tr key={item.prediction_id || idx} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/40">
                    <td className="px-4 py-3 font-bold text-slate-900 dark:text-white uppercase">
                      {item.label}
                    </td>
                    <td className="px-4 py-3 text-slate-400 font-mono text-xs">
                      {item.class_id}
                    </td>
                    <td className="px-4 py-3 font-semibold text-brand-600 dark:text-brand-400">
                      {Math.round(item.confidence * 100)}%
                    </td>
                    <td className="px-4 py-3 text-slate-400 text-xs font-mono">
                      {item.created || "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Confirmation Modal for Clearing Sentences */}
      <ConfirmModal
        isOpen={clearModalOpen}
        title="Clear Sentence History?"
        message="This will remove all recorded sentence translations from your history. This action cannot be undone."
        confirmLabel="Clear All Sentences"
        isDestructive
        onConfirm={handleClearAll}
        onCancel={() => setClearModalOpen(false)}
      />
    </div>
  );
}
