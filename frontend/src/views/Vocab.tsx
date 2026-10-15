import React, { useEffect, useState } from "react";
import { api, type ClassItem } from "../api/client";
import { BookOpenIcon, AlertCircleIcon, VolumeUpIcon } from "../components/Icons";

const DOMAIN_CATEGORIES = [
  { id: "all", label: "All Signs" },
  { id: "greetings", label: "Greetings & Courtesy" },
  { id: "emergency", label: "Emergency & Medical" },
  { id: "actions", label: "Daily & Actions" },
  { id: "people", label: "People & Family" },
  { id: "places", label: "Places & Travel" },
  { id: "time_questions", label: "Time & Questions" },
  { id: "feelings_daily", label: "Emotions & Living" },
] as const;

type DomainId = typeof DOMAIN_CATEGORIES[number]["id"];

const DOMAIN_MAP: Record<string, DomainId> = {
  // greetings
  "Hello": "greetings", "Thank You": "greetings", "Please": "greetings", "Good Morning": "greetings",
  "Good Night": "greetings", "Good Afternoon": "greetings", "Good Evening": "greetings",
  // emergency
  "Help": "emergency", "Doctor": "emergency", "Medicine": "emergency",
  "Pain": "emergency", "Water": "emergency", "Food": "emergency",
  // people
  "Man": "people", "Woman": "people", "Mother": "people", "Father": "people", "Friend": "people",
  "Family": "people", "Sister": "people", "Student": "people", "Teacher": "people", "Child": "people",
  "Girl": "people", "Boy": "people", "She": "people", "He": "people", "You": "people", "We": "people",
  "They": "people", "I": "people", "Wife": "people", "Husband": "people", "Uncle": "people",
  "Aunt": "people", "Baby": "people",
  // places
  "Market": "places", "House": "places", "School": "places", "Office": "places", "Road": "places",
  "City": "places", "Shop": "places", "Bank": "places", "Car": "places", "Bus": "places",
  // actions
  "Go": "actions", "Sit": "actions", "Eat": "actions", "Drink": "actions",
  "Stay": "actions", "Wait": "actions", "Open": "actions",
  "Close": "actions", "Give": "actions",
  "Walk": "actions", "Work": "actions",
  // time_questions
  "Morning": "time_questions", "Evening": "time_questions", "Night": "time_questions", "Day": "time_questions",
  "Time": "time_questions", "Today": "time_questions", "Tomorrow": "time_questions", "Yesterday": "time_questions",
  "Month": "time_questions", "Year": "time_questions", "Saturday": "time_questions", "Sunday": "time_questions",
  "Hour": "time_questions", "What": "time_questions",
  "Where": "time_questions", "Why": "time_questions",
  "Which": "time_questions",
  // feelings_daily
  "Happy": "feelings_daily", "Sad": "feelings_daily", "Good": "feelings_daily",
  "Bad": "feelings_daily", "Yes": "feelings_daily", "No": "feelings_daily", "Tea": "feelings_daily",
  "Book": "feelings_daily", "Bread": "feelings_daily", "Pizza": "feelings_daily", "Mango": "feelings_daily",
  "Lunch": "feelings_daily", "Onion": "feelings_daily", "Lion": "feelings_daily", "Dog": "feelings_daily",
  "Cat": "feelings_daily", "Red": "feelings_daily", "Blue": "feelings_daily", "Green": "feelings_daily",
  "Computer": "feelings_daily", "Movie": "feelings_daily", "Music": "feelings_daily", "Big": "feelings_daily",
  "Small": "feelings_daily", "Hot": "feelings_daily", "Cold": "feelings_daily",
};

