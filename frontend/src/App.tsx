import React, { useEffect, useState } from "react";
import { api, type Prediction } from "./api/client";
import Header from "./components/Header";
import Sidebar, { type NavTab } from "./components/Sidebar";
import ToastContainer, { type ToastMessage } from "./components/Toast";
import Dashboard from "./views/Dashboard";
import Live from "./views/Live";
import TextToSign from "./views/TextToSign";
import History from "./views/History";
import Vocab from "./views/Vocab";
import Admin from "./views/Admin";
import Settings from "./views/Settings";

export default function App() {
  const [tab, setTab] = useState<NavTab>("dashboard");
  const [lastResult, setLastResult] = useState<Prediction | null>(null);
  const [backendOnline, setBackendOnline] = useState<boolean>(true);
  const [modelVersion, setModelVersion] = useState<string>("SBAI-MDL-ISL-1.0.0");
  const [sessionId, setSessionId] = useState<string>("");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  // Theme management (persisted in localStorage)
  const [theme, setTheme] = useState<"dark" | "light" | "system">(() => {
    return (localStorage.getItem("sb_theme") as "dark" | "light" | "system") || "dark";
  });

  useEffect(() => {
    const root = document.documentElement;
    const isDark =
      theme === "dark" ||
      (theme === "system" && window.matchMedia("(prefers-color-scheme: dark)").matches);
    if (isDark) {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
    localStorage.setItem("sb_theme", theme);
  }, [theme]);

  function addToast(type: "success" | "error" | "info", text: string) {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, type, text }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  }

  function dismissToast(id: string) {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }

  // Health and session polling on startup
  useEffect(() => {
    let active = true;

    async function checkHealthAndInit() {
      try {
        const res = await api.health();
        if (active) {
          setBackendOnline(true);
          if (res.model_version) setModelVersion(res.model_version);
        }
      } catch {
        if (active) setBackendOnline(false);
      }
    }

    async function initSession() {
      try {
        const res = await api.openSession();
        if (active && res.session_id) {
          setSessionId(res.session_id);
        }
      } catch {
        // will retry on user action
      }
    }

    checkHealthAndInit();
    initSession();

    // Gentle health polling every 25 seconds
    const interval = setInterval(checkHealthAndInit, 25000);
    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  async function handleResetSession() {
    try {
      await api.resetSession();
      const newSess = await api.openSession();
      setSessionId(newSess.session_id);
      addToast("success", `Session reset: #${newSess.session_id.replace(/^sess_/, "")}`);
    } catch {
      addToast("error", "Could not reset session. Check backend status.");
    }
  }

  function toggleTheme() {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col font-sans transition-colors">
      {/* Top Application Header */}
      <Header
        backendOnline={backendOnline}
        modelVersion={modelVersion}
        sessionId={sessionId}
        onResetSession={handleResetSession}
        currentTheme={theme}
        onToggleTheme={toggleTheme}
        onMobileMenuToggle={() => setMobileMenuOpen(!mobileMenuOpen)}
      />

      <div className="flex-1 flex">
        {/* Navigation Sidebar */}
        <Sidebar
          activeTab={tab}
          onSelectTab={setTab}
          isOpenMobile={mobileMenuOpen}
          onCloseMobile={() => setMobileMenuOpen(false)}
        />

        {/* Main Content Area */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto overflow-y-auto">
          {tab === "dashboard" && (
            <Dashboard
              onNavigate={(dest) => setTab(dest)}
              backendOnline={backendOnline}
            />
          )}
          {tab === "live" && (
            <Live
              activeSessionId={sessionId}
              onResult={(p) => setLastResult(p)}
            />
          )}
          {tab === "text-to-sign" && <TextToSign />}
          {tab === "history" && <History />}
          {tab === "vocab" && <Vocab />}
          {tab === "admin" && <Admin />}
          {tab === "settings" && (
            <Settings
              currentTheme={theme}
              onThemeChange={setTheme}
            />
          )}

          {/* Accessible Live Region for Screen Readers */}
          {lastResult && tab === "live" && (
            <div className="sr-only" role="status" aria-live="polite">
              Recognized sign: {lastResult.label} with confidence {Math.round(lastResult.confidence * 100)} percent.
            </div>
          )}
        </main>
      </div>

      {/* Toast Notifications */}
      <ToastContainer toasts={toasts} onDismiss={dismissToast} />
    </div>
  );
}
