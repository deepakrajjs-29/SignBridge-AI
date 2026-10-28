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
    <header className="sticky top-0 z-40 w-full border-b border-card-border/80 bg-page-bg/90 dark:bg-midnight/90 backdrop-blur-md px-4 sm:px-8 py-3 transition-colors">
      <div className="flex items-center justify-between gap-4">
        {/* Left: Branding & Mobile Menu Toggle */}
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={onMobileMenuToggle}
            className="md:hidden p-2 rounded-lg text-text-secondary hover:text-midnight dark:hover:text-white hover:bg-soft-surface dark:hover:bg-midnight-light"
            aria-label="Toggle navigation menu"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-teal-deep flex items-center justify-center text-white border border-white/20 shadow-xs">
              <span className="material-symbols-outlined text-xl">sign_language</span>
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-bold text-base sm:text-lg text-midnight dark:text-white tracking-tight">
                  SignBridge
                </span>
                <span className="text-[11px] font-bold px-1.5 py-0.5 rounded bg-seafoam-light text-teal-deep border border-seafoam/30">
                  AI
                </span>
              </div>
              <p className="text-[10px] text-text-secondary font-medium tracking-wider hidden sm:block">
                ISL • REAL-TIME INTERPRETATION
              </p>
            </div>
          </div>
        </div>

        {/* Right: Status Badges, Session, Theme Toggle */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Backend Status Indicator */}
          <div
            className={`hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold ${
              backendOnline
                ? "bg-seafoam-light text-teal-deep border border-seafoam/30"
                : "bg-rose-50 text-rose-700 border border-rose-200"
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full ${
                backendOnline ? "bg-seafoam animate-pulse" : "bg-rose-500"
              }`}
            ></span>
            <span>{backendOnline ? "Engine Online" : "Engine Offline"}</span>
          </div>

          {/* Model Badge */}
          {modelVersion && (
            <div className="hidden lg:inline-flex items-center px-2.5 py-1 rounded-full text-xs font-mono bg-white dark:bg-midnight-light text-text-secondary dark:text-slate-200 border border-card-border shadow-2xs">
              {modelVersion}
            </div>
          )}

          {/* Active Session Pill */}
          {sessionId && (
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs bg-white dark:bg-midnight-light border border-card-border font-mono text-midnight dark:text-white shadow-2xs">
              <span className="text-text-secondary">#</span>
              <span className="max-w-[70px] truncate">{sessionId.replace(/^sess_/, "")}</span>
              <button
                type="button"
                onClick={onResetSession}
                className="text-text-secondary hover:text-teal-deep dark:hover:text-seafoam ml-0.5"
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
            className="p-2 rounded-xl text-text-secondary hover:text-midnight dark:hover:text-white hover:bg-white dark:hover:bg-midnight-light border border-transparent hover:border-card-border transition shadow-2xs"
            aria-label="Toggle color theme"
          >
            {currentTheme === "dark" ? <SunIcon className="w-4 h-4" /> : <MoonIcon className="w-4 h-4" />}
          </button>
        </div>
      </div>
    </header>
  );
}
