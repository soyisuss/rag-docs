import React, { useEffect, useRef } from 'react';
import { Trash2, X } from 'lucide-react';

interface DeleteModalProps {
  isOpen: boolean;
  documentName: string;
  isDeleting: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export const DeleteModal: React.FC<DeleteModalProps> = ({
  isOpen,
  documentName,
  isDeleting,
  onConfirm,
  onCancel,
}) => {
  const cancelButtonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!isOpen) return;

    cancelButtonRef.current?.focus();

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && !isDeleting) {
        e.preventDefault();
        onCancel();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, isDeleting, onCancel]);

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn"
      role="dialog"
      aria-modal="true"
      aria-labelledby="delete-modal-title"
      aria-describedby="delete-modal-desc"
    >
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl max-w-sm w-full p-5 shadow-2xl relative text-left space-y-4">
        <button
          type="button"
          onClick={onCancel}
          disabled={isDeleting}
          aria-label="Cerrar modal"
          className="absolute top-4 right-4 text-zinc-400 hover:text-zinc-200 p-1 rounded-md transition-colors focus:outline-none focus:ring-1 focus:ring-zinc-600 disabled:opacity-40"
        >
          <X className="w-4 h-4" />
        </button>

        <div className="space-y-1.5">
          <h3 id="delete-modal-title" className="text-sm font-semibold text-zinc-100">
            Eliminar documento
          </h3>
          <p id="delete-modal-desc" className="text-xs text-zinc-400 leading-relaxed">
            Se eliminará el archivo y se purgarán todos sus vectores asociados en el almacén de conocimiento.
          </p>
        </div>

        <div className="p-2.5 rounded-lg bg-zinc-950 border border-zinc-800">
          <p className="text-xs font-mono text-zinc-200 truncate font-medium">
            {documentName}
          </p>
        </div>

        <div className="flex items-center justify-end gap-2 pt-1">
          <button
            ref={cancelButtonRef}
            type="button"
            onClick={onCancel}
            disabled={isDeleting}
            className="px-3 py-1.5 rounded-lg text-xs font-medium text-zinc-300 hover:text-zinc-100 hover:bg-zinc-800 transition-colors focus:outline-none focus:ring-1 focus:ring-zinc-600"
          >
            Cancelar
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={isDeleting}
            className="px-3.5 py-1.5 rounded-lg text-xs font-medium bg-red-600 hover:bg-red-500 text-white flex items-center gap-1.5 transition-colors disabled:opacity-50 focus:outline-none focus:ring-1 focus:ring-red-400"
          >
            {isDeleting ? (
              <>
                <span className="w-3 h-3 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                <span>Eliminando...</span>
              </>
            ) : (
              <>
                <Trash2 className="w-3.5 h-3.5" />
                <span>Confirmar</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
