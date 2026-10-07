import React from "react";
import { CameraIcon, SparklesIcon, HistoryIcon, BookOpenIcon, ShieldCheckIcon, CogIcon } from "./Icons";

export type NavTab = "dashboard" | "live" | "text-to-sign" | "history" | "vocab" | "admin" | "settings";

interface SidebarProps {
  activeTab: NavTab;
  onSelectTab: (tab: NavTab) => void;
  isOpenMobile: boolean;
  onCloseMobile: () => void;
}

const NAV_ITEMS: { id: NavTab; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { id: "dashboard", label: "Dashboard", icon: SparklesIcon },
  { id: "live", label: "Live Translator", icon: CameraIcon },
  { id: "text-to-sign", label: "Text to Sign", icon: SparklesIcon },
  { id: "history", label: "History & Logs", icon: HistoryIcon },
  { id: "vocab", label: "Vocabulary (50)", icon: BookOpenIcon },
  { id: "admin", label: "Model Admin", icon: ShieldCheckIcon },
  { id: "settings", label: "Settings", icon: CogIcon },
];

export default function Sidebar({
  activeTab,
  onSelectTab,
  isOpenMobile,
  onCloseMobile,
}: SidebarProps) {
  return (
    <>
      {/* Mobile Backdrop */}
      {isOpenMobile && (
        <div
          role="presentation"
          onClick={onCloseMobile}
          className="fixed inset-0 z-40 bg-black/50 md:hidden backdrop-blur-xs animate-in fade-in"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed md:sticky top-0 md:top-[57px] left-0 z-50 md:z-0 h-screen md:h-[calc(100vh-57px)] w-64 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 p-4 flex flex-col justify-between transition-transform duration-200 ${
          isOpenMobile ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        }`}
      >
        <div className="space-y-6">
          <div className="md:hidden flex items-center justify-between pb-2 border-b border-slate-200 dark:border-slate-800">
            <span className="font-bold text-slate-900 dark:text-white">Navigation</span>
            <button
              type="button"
              onClick={onCloseMobile}
              className="p-1 text-slate-500 hover:text-slate-900 dark:hover:text-white"
            >
              ✕
            </button>
          </div>

          <nav aria-label="Main Navigation" className="space-y-1">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => {
                    onSelectTab(item.id);
                    onCloseMobile();
                  }}
                  aria-current={isActive ? "page" : undefined}
                  className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition ${
                    isActive
                      ? "bg-brand-50 dark:bg-brand-950/70 text-brand-700 dark:text-brand-300 shadow-xs"
                      : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-white"
                  }`}
                >
                  <Icon
                    className={`w-5 h-5 shrink-0 ${
                      isActive ? "text-brand-600 dark:text-brand-400" : "text-slate-400"
                    }`}
                  />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Bottom System Info */}
        <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-800 text-[11px] text-slate-400 space-y-1">
          <div className="flex justify-between font-medium">
            <span>FastAPI Server:</span>
            <span className="font-mono text-emerald-600 dark:text-emerald-400">:8000</span>
          </div>
          <div className="flex justify-between font-medium">
            <span>Client:</span>
            <span className="font-mono">:3000 (Vite)</span>
          </div>
        </div>
      </aside>
    </>
  );
}