export default function Vocab() {
  const [classes, setClasses] = useState<ClassItem[]>([]);
  const [q, setQ] = useState("");
  const [category, setCategory] = useState<DomainId>("all");
  const [handednessFilter, setHandednessFilter] = useState<"all" | "Both" | "Right">("all");
  const [typeFilter, setTypeFilter] = useState<"all" | "Dynamic" | "Static">("all");
  const [note, setNote] = useState("");
  const [loading, setLoading] = useState(true);
  const [failedImgs, setFailedImgs] = useState<Set<string>>(new Set());
  const [selectedSign, setSelectedSign] = useState<ClassItem | null>(null);
  const [speakingId, setSpeakingId] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    api
      .classes()
      .then((r) => setClasses(r.classes))
      .catch((e: Error) => setNote(e.message))
      .finally(() => setLoading(false));
  }, []);

  function getDomain(label: string): DomainId {
    return DOMAIN_MAP[label] || "feelings_daily";
  }

  function photoSrc(c: ClassItem): string {
    return c.asset_uri || `/assets/${c.class_id}.jpg`;
  }

  function markImgFailed(class_id: string) {
    setFailedImgs((prev) => new Set(prev).add(class_id));
  }

  function speakLabel(text: string, id: string, e?: React.MouseEvent) {
    if (e) e.stopPropagation();
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(text);
      u.rate = 0.95;
      u.pitch = 1.0;
      setSpeakingId(id);
      u.onend = () => setSpeakingId(null);
      u.onerror = () => setSpeakingId(null);
      window.speechSynthesis.speak(u);
    }
  }

  const categoryCounts: Record<DomainId, number> = {
    all: classes.length,
    greetings: classes.filter((c) => getDomain(c.label) === "greetings").length,
    emergency: classes.filter((c) => getDomain(c.label) === "emergency").length,
    actions: classes.filter((c) => getDomain(c.label) === "actions").length,
    people: classes.filter((c) => getDomain(c.label) === "people").length,
    places: classes.filter((c) => getDomain(c.label) === "places").length,
    time_questions: classes.filter((c) => getDomain(c.label) === "time_questions").length,
    feelings_daily: classes.filter((c) => getDomain(c.label) === "feelings_daily").length,
  };

  const filtered = classes.filter((c) => {
    const matchesSearch =
      c.label.toLowerCase().includes(q.toLowerCase()) ||
      c.class_id.toLowerCase().includes(q.toLowerCase()) ||
      (c.meaning && c.meaning.toLowerCase().includes(q.toLowerCase())) ||
      (c.gloss && c.gloss.toLowerCase().includes(q.toLowerCase()));
    const matchesCat = category === "all" || getDomain(c.label) === category;
    const matchesType = typeFilter === "all" || c.sign_type === typeFilter;
    const matchesHand =
      handednessFilter === "all" || (c.handedness || "Both") === handednessFilter;
    return matchesSearch && matchesCat && matchesType && matchesHand;
  });

  return (
    <div className="space-y-6 max-w-6xl animate-in fade-in duration-200">
      {/* Header & Overview Card */}
      <div className="p-6 md:p-8 rounded-3xl bg-gradient-to-br from-slate-900 via-brand-950 to-slate-900 text-white shadow-xl border border-slate-800 space-y-4">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-brand-500/20 text-brand-300 border border-brand-500/30 mb-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              SBAI-MDL-ISL-2.0.0 • SOFTMAX(100) ACTIVE
            </div>
            <h2 className="text-2xl sm:text-3xl font-black text-white flex items-center gap-3">
              <BookOpenIcon className="w-8 h-8 text-brand-400" />
              <span>ISL-100 Vocabulary & Photo Explorer</span>
            </h2>
            <p className="text-sm text-slate-300 mt-1 max-w-2xl leading-relaxed">
              Explore all 100 registered Indian Sign Language dynamic signs with real photographic demonstration keyframes, phonetic pronunciation, and neural model class mappings.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-3.5 text-center min-w-[100px]">
              <span className="text-2xl font-black text-brand-300 block">{classes.length || 100}</span>
              <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Total Signs</span>
            </div>
            <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-3.5 text-center min-w-[100px]">
              <span className="text-2xl font-black text-emerald-400 block">100%</span>
              <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Photo Ref</span>
            </div>
          </div>
        </div>
      </div>

      {/* Filter and Search Controls */}
      <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
        <div className="flex flex-col md:flex-row gap-3 items-center justify-between">
          <div className="relative flex-1 w-full">
            <input
              type="text"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search sign word, meaning, gloss, or ID (e.g. Hello, Doctor, ISL_001)..."
              aria-label="vocab-search"
              className="w-full pl-4 pr-10 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/80 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
            {q && (
              <button
                type="button"
                onClick={() => setQ("")}
                className="absolute right-3 top-3 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xs"
              >
                ✕
              </button>
            )}
          </div>

          <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
            {/* Handedness Filter */}
            <select
              value={handednessFilter}
              onChange={(e) => setHandednessFilter(e.target.value as any)}
              className="px-3 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-300 focus:outline-none"
            >
              <option value="all">All Handedness</option>
              <option value="Both">👐 Both Hands</option>
              <option value="Right">✋ Right Hand</option>
            </select>

            {/* Dynamic / Static Filter */}
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value as any)}
              className="px-3 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-300 focus:outline-none"
            >
              <option value="all">All Sign Types</option>
              <option value="Dynamic">Dynamic Signs</option>
              <option value="Static">Static Signs</option>
            </select>
          </div>
        </div>

        {/* Category Tabs */}
        <div className="flex flex-wrap items-center gap-1.5 pt-1">
          {DOMAIN_CATEGORIES.map((t) => (
            <button
              key={t.id}
              type="button"
              onClick={() => setCategory(t.id)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition flex items-center gap-1.5 border ${
                category === t.id
                  ? "bg-brand-600 text-white border-brand-600 shadow-sm shadow-brand-500/25"
                  : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-transparent hover:bg-slate-200 dark:hover:bg-slate-700 hover:text-slate-900 dark:hover:text-white"
              }`}
            >
              <span>{t.label}</span>
              <span className={`text-[10px] px-1.5 py-0.2 rounded-full ${
                category === t.id ? "bg-white/20 text-white" : "bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300"
              }`}>
                {categoryCounts[t.id] ?? 0}
              </span>
            </button>
          ))}
        </div>
      </div>

      {note && (
        <div role="alert" className="p-3.5 rounded-xl bg-rose-50 dark:bg-rose-950/60 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300 text-sm flex items-center gap-2">
          <AlertCircleIcon className="w-5 h-5 shrink-0" />
          <span>{note}</span>
        </div>
      )}

      {/* Grid of 100 Sign Cards */}
      {loading ? (
        <div className="p-16 text-center space-y-3">
          <span className="w-8 h-8 border-3 border-brand-500 border-t-transparent rounded-full animate-spin inline-block"></span>
          <p className="text-sm font-semibold text-slate-600 dark:text-slate-300">
            Loading 100 ISL signs and photographic assets from backend…
          </p>
        </div>
      ) : filtered.length === 0 ? (
        <div className="p-12 text-center rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-3">
          <p className="text-slate-500 dark:text-slate-400 text-sm">
            No signs found matching &ldquo;{q}&rdquo;. Try another search keyword or clear filters.
          </p>
          <button
            type="button"
            onClick={() => {
              setQ("");
              setCategory("all");
              setHandednessFilter("all");
              setTypeFilter("all");
            }}
            className="px-4 py-2 rounded-xl bg-brand-500 text-white text-xs font-bold"
          >
            Reset Filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {filtered.map((c) => {
            const isSpeaking = speakingId === c.class_id;
            return (
              <div
                key={c.class_id}
                onClick={() => setSelectedSign(c)}
                className="group cursor-pointer p-3.5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-brand-500 dark:hover:border-brand-500 hover:shadow-lg transition-all duration-200 flex flex-col justify-between space-y-2.5"
              >
                {/* Card Top: ID and Type Badge */}
                <div className="flex items-center justify-between text-[11px] text-slate-400">
                  <span className="font-mono font-bold text-brand-600 dark:text-brand-400">{c.class_id}</span>
                  <div className="flex items-center gap-1">
                    <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-brand-50 dark:bg-brand-950/60 text-brand-600 dark:text-brand-300">
                      {c.sign_type || "Dynamic"}
                    </span>
                  </div>
                </div>

                {/* Card Center: High-Res Reference Photo */}
                <div className="relative aspect-4/3 w-full bg-slate-100 dark:bg-slate-800/60 rounded-xl overflow-hidden border border-slate-100 dark:border-slate-800 flex items-center justify-center">
                  {failedImgs.has(c.class_id) ? (
                    <span className="text-lg font-black text-slate-900 dark:text-white uppercase tracking-tight block p-4 text-center">
                      {c.label}
                    </span>
                  ) : (
                    <img
                      src={photoSrc(c)}
                      alt={`${c.label} ISL sign`}
                      loading="lazy"
                      onError={() => markImgFailed(c.class_id)}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  )}

                  {/* Audio button overlay */}
                  <button
                    type="button"
                    onClick={(e) => speakLabel(c.label, c.class_id, e)}
                    className={`absolute bottom-2 right-2 p-1.5 rounded-lg backdrop-blur-md transition shadow-sm ${
                      isSpeaking
                        ? "bg-emerald-500 text-white animate-pulse"
                        : "bg-black/50 hover:bg-brand-600 text-white opacity-85 group-hover:opacity-100"
                    }`}
                    title={`Pronounce ${c.label}`}
                    aria-label={`Pronounce ${c.label}`}
                  >
                    <VolumeUpIcon className="w-3.5 h-3.5" />
                  </button>
                </div>

                {/* Card Bottom: Word Label & Context */}
                <div className="pt-1">
                  <div className="flex items-center justify-between gap-1">
                    <span className="text-sm font-bold text-slate-900 dark:text-white truncate block group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors">
                      {c.label}
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono shrink-0">
                      {c.handedness === "Right" ? "✋ Right" : "👐 Both"}
                    </span>
                  </div>
                  {c.meaning && (
                    <span className="text-[11px] text-slate-500 dark:text-slate-400 truncate block mt-0.5">
                      {c.meaning}
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Sign Detail Modal */}
      {selectedSign && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-150"
          onClick={() => setSelectedSign(null)}
          role="dialog"
          aria-modal="true"
        >
          <div
            className="w-full max-w-lg bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-2xl p-6 md:p-8 space-y-5 animate-in zoom-in-95 duration-150"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between">
              <div>
                <span className="text-xs font-mono font-bold text-brand-600 dark:text-brand-400 bg-brand-50 dark:bg-brand-950/80 px-2 py-0.5 rounded">
                  {selectedSign.class_id} • {selectedSign.sign_type || "Dynamic"}
                </span>
                <h3 className="text-2xl font-black text-slate-900 dark:text-white mt-1.5 flex items-center gap-2">
                  <span>{selectedSign.label}</span>
                  <button
                    type="button"
                    onClick={() => speakLabel(selectedSign.label, selectedSign.class_id)}
                    className="p-1.5 rounded-lg text-brand-600 dark:text-brand-400 hover:bg-brand-50 dark:hover:bg-brand-950 transition"
                    title="Speak word"
                  >
                    <VolumeUpIcon className="w-5 h-5" />
                  </button>
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setSelectedSign(null)}
                className="text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 p-2 rounded-xl text-lg font-bold"
                aria-label="Close modal"
              >
                ✕
              </button>
            </div>

            {/* Modal Image */}
            <div className="w-full aspect-16/10 rounded-2xl overflow-hidden bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-800 flex items-center justify-center">
              <img
                src={photoSrc(selectedSign)}
                alt={`${selectedSign.label} ISL Demonstration`}
                className="w-full h-full object-cover"
              />
            </div>

            {/* Metadata Badges & Info */}
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800 space-y-1">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Handedness</span>
                <span className="font-semibold text-slate-800 dark:text-slate-200 text-sm">
                  {selectedSign.handedness === "Right" ? "✋ Right Hand Only" : "👐 Both Hands Active"}
                </span>
              </div>
              <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800 space-y-1">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Context / Domain</span>
                <span className="font-semibold text-slate-800 dark:text-slate-200 text-sm">
                  {selectedSign.meaning || "Everyday Vocabulary"}
                </span>
              </div>
              <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800 space-y-1">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Gloss Token</span>
                <span className="font-mono font-semibold text-slate-800 dark:text-slate-200">
                  {selectedSign.gloss || selectedSign.label.toUpperCase()}
                </span>
              </div>
              <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800 space-y-1">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Active Neural Head</span>
                <span className="font-semibold text-emerald-600 dark:text-emerald-400">
                  Softmax(100) Class {selectedSign.class_id.replace("ISL_", "")}
                </span>
              </div>
            </div>

            <div className="pt-2 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setSelectedSign(null)}
                className="px-5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-semibold text-xs hover:bg-slate-200 dark:hover:bg-slate-700 transition"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
