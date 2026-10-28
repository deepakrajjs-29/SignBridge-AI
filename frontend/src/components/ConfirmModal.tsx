import React, { useEffect, useRef } from "react";

interface ConfirmModalProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  isDestructive?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function ConfirmModal({
  isOpen,
  title,
  message,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  isDestructive = false,
  onConfirm,
  onCancel,
}: ConfirmModalProps) {
  const cancelBtnRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (isOpen) {
      cancelBtnRef.current?.focus();
      const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key === "Escape") onCancel();
      };
      window.addEventListener("keydown", handleKeyDown);
      return () => window.removeEventListener("keydown", handleKeyDown);
    }
  }, [isOpen, onCancel]);

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-midnight/70 backdrop-blur-sm animate-in fade-in duration-150"
    >
      <div className="bg-white dark:bg-midnight border border-card-border rounded-2xl shadow-2xl max-w-md w-full p-6 space-y-4">
        <h3 id="confirm-modal-title" className="text-lg font-bold text-midnight dark:text-white">
          {title}
        </h3>
        <p className="text-sm text-text-secondary leading-relaxed">
          {message}
        </p>
        <div className="flex justify-end gap-3 pt-2">
          <button
            ref={cancelBtnRef}
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-xs sm:text-sm font-semibold text-midnight dark:text-white bg-soft-surface dark:bg-midnight-light hover:bg-white dark:hover:bg-midnight border border-card-border rounded-xl transition shadow-xs"
          >
            {cancelLabel}
          </button>
          <button
            type="button"
            onClick={onConfirm}
            className={`px-4 py-2 text-xs sm:text-sm font-semibold text-white rounded-xl transition shadow-xs ${
              isDestructive
                ? "bg-rose-600 hover:bg-rose-700"
                : "bg-teal-deep hover:bg-deep-teal-hover"
            }`}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
