import React from "react";
import { CheckCircleIcon, AlertCircleIcon } from "./Icons";

export interface ToastMessage {
  id: string;
  type: "success" | "error" | "info";
  text: string;
}

export default function ToastContainer({ toasts, onDismiss }: { toasts: ToastMessage[]; onDismiss: (id: string) => void }) {
  if (toasts.length === 0) return null;

  return (
    <div
      aria-live="polite"
      className="fixed bottom-5 right-5 z-50 flex flex-col gap-2 max-w-sm pointer-events-none"
    >
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg border text-sm font-medium transition-all ${
            t.type === "success"
              ? "bg-seafoam-light dark:bg-seafoam/20 text-teal-deep dark:text-seafoam border-seafoam/40"
              : t.type === "error"
              ? "bg-rose-50 dark:bg-rose-950/80 text-rose-800 dark:text-rose-200 border-rose-300 dark:border-rose-800"
              : "bg-white dark:bg-midnight text-midnight dark:text-white border-card-border"
          }`}
        >
          {t.type === "success" && <CheckCircleIcon className="w-5 h-5 text-seafoam-dark dark:text-seafoam shrink-0" />}
          {t.type === "error" && <AlertCircleIcon className="w-5 h-5 text-rose-600 dark:text-rose-400 shrink-0" />}
          <span className="flex-1">{t.text}</span>
          <button
            type="button"
            onClick={() => onDismiss(t.id)}
            className="text-xs opacity-60 hover:opacity-100 ml-2"
            aria-label="Close notification"
          >
            ✕
          </button>
        </div>
      ))}
    </div>
  );
}
