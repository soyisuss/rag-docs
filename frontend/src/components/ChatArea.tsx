import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { 
  Send, 
  RotateCcw, 
  Clock,
  Copy,
  Check,
  AlertCircle
} from 'lucide-react';
import { ChatMessage } from '../types';
import { CitationCard } from './CitationCard';

interface ChatAreaProps {
  messages: ChatMessage[];
  isLoading: boolean;
  onSendMessage: (query: string) => void;
  onClearChat: () => void;
}

const SAMPLE_QUESTIONS = [
  "¿Cuáles son los puntos y conclusiones clave?",
  "¿Qué requisitos u obligaciones se especifican?",
  "¿Cuál es el resumen ejecutivo del documento?",
  "¿Qué procedimientos o metodologías se describen?"
];

export const ChatArea: React.FC<ChatAreaProps> = ({
  messages,
  isLoading,
  onSendMessage,
  onClearChat,
}) => {
  const [inputQuery, setInputQuery] = useState('');
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputQuery.trim() || isLoading) return;

    onSendMessage(inputQuery.trim());
    setInputQuery('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputQuery(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`;
  };

  const handleCopyText = async (id: string, text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch (err) {
      console.error('Failed to copy text', err);
    }
  };

  return (
    <main className="flex-1 flex flex-col h-[calc(100vh-3.5rem)] bg-zinc-950 relative overflow-hidden">
      {/* Top action bar */}
      <div className="h-9 border-b border-zinc-800/80 px-4 flex items-center justify-between text-xs text-zinc-400 select-none bg-zinc-950">
        <span className="text-[11px] font-medium text-zinc-400">
          {messages.length > 0 ? `${messages.length} mensajes` : 'Conversación vacía'}
        </span>
        {messages.length > 0 && (
          <button
            onClick={onClearChat}
            className="flex items-center gap-1.5 text-zinc-400 hover:text-zinc-200 text-xs transition-colors py-0.5 px-1.5 rounded hover:bg-zinc-900 focus:outline-none focus:ring-1 focus:ring-zinc-600"
            title="Limpiar conversación actual"
            aria-label="Limpiar historial de conversación"
          >
            <RotateCcw className="w-3 h-3" />
            <span>Limpiar</span>
          </button>
        )}
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6">
        {messages.length === 0 ? (
          <div className="max-w-xl mx-auto py-16 px-4 text-center space-y-6 animate-fadeIn">
            <div className="space-y-2">
              <h2 className="text-lg font-semibold text-zinc-100 tracking-tight">
                Consulta tus documentos
              </h2>
              <p className="text-xs text-zinc-400 max-w-sm mx-auto leading-relaxed">
                Obtén respuestas verificadas con citas exactas por página a partir de los archivos PDF cargados.
              </p>
            </div>

            {/* Quick prompts */}
            <div className="pt-2 max-w-md mx-auto space-y-2">
              {SAMPLE_QUESTIONS.map((q, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    setInputQuery(q);
                    onSendMessage(q);
                  }}
                  className="w-full p-2.5 rounded-lg bg-zinc-900/60 hover:bg-zinc-900 border border-zinc-800/80 hover:border-zinc-700 text-xs text-zinc-300 hover:text-zinc-100 transition-colors text-left flex items-center justify-between group focus:outline-none focus:ring-1 focus:ring-zinc-600"
                >
                  <span className="truncate">{q}</span>
                  <span className="text-zinc-400 group-hover:text-zinc-200 text-[10px] font-mono ml-2">↵</span>
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex flex-col max-w-3xl mx-auto ${
                msg.role === 'user' ? 'items-end' : 'items-start w-full'
              }`}
            >
              {/* Message block */}
              {msg.role === 'user' ? (
                <div className="bg-zinc-900 border border-zinc-800 text-zinc-100 px-4 py-2.5 rounded-xl text-xs leading-relaxed max-w-[85%] md:max-w-xl whitespace-pre-wrap shadow-sm">
                  {msg.content}
                </div>
              ) : (
                <div className="w-full space-y-3 py-1">
                  {/* Toolbar */}
                  <div className="flex items-center justify-between text-xs text-zinc-400 border-b border-zinc-850 pb-1.5">
                    <span className="text-[11px] font-mono uppercase tracking-wider text-zinc-400">
                      Respuesta
                    </span>
                    <button
                      type="button"
                      onClick={() => handleCopyText(msg.id, msg.content)}
                      className="flex items-center gap-1 text-[11px] text-zinc-400 hover:text-zinc-200 px-1.5 py-0.5 rounded hover:bg-zinc-900 transition-colors"
                      title="Copiar texto"
                      aria-label="Copiar respuesta"
                    >
                      {copiedId === msg.id ? (
                        <>
                          <Check className="w-3 h-3 text-emerald-400" />
                          <span className="text-emerald-400">Copiado</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3 h-3" />
                          <span>Copiar</span>
                        </>
                      )}
                    </button>
                  </div>

                  {/* Guardrail Refusal Notice */}
                  {msg.guardrail_passed === false && (
                    <div className="p-3 rounded-lg bg-zinc-900 border border-amber-900/40 text-amber-300 text-xs flex items-start gap-2.5">
                      <AlertCircle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
                      <div className="space-y-1">
                        <p className="font-medium text-amber-200">
                          Información insuficiente en los documentos cargados
                        </p>
                        <p className="text-zinc-400 text-xs leading-relaxed">
                          La coincidencia semántica no alcanzó el umbral mínimo (70%). Por favor, intenta formular la consulta con términos o palabras clave más específicas.
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Prose Content */}
                  <div className="prose prose-invert prose-xs max-w-none space-y-2 text-zinc-200 leading-relaxed font-sans">
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>

                  {/* Sources List */}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="pt-2 border-t border-zinc-850 space-y-1.5">
                      <span className="text-[11px] font-mono uppercase tracking-wider text-zinc-400 block mb-1">
                        Fuentes ({msg.sources.length})
                      </span>
                      <div className="space-y-1.5">
                        {msg.sources.map((cit, idx) => (
                          <CitationCard key={idx} citation={cit} index={idx} />
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Timestamp */}
              <div className="flex items-center gap-1 text-[10px] text-zinc-500 mt-1 px-1">
                <Clock className="w-2.5 h-2.5" />
                <span>
                  {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            </div>
          ))
        )}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="max-w-3xl mx-auto flex items-center gap-2.5 text-xs text-zinc-400 py-2 animate-fadeIn">
            <div className="w-3.5 h-3.5 border-2 border-zinc-400 border-t-transparent rounded-full animate-spin" />
            <span>Consultando fuentes y sintetizando respuesta...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Console */}
      <div className="p-3 md:p-4 border-t border-zinc-800/80 bg-zinc-950">
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
          <div className="relative flex items-end gap-2 bg-zinc-900 border border-zinc-800 focus-within:border-zinc-600 rounded-xl px-3.5 py-2.5 transition-colors shadow-sm">
            <textarea
              ref={textareaRef}
              rows={1}
              value={inputQuery}
              onChange={handleTextareaChange}
              onKeyDown={handleKeyDown}
              placeholder="Haz una pregunta sobre tus documentos..."
              aria-label="Haz una pregunta sobre tus documentos"
              disabled={isLoading}
              className="flex-1 bg-transparent border-none text-xs text-zinc-100 placeholder-zinc-400 focus:outline-none resize-none max-h-32 disabled:opacity-40"
            />

            <button
              type="submit"
              disabled={!inputQuery.trim() || isLoading}
              className="w-7 h-7 rounded-lg bg-zinc-100 text-zinc-950 hover:bg-white disabled:bg-zinc-800 disabled:text-zinc-600 flex items-center justify-center transition-all flex-shrink-0 disabled:opacity-30 focus:outline-none focus:ring-1 focus:ring-zinc-400"
              title="Enviar consulta (Enter)"
              aria-label="Enviar consulta"
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </div>
        </form>
        <p className="text-[11px] text-center text-zinc-400 mt-2 select-none">
          Presiona <kbd className="font-mono text-zinc-400 bg-zinc-900 px-1 py-0.5 rounded border border-zinc-800">Enter</kbd> para enviar, <kbd className="font-mono text-zinc-400 bg-zinc-900 px-1 py-0.5 rounded border border-zinc-800">Shift + Enter</kbd> para nueva línea.
        </p>
      </div>
    </main>
  );
};
