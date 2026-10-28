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
  { id: "vocab", label: "Vocabulary (109)", icon: BookOpenIcon },
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
        className={`fixed md:sticky top-0 md:top-0 left-0 z-50 h-screen w-64 bg-[hsl(var(--hue,188),32%,11%)] text-white border-r border-[hsl(var(--hue,188),25%,18%)] p-4 flex flex-col justify-between select-none shadow-sm transition-colors duration-200 ${
          isOpenMobile ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        }`}
      >
        <div className="space-y-5">
          {/* Brand header */}
          <div className="flex items-center justify-between pb-4 border-b border-[hsl(var(--hue,188),25%,18%)]">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-teal-deep border border-white/20 flex items-center justify-center text-white shadow-sm">
                <span className="material-symbols-outlined text-xl">sign_language</span>
              </div>
              <div className="flex flex-col">
                <span className="font-bold text-base tracking-tight text-white leading-tight">SignBridge AI</span>
                <span className="text-xs text-[#8BA1AD]">Indian Sign Language</span>
              </div>
            </div>
            <button
              type="button"
              onClick={onCloseMobile}
              className="md:hidden p-1 text-slate-400 hover:text-white"
            >
              ✕
            </button>
          </div>

          <nav aria-label="Main Navigation" className="space-y-1.5">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              const isLive = item.id === "live";
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => {
                    onSelectTab(item.id);
                    onCloseMobile();
                  }}
                  aria-current={isActive ? "page" : undefined}
                  className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-teal-deep text-white font-bold shadow-md border border-white/25"
                      : "text-slate-300 hover:text-white hover:bg-white/10"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon
                      className={`w-5 h-5 shrink-0 ${
                        isActive ? "text-white" : "text-slate-400"
                      }`}
                    />
                    <span>{item.label}</span>
                  </div>
                  {isLive && (
                    <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-seafoam/20 text-seafoam text-[11px] font-semibold">
                      <span className="w-1.5 h-1.5 rounded-full bg-seafoam animate-pulse"></span>
                      LIVE
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Bottom System & Profile Card */}
        <div className="p-3.5 rounded-xl bg-[hsl(var(--hue,188),28%,15%)] border border-white/10 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-full bg-teal-deep border border-white/20 flex items-center justify-center font-bold text-white text-xs">
              SB
            </div>
            <div className="flex flex-col text-left">
              <span className="text-xs font-semibold text-white leading-tight">ISL Studio</span>
              <span className="text-[11px] text-[#8BA1AD]">MediaPipe Pipeline</span>
            </div>
          </div>
          <span className="w-2.5 h-2.5 rounded-full bg-seafoam" title="System Ready"></span>
        </div>
      </aside>
    </>
  );
}
