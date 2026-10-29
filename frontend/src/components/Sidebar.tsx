import React, { useState, useRef } from 'react';
import { 
  FileText, 
  Plus, 
  Trash2, 
  Search, 
  RefreshCw, 
  CheckCircle2, 
  AlertCircle,
  X,
  Upload
} from 'lucide-react';
import { DocumentItem } from '../types';

interface SidebarProps {
  documents: DocumentItem[];
  isLoading: boolean;
  isAuthenticated: boolean;
  onRequireLogin?: () => void;
  onRefresh: () => void;
  onUpload: (files: File[]) => Promise<void>;
  onSelectDelete: (docName: string) => void;
  isOpen: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({
  documents,
  isLoading,
  isAuthenticated,
  onRequireLogin,
  onRefresh,
  onUpload,
  onSelectDelete,
  isOpen,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadFeedback, setUploadFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const filteredDocs = documents.filter(d => 
    d.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleFiles = async (files: FileList | null) => {
    if (!isAuthenticated) {
      onRequireLogin?.();
      return;
    }
    if (!files || files.length === 0) return;

    const pdfFiles: File[] = [];
    for (let i = 0; i < files.length; i++) {
      if (files[i].name.toLowerCase().endsWith('.pdf')) {
        pdfFiles.push(files[i]);
      }
    }

    if (pdfFiles.length === 0) {
      setUploadFeedback({ type: 'error', message: 'Sube solo archivos en formato PDF.' });
      setTimeout(() => setUploadFeedback(null), 5000);
      return;
    }

    setIsUploading(true);
    setUploadFeedback(null);
    try {
      await onUpload(pdfFiles);
      setUploadFeedback({
        type: 'success',
        message: `${pdfFiles.length} documento(s) procesado(s).`
      });
      setTimeout(() => setUploadFeedback(null), 4000);
    } catch (err: any) {
      setUploadFeedback({
        type: 'error',
        message: err.message || 'Error al procesar el archivo.'
      });
      setTimeout(() => setUploadFeedback(null), 6000);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFiles(e.dataTransfer.files);
  };

  return (
    <aside
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
      onDragLeave={(e) => {
        if (!e.currentTarget.contains(e.relatedTarget as Node)) {
          setIsDragging(false);
        }
      }}
      onDrop={handleDrop}
      className={`
        fixed inset-y-14 left-0 z-20 w-72 bg-zinc-950 border-r border-zinc-800/80 flex flex-col transition-transform duration-200 ease-in-out md:translate-x-0 md:static md:h-[calc(100vh-3.5rem)]
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
      `}
    >
      {/* Invisible file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf"
        multiple
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />

      {/* Drag Over Overlay */}
      {isDragging && (
        <div className="absolute inset-0 z-30 bg-zinc-900/90 border-2 border-dashed border-zinc-400 m-2 rounded-xl flex flex-col items-center justify-center gap-2 pointer-events-none animate-fadeIn">
          <Upload className="w-6 h-6 text-zinc-100" />
          <span className="text-xs font-medium text-zinc-200">Suelta los archivos PDF aquí</span>
        </div>
      )}

      {/* Header section */}
      <div className="p-3.5 border-b border-zinc-800/80 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-zinc-200">Documentos</span>
            <span className="text-[11px] font-mono text-zinc-400 bg-zinc-900 px-1.5 py-0.5 rounded border border-zinc-800">
              {documents.length}
            </span>
          </div>

          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={onRefresh}
              disabled={isLoading}
              className="p-1 rounded text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900 transition-colors disabled:opacity-40 focus:outline-none focus:ring-1 focus:ring-zinc-600"
              title="Actualizar biblioteca"
              aria-label="Actualizar lista de documentos"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            </button>

            <button
              type="button"
              onClick={() => {
                if (!isAuthenticated) {
                  onRequireLogin?.();
                } else {
                  fileInputRef.current?.click();
                }
              }}
              disabled={isUploading}
              className="p-1 rounded text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900 transition-colors disabled:opacity-40 focus:outline-none focus:ring-1 focus:ring-zinc-600"
              title="Cargar nuevo PDF"
              aria-label="Cargar nuevo PDF"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Minimal Search Input */}
        <div className="relative">
          <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-zinc-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Buscar documento..."
            aria-label="Buscar documento por nombre"
            className="w-full bg-zinc-900/80 border border-zinc-800/90 rounded-lg pl-8 pr-3 py-1.5 text-xs text-zinc-200 placeholder-zinc-400 focus:outline-none focus:border-zinc-500 focus:ring-1 focus:ring-zinc-500 transition-colors"
          />
        </div>
      </div>

      {/* Document List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {isLoading && documents.length === 0 ? (
          <div className="text-center py-12 space-y-2 text-zinc-500">
            <div className="w-4 h-4 border-2 border-zinc-400 border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-xs">Cargando archivos...</p>
          </div>
        ) : filteredDocs.length === 0 ? (
          <div className="text-center py-12 px-4 space-y-1 text-zinc-500">
            <FileText className="w-6 h-6 mx-auto mb-1 text-zinc-600" />
            <p className="text-xs font-medium text-zinc-400">Sin documentos</p>
            <p className="text-[11px] text-zinc-500">
              {searchTerm ? 'No hay coincidencias' : 'Arrastra o añade un PDF'}
            </p>
          </div>
        ) : (
          filteredDocs.map((doc) => (
            <div
              key={doc.name}
              className="group flex items-center justify-between p-2 rounded-lg hover:bg-zinc-900 transition-colors text-xs"
            >
              <div className="flex items-center gap-2 min-w-0 flex-1 pr-1.5">
                <FileText className="w-3.5 h-3.5 text-zinc-400 flex-shrink-0" />
                <span className="text-zinc-300 group-hover:text-zinc-100 font-medium truncate" title={doc.name}>
                  {doc.name}
                </span>
              </div>

              <button
                type="button"
                onClick={() => onSelectDelete(doc.name)}
                className="opacity-0 group-hover:opacity-100 focus:opacity-100 p-1 rounded text-zinc-500 hover:text-red-400 hover:bg-zinc-800 transition-all flex-shrink-0 focus:outline-none focus:ring-1 focus:ring-red-400"
                title={`Eliminar ${doc.name}`}
                aria-label={`Eliminar documento ${doc.name}`}
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))
        )}
      </div>

      {/* Bottom Compact Action */}
      <div className="p-3 border-t border-zinc-800/80 bg-zinc-950">
        <button
          type="button"
          onClick={() => {
            if (!isAuthenticated) {
              onRequireLogin?.();
            } else {
              fileInputRef.current?.click();
            }
          }}
          disabled={isUploading}
          className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-lg border border-zinc-800 hover:border-zinc-700 bg-zinc-900/60 hover:bg-zinc-900 text-xs font-medium text-zinc-300 hover:text-zinc-100 transition-colors disabled:opacity-50"
        >
          {isUploading ? (
            <>
              <span className="w-3.5 h-3.5 border-2 border-zinc-400 border-t-transparent rounded-full animate-spin" />
              <span>Indexando...</span>
            </>
          ) : (
            <>
              <Plus className="w-3.5 h-3.5 text-zinc-400" />
              <span>Cargar PDF</span>
            </>
          )}
        </button>

        {/* Feedback message */}
        {uploadFeedback && (
          <div
            role="alert"
            className={`mt-2 p-2 rounded-lg text-xs flex items-center justify-between gap-1.5 animate-fadeIn ${
              uploadFeedback.type === 'success'
                ? 'bg-zinc-900 border border-emerald-800/60 text-emerald-400'
                : 'bg-zinc-900 border border-red-800/60 text-red-400'
            }`}
          >
            <div className="flex items-center gap-1.5 min-w-0">
              {uploadFeedback.type === 'success' ? (
                <CheckCircle2 className="w-3.5 h-3.5 flex-shrink-0 text-emerald-400" />
              ) : (
                <AlertCircle className="w-3.5 h-3.5 flex-shrink-0 text-red-400" />
              )}
              <span className="text-[11px] leading-tight truncate">{uploadFeedback.message}</span>
            </div>
            <button
              type="button"
              onClick={() => setUploadFeedback(null)}
              className="text-zinc-500 hover:text-zinc-300 p-0.5 rounded transition-colors flex-shrink-0"
              aria-label="Cerrar mensaje"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
        )}
      </div>
    </aside>
  );
};
