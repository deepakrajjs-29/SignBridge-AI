import React from "react";
import { HandIcon, RefreshIcon, SunIcon, MoonIcon } from "./Icons";

interface HeaderProps {
  backendOnline: boolean;
  modelVersion: string;
  sessionId: string;
  onResetSession: () => void;
  currentTheme: "dark" | "light" | "system";
  onToggleTheme: () => void;
  onMobileMenuToggle: () => void;
}

export default function Header({
  backendOnline,
  modelVersion,
  sessionId,
  onResetSession,
  currentTheme,
  onToggleTheme,
  onMobileMenuToggle,
}: HeaderProps) {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md px-4 sm:px-6 py-3 transition-colors">
      <div className="flex items-center justify-between gap-4">
        {/* Left: Branding & Mobile Menu Toggle */}
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={onMobileMenuToggle}
            className="md:hidden p-2 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
            aria-label="Toggle navigation menu"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 to-isl-teal flex items-center justify-center text-white shadow-md shadow-brand-500/20">
              <HandIcon className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold text-base sm:text-lg text-slate-900 dark:text-white tracking-tight">
                  SignBridge
                </span>
                <span className="text-xs font-bold px-1.5 py-0.5 rounded bg-brand-100 dark:bg-brand-950 text-brand-700 dark:text-brand-300">
                  AI
                </span>
              </div>
              <p className="text-[10px] text-slate-400 font-medium tracking-wider hidden sm:block">
                ISL • DETERMINISTIC AI • REAL-TIME
              </p>
            </div>
          </div>
        </div>

        {/* Right: Status Badges, Session, Theme Toggle */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Backend Status Indicator */}
          <div
            className={`hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${
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
            <span>{backendOnline ? "Backend Online" : "Offline"}</span>
          </div>

          {/* Model Badge */}
          {modelVersion && (
            <div className="hidden lg:inline-flex items-center px-2.5 py-1 rounded-full text-xs font-mono bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
              {modelVersion}
            </div>
          )}

          {/* Active Session Pill */}
          {sessionId && (
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 font-mono text-slate-700 dark:text-slate-300">
              <span className="text-slate-400">#</span>
              <span className="max-w-[70px] truncate">{sessionId.replace(/^sess_/, "")}</span>
              <button
                type="button"
                onClick={onResetSession}
                className="text-slate-400 hover:text-brand-600 dark:hover:text-brand-400 ml-0.5"
                title="Reset session & clear rate limits"
                aria-label="Reset session"
              >
                <RefreshIcon className="w-3.5 h-3.5" />
              </button>
            </div>
          )}

          {/* Theme Toggle */}
          <button
            type="button"
            onClick={onToggleTheme}
            className="p-2 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
            aria-label="Toggle color theme"
          >
            {currentTheme === "dark" ? <SunIcon className="w-4 h-4" /> : <MoonIcon className="w-4 h-4" />}
          </button>
        </div>
      </div>
    </header>
  );
}
