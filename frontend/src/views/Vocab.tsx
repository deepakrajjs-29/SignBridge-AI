import React, { useEffect, useState } from "react";
import { api, type ClassItem } from "../api/client";
import { BookOpenIcon, AlertCircleIcon } from "../components/Icons";

export default function Vocab() {
  const [classes, setClasses] = useState<ClassItem[]>([]);
  const [q, setQ] = useState("");
  const [category, setCategory] = useState<"all" | "words" | "digits" | "letters">("all");
  const [typeFilter, setTypeFilter] = useState<"all" | "Dynamic" | "Static">("all");
  const [note, setNote] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api
      .classes()
      .then((r) => setClasses(r.classes))
      .catch((e: Error) => setNote(e.message))
      .finally(() => setLoading(false));
  }, []);

  function getCategory(label: string): "digits" | "letters" | "words" {
    if (/^[0-9]$/.test(label)) return "digits";
    if (/^[A-Za-z]$/.test(label)) return "letters";
    return "words";
  }

  const filtered = classes.filter((c) => {
    const matchesSearch =
      c.label.toLowerCase().includes(q.toLowerCase()) ||
      c.class_id.toLowerCase().includes(q.toLowerCase());
    const matchesCat = category === "all" || getCategory(c.label) === category;
    const matchesType = typeFilter === "all" || c.sign_type === typeFilter;
    return matchesSearch && matchesCat && matchesType;
  });

  return (
    <div className="space-y-6 max-w-5xl animate-in fade-in duration-200">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <BookOpenIcon className="w-6 h-6 text-brand-600 dark:text-brand-400" />
            ISL Vocabulary Explorer
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Browse the {classes.length} registered Indian Sign Language signs supported by the active neural model.
          </p>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col md:flex-row gap-4 items-center justify-between">
        <div className="flex-1 w-full">
          <input
            type="text"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search sign label or class ID (e.g. hello, ISL_001)…"
            aria-label="vocab-search"
            className="w-full px-4 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm text-slate-900 dark:text-white"
          />
        </div>

        {/* Category Tabs */}
        <div className="flex items-center gap-1 p-1 bg-slate-100 dark:bg-slate-800 rounded-lg text-xs font-semibold w-full md:w-auto">
          {(
            [
              { id: "all", label: "All (50)" },
              { id: "words", label: "Words (30)" },
              { id: "digits", label: "Digits (10)" },
              { id: "letters", label: "Letters (10)" },
            ] as const
          ).map((t) => (
            <button
              key={t.id}
              type="button"
              onClick={() => setCategory(t.id)}
              className={`px-3 py-1.5 rounded-md transition ${
                category === t.id
                  ? "bg-white dark:bg-slate-900 text-brand-600 dark:text-brand-400 shadow-sm"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* Dynamic / Static Filter */}
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value as any)}
          className="px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs font-medium text-slate-700 dark:text-slate-300 w-full md:w-auto"
        >
          <option value="all">All Sign Types</option>
          <option value="Dynamic">Dynamic Signs</option>
          <option value="Static">Static Signs</option>
        </select>
      </div>

      {note && (
        <div role="alert" className="p-3 rounded-lg bg-rose-50 dark:bg-rose-950/60 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300 text-sm flex items-center gap-2">
          <AlertCircleIcon className="w-4 h-4 shrink-0" />
          <span>{note}</span>
        </div>
      )}

      {/* Grid of Sign Cards */}
      {loading ? (
        <div className="p-12 text-center">
          <span className="w-6 h-6 border-2 border-brand-500 border-t-transparent rounded-full animate-spin inline-block"></span>
          <p className="text-xs text-slate-500 mt-2">Loading vocabulary from backend…</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {filtered.map((c) => (
            <div
              key={c.class_id}
              className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm hover:border-brand-400 dark:hover:border-brand-600 transition space-y-3"
            >
              <div className="flex items-center justify-between text-[11px] text-slate-400">
                <span className="font-mono">{c.class_id}</span>
                <span
                  className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${
                    c.sign_type === "Dynamic"
                      ? "bg-brand-50 dark:bg-brand-950/60 text-brand-600 dark:text-brand-300"
                      : "bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-300"
                  }`}
                >
                  {c.sign_type}
                </span>
              </div>

              <div className="text-center py-6 bg-slate-50 dark:bg-slate-800/40 rounded-lg border border-slate-100 dark:border-slate-800">
                <span className="text-xl font-black text-slate-900 dark:text-white uppercase tracking-tight">
                  {c.label}
                </span>
              </div>

              <div className="text-center">
                <span className="text-[10px] text-slate-400">
                  Sign preview unavailable
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
