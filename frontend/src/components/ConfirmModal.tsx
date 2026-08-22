import React, { useEffect, useRef } from 'react';

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

export const ConfirmModal: React.FC<ConfirmModalProps> = ({
  isOpen,
  title,
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  isDestructive = false,
  onConfirm,
  onCancel,
}) => {
  const confirmButtonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (isOpen) {
      confirmButtonRef.current?.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onCancel();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onCancel]);

  if (!isOpen) return null;

  return (
    <div
      className="modal-overlay"
      onClick={onCancel}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      aria-describedby="modal-desc"
    >
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <header className="modal-header">
          <h3 id="modal-title" className="modal-title">{title}</h3>
        </header>
        <div className="modal-body">
          <p id="modal-desc">{message}</p>
        </div>
        <footer className="modal-actions">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onCancel}
            aria-label="Cancel action"
          >
            {cancelLabel}
          </button>
          <button
            ref={confirmButtonRef}
            type="button"
            className={`btn ${isDestructive ? 'btn-danger' : 'btn-primary'}`}
            onClick={onConfirm}
            aria-label={confirmLabel}
          >
            {confirmLabel}
          </button>
        </footer>
      </div>
    </div>
  );
};
