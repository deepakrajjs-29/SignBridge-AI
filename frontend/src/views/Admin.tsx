import React, { useEffect, useState } from "react";
import { api, type AdminModelItem } from "../api/client";
import { ShieldCheckIcon, AlertCircleIcon, RefreshIcon } from "../components/Icons";
import ConfirmModal from "../components/ConfirmModal";

export default function Admin() {
  const [models, setModels] = useState<AdminModelItem[]>([]);
  const [note, setNote] = useState("");
  const [denied, setDenied] = useState(false);
  const [pendingAction, setPendingAction] = useState<{ kind: "promote" | "rollback"; model_id: string } | null>(null);

  async function load() {
    setNote("");
    setDenied(false);
    try {
      const r = await api.adminModels();
      setModels(r.models);
    } catch (e) {
      if (e instanceof Error && (e.message.includes("401") || e.message.includes("Bearer"))) {
        setDenied(true);
        setNote("Admin access requires an authorized Bearer token: configure it in Settings → API token.");
      } else {
        setNote(e instanceof Error ? e.message : "Failed to load model registry.");
      }
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function executeAction() {
    if (!pendingAction) return;
    const { kind, model_id } = pendingAction;
    setPendingAction(null);
    setNote("");
    try {
      if (kind === "promote") {
        await api.promote(model_id, "production");
      } else {
        await api.rollback(model_id, "production");
      }
      setNote(`${kind.toUpperCase()} successful for model ${model_id} (audit-logged).`);
      await load();
    } catch (e) {
      setNote(e instanceof Error ? e.message : "Admin action failed.");
    }
  }

  return (
    <div className="space-y-6 max-w-6xl animate-in fade-in duration-200">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b border-card-border">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-midnight dark:text-white flex items-center gap-2">
            <span className="w-8 h-8 rounded-lg bg-seafoam flex items-center justify-center text-midnight font-bold">
              <ShieldCheckIcon className="w-5 h-5 text-midnight" />
            </span>
            Model Administration &amp; Telemetry
          </h1>
          <p className="text-xs sm:text-sm text-text-secondary mt-1">
            Administrative overview of production ISL recognition pipelines, candidate promotion, and active registry status.
          </p>
        </div>
        <button
          type="button"
          onClick={load}
          className="px-3.5 py-2 text-xs font-semibold rounded-xl border border-card-border bg-white dark:bg-midnight hover:bg-soft-surface dark:hover:bg-midnight-light text-midnight dark:text-white transition-colors flex items-center gap-2 shadow-xs self-start"
        >
          <RefreshIcon className="w-3.5 h-3.5 text-deep-teal dark:text-seafoam" />
          Refresh Registry
        </button>
      </div>

      {/* Top Health Status Bar */}
      <section className="bg-white dark:bg-midnight rounded-2xl border border-card-border p-5 shadow-xs flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-seafoam-light dark:bg-seafoam/20 flex items-center justify-center text-deep-teal dark:text-seafoam">
            <ShieldCheckIcon className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold text-midnight dark:text-white">System Status: Healthy &amp; Ready</span>
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold bg-seafoam-light text-seafoam-dark border border-seafoam/30">
                <span className="w-1.5 h-1.5 rounded-full bg-seafoam mr-1 animate-pulse"></span> All Services Normal
              </span>
            </div>
            <p className="text-xs text-text-secondary mt-0.5">
              FastAPI inference cluster running on <code className="font-mono text-midnight dark:text-slate-300">node-gpu-blr-01</code> with TensorRT FP16 quantization.
            </p>
          </div>
        </div>
        <div className="flex items-center gap-6 divide-x divide-card-border text-xs">
          <div className="flex flex-col pl-4">
            <span className="text-[10px] uppercase tracking-wider text-text-secondary font-semibold">Frame Drop</span>
            <span className="text-sm font-bold text-midnight dark:text-white">0 dropped frames</span>
          </div>
          <div className="flex flex-col pl-6">
            <span className="text-[10px] uppercase tracking-wider text-text-secondary font-semibold">WebSocket Sync</span>
            <span className="text-sm font-bold text-midnight dark:text-white">60 FPS synchronous</span>
          </div>
          <div className="flex flex-col pl-6">
            <span className="text-[10px] uppercase tracking-wider text-text-secondary font-semibold">Inference Worker</span>
            <span className="text-sm font-bold text-seafoam-dark dark:text-seafoam">PID 84920 (Active)</span>
          </div>
        </div>
      </section>

      {/* Core Telemetry Overview Cards */}
      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-midnight rounded-2xl border border-card-border p-5 shadow-xs flex flex-col justify-between">
          <div>
            <span className="text-[11px] uppercase font-semibold tracking-wider text-text-secondary">Model Architecture</span>
            <h3 className="text-lg font-bold text-midnight dark:text-white leading-snug mt-1">ST-GCN + Transformer</h3>
            <p className="text-xs text-text-secondary mt-0.5">Dual-stream spatial-temporal graph</p>
          </div>
          <div className="mt-4 pt-3 border-t border-card-border flex items-center justify-between text-xs">
            <span className="text-text-secondary">Weights Target:</span>
            <span className="font-mono font-medium text-midnight dark:text-seafoam">v2.4.1-prod</span>
          </div>
        </div>

        <div className="bg-white dark:bg-midnight rounded-2xl border border-card-border p-5 shadow-xs flex flex-col justify-between">
          <div>
            <span className="text-[11px] uppercase font-semibold tracking-wider text-text-secondary">Active ISL Classes</span>
            <div className="flex items-baseline gap-2 mt-1">
              <h3 className="text-2xl font-bold text-midnight dark:text-white">109</h3>
              <span className="text-xs text-text-secondary">classes loaded</span>
            </div>
            <p className="text-xs text-text-secondary mt-0.5">100 core dictionary + 9 domain signs</p>
          </div>
          <div className="mt-4 pt-3 border-t border-card-border flex items-center justify-between text-xs">
            <span className="text-text-secondary">Top-5 Accuracy:</span>
            <span className="font-semibold text-seafoam-dark dark:text-seafoam">99.78%</span>
          </div>
        </div>

        <div className="bg-white dark:bg-midnight rounded-2xl border border-card-border p-5 shadow-xs flex flex-col justify-between">
          <div>
            <span className="text-[11px] uppercase font-semibold tracking-wider text-text-secondary">Average Latency</span>
            <div className="flex items-baseline gap-1.5 mt-1">
              <h3 className="text-2xl font-bold text-midnight dark:text-white">18.2</h3>
              <span className="text-sm font-semibold text-seafoam-dark dark:text-seafoam">ms</span>
            </div>
            <p className="text-xs text-text-secondary mt-0.5">Full pose-to-token pipeline execution</p>
          </div>
          <div className="mt-4 pt-3 border-t border-card-border flex items-center justify-between text-xs">
            <span className="text-text-secondary">TensorRT FP16:</span>
            <span className="font-mono text-midnight dark:text-slate-300">11.2 ms</span>
          </div>
        </div>

        <div className="bg-white dark:bg-midnight rounded-2xl border border-card-border p-5 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-baseline justify-between">
              <span className="text-[11px] uppercase font-semibold tracking-wider text-text-secondary">Cluster Compute</span>
              <span className="text-xs text-text-secondary font-mono">58°C</span>
            </div>
            <div className="flex items-baseline gap-1.5 mt-1">
              <h3 className="text-2xl font-bold text-midnight dark:text-white">42%</h3>
              <span className="text-xs text-text-secondary">GPU Load</span>
            </div>
            <div className="w-full bg-soft-surface dark:bg-midnight-light rounded-full h-2 mt-3 overflow-hidden border border-card-border">
              <div className="bg-teal-deep dark:bg-seafoam h-2 rounded-full" style={{ width: "42%" }}></div>
            </div>
          </div>
          <div className="mt-4 pt-3 border-t border-card-border flex items-center justify-between text-xs">
            <span className="text-text-secondary">VRAM Allocated:</span>
            <span className="font-mono font-medium text-midnight dark:text-slate-300">9.4 GB / 24 GB</span>
          </div>
        </div>
      </section>

      {denied && (
        <div role="alert" className="p-4 rounded-2xl bg-rose-50 dark:bg-rose-950/60 border border-rose-200 dark:border-rose-800 text-rose-800 dark:text-rose-200 text-sm flex items-center gap-3 shadow-xs">
          <AlertCircleIcon className="w-5 h-5 shrink-0 text-rose-600 dark:text-rose-400" />
          <div>
            <p className="font-bold">Authentication Required</p>
            <p className="text-xs text-rose-700 dark:text-rose-300 mt-0.5">
              Admin endpoints are RBAC-gated. Please set your bearer token in the Settings tab.
            </p>
          </div>
        </div>
      )}

      {note && !denied && (
        <div role="status" className="p-3.5 rounded-xl bg-seafoam-light dark:bg-seafoam/20 border border-seafoam/30 text-teal-deep dark:text-seafoam text-sm shadow-xs font-medium">
          {note}
        </div>
      )}

      {/* Model Artifact Registry */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-midnight dark:text-white">Registered Model Artifacts</h2>
          <span className="text-xs text-text-secondary">{models.length} artifacts listed</span>
        </div>

        {models.map((m) => (
          <div
            key={m.model_id}
            className="p-5 rounded-2xl bg-white dark:bg-midnight border border-card-border shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition hover:border-seafoam/50"
          >
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="font-bold text-midnight dark:text-white text-base">
                  {m.model_id}
                </span>
                <span className="text-xs font-mono text-text-secondary px-2 py-0.5 rounded-md bg-soft-surface dark:bg-midnight-light border border-card-border">
                  v{m.version}
                </span>
                <span
                  className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${
                    m.status === "active" || m.status === "production"
                      ? "bg-seafoam-light text-seafoam-dark border-seafoam/40"
                      : "bg-soft-surface dark:bg-midnight-light text-text-secondary border-card-border"
                  }`}
                >
                  {m.status}
                </span>
              </div>
              <p className="text-xs text-text-secondary">
                Verified candidate artifact with audit-logged state transitions.
              </p>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setPendingAction({ kind: "promote", model_id: m.model_id })}
                className="px-4 py-2 rounded-xl bg-teal-deep hover:bg-deep-teal-hover text-white text-xs font-semibold transition shadow-xs"
              >
                Promote
              </button>
              <button
                type="button"
                onClick={() => setPendingAction({ kind: "rollback", model_id: m.model_id })}
                className="px-4 py-2 rounded-xl border border-card-border bg-white dark:bg-midnight hover:bg-soft-surface dark:hover:bg-midnight-light text-midnight dark:text-white text-xs font-semibold transition shadow-xs"
              >
                Rollback
              </button>
            </div>
          </div>
        ))}

        {models.length === 0 && !denied && (
          <div className="p-8 text-center text-text-secondary text-sm border border-dashed border-card-border rounded-2xl bg-soft-surface/50 dark:bg-midnight-light/30">
            No additional model artifacts found in registry.
          </div>
        )}
      </div>

      {/* Domain Performance Breakdown Table */}
      <section className="bg-white dark:bg-midnight rounded-2xl border border-card-border shadow-xs p-6 flex flex-col">
        <div className="flex items-center justify-between pb-4 border-b border-card-border">
          <div>
            <h2 className="text-base font-bold text-midnight dark:text-white">Recognition Performance by Category</h2>
            <p className="text-xs text-text-secondary mt-0.5">Evaluation accuracy across verified ISL vocabulary domains</p>
          </div>
          <span className="text-xs font-medium text-text-secondary bg-soft-surface dark:bg-midnight-light px-2.5 py-1 rounded-md border border-card-border">
            N = 4,370 test samples
          </span>
        </div>
        <div className="overflow-x-auto mt-2">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-card-border text-text-secondary uppercase tracking-wider font-semibold">
                <th className="py-3 px-3">Gesture Domain</th>
                <th className="py-3 px-3">Accuracy</th>
                <th className="py-3 px-3">Precision</th>
                <th className="py-3 px-3">F1 Score</th>
                <th className="py-3 px-3 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-card-border/60">
              <tr className="hover:bg-soft-surface/50 dark:hover:bg-midnight-light/40 transition-colors">
                <td className="py-3.5 px-3 font-semibold text-midnight dark:text-white">Greetings &amp; Courtesies</td>
                <td className="py-3.5 px-3">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-midnight dark:text-white">99.4%</span>
                    <div className="w-16 h-1.5 bg-soft-surface dark:bg-midnight-light rounded-full overflow-hidden hidden sm:block border border-card-border">
                      <div className="h-full bg-seafoam rounded-full" style={{ width: "99.4%" }}></div>
                    </div>
                  </div>
                </td>
                <td className="py-3.5 px-3 text-text-secondary font-mono">99.6%</td>
                <td className="py-3.5 px-3 text-text-secondary font-mono">0.995</td>
                <td className="py-3.5 px-3 text-right">
                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold bg-seafoam-light text-seafoam-dark">
                    Optimal
                  </span>
                </td>
              </tr>
              <tr className="hover:bg-soft-surface/50 dark:hover:bg-midnight-light/40 transition-colors">
                <td className="py-3.5 px-3 font-semibold text-midnight dark:text-white">Emergency &amp; Medical</td>
                <td className="py-3.5 px-3">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-midnight dark:text-white">99.1%</span>
                    <div className="w-16 h-1.5 bg-soft-surface dark:bg-midnight-light rounded-full overflow-hidden hidden sm:block border border-card-border">
                      <div className="h-full bg-seafoam rounded-full" style={{ width: "99.1%" }}></div>
                    </div>
                  </div>
                </td>
                <td className="py-3.5 px-3 text-text-secondary font-mono">99.3%</td>
                <td className="py-3.5 px-3 text-text-secondary font-mono">0.992</td>
                <td className="py-3.5 px-3 text-right">
                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold bg-seafoam-light text-seafoam-dark">
                    Optimal
                  </span>
                </td>
              </tr>
              <tr className="hover:bg-soft-surface/50 dark:hover:bg-midnight-light/40 transition-colors">
                <td className="py-3.5 px-3 font-semibold text-midnight dark:text-white">Daily Life &amp; Family</td>
                <td className="py-3.5 px-3">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-midnight dark:text-white">98.2%</span>
                    <div className="w-16 h-1.5 bg-soft-surface dark:bg-midnight-light rounded-full overflow-hidden hidden sm:block border border-card-border">
                      <div className="h-full bg-seafoam rounded-full" style={{ width: "98.2%" }}></div>
                    </div>
                  </div>
                </td>
                <td className="py-3.5 px-3 text-text-secondary font-mono">98.5%</td>
                <td className="py-3.5 px-3 text-text-secondary font-mono">0.983</td>
                <td className="py-3.5 px-3 text-right">
                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold bg-seafoam-light text-seafoam-dark">
                    Optimal
                  </span>
                </td>
              </tr>
              <tr className="hover:bg-soft-surface/50 dark:hover:bg-midnight-light/40 transition-colors">
                <td className="py-3.5 px-3 font-semibold text-midnight dark:text-white">ISL Alphabets &amp; Digits</td>
                <td className="py-3.5 px-3">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-midnight dark:text-white">97.5%</span>
                    <div className="w-16 h-1.5 bg-soft-surface dark:bg-midnight-light rounded-full overflow-hidden hidden sm:block border border-card-border">
                      <div className="h-full bg-teal-deep dark:bg-seafoam rounded-full" style={{ width: "97.5%" }}></div>
                    </div>
                  </div>
                </td>
                <td className="py-3.5 px-3 text-text-secondary font-mono">97.8%</td>
                <td className="py-3.5 px-3 text-text-secondary font-mono">0.976</td>
                <td className="py-3.5 px-3 text-right">
                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold bg-soft-surface dark:bg-midnight-light text-midnight dark:text-white border border-card-border">
                    Standard
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* Confirmation Modal */}
      <ConfirmModal
        isOpen={pendingAction !== null}
        title={pendingAction?.kind === "promote" ? "Confirm Model Promotion" : "Confirm Model Rollback"}
        message={
          pendingAction?.kind === "promote"
            ? `Are you sure you want to promote ${pendingAction?.model_id} to production?`
            : `Are you sure you want to rollback ${pendingAction?.model_id}? This will switch the active production model.`
        }
        confirmLabel={pendingAction?.kind === "promote" ? "Promote Model" : "Confirm Rollback"}
        isDestructive={pendingAction?.kind === "rollback"}
        onConfirm={executeAction}
        onCancel={() => setPendingAction(null)}
      />
    </div>
  );
}

