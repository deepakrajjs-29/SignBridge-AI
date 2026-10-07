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
    <div className="space-y-6 max-w-4xl animate-in fade-in duration-200">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <ShieldCheckIcon className="w-6 h-6 text-brand-600 dark:text-brand-400" />
            Model Administration & Registry
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Manage versioned model artifacts (`SBAI-MDL-ISL-*`), promote candidates, or roll back production deployments.
          </p>
        </div>
        <button
          type="button"
          onClick={load}
          className="px-3 py-2 text-xs font-semibold rounded-lg border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 transition flex items-center gap-1.5 self-start"
        >
          <RefreshIcon className="w-3.5 h-3.5" />
          Refresh Registry
        </button>
      </div>

      {denied && (
        <div role="alert" className="p-4 rounded-xl bg-rose-50 dark:bg-rose-950/60 border border-rose-200 dark:border-rose-800 text-rose-800 dark:text-rose-200 text-sm flex items-center gap-3">
          <AlertCircleIcon className="w-5 h-5 shrink-0 text-rose-600 dark:text-rose-400" />
          <div>
            <p className="font-semibold">Authentication Required</p>
            <p className="text-xs text-rose-700 dark:text-rose-300 mt-0.5">
              Admin endpoints are RBAC-gated. Please set your bearer token in the Settings tab.
            </p>
          </div>
        </div>
      )}

      {note && !denied && (
        <div role="status" className="p-3 rounded-lg bg-brand-50 dark:bg-brand-950/60 border border-brand-200 dark:border-brand-800 text-brand-800 dark:text-brand-300 text-sm">
          {note}
        </div>
      )}

      {/* Model Cards List */}
      <div className="space-y-4">
        {models.map((m) => (
          <div
            key={m.model_id}
            className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4"
          >
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="font-bold text-slate-900 dark:text-white text-base">
                  {m.model_id}
                </span>
                <span className="text-xs font-mono text-slate-500 dark:text-slate-400">
                  v{m.version}
                </span>
                <span
                  className={`px-2 py-0.5 rounded-full text-[11px] font-semibold ${
                    m.status === "active" || m.status === "production"
                      ? "bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300"
                      : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                  }`}
                >
                  {m.status}
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Verified candidate artifact with audit-logged state transitions.
              </p>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setPendingAction({ kind: "promote", model_id: m.model_id })}
                className="px-3.5 py-1.5 rounded-lg bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold transition"
              >
                Promote
              </button>
              <button
                type="button"
                onClick={() => setPendingAction({ kind: "rollback", model_id: m.model_id })}
                className="px-3.5 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 text-xs font-semibold transition"
              >
                Rollback
              </button>
            </div>
          </div>
        ))}

        {models.length === 0 && !denied && (
          <div className="p-8 text-center text-slate-400 text-sm border border-dashed border-slate-300 dark:border-slate-800 rounded-xl">
            No additional model artifacts found in registry.
          </div>
        )}
      </div>

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
