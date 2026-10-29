import React, { useState } from 'react';
import { ChevronDown, ChevronUp, FileText } from 'lucide-react';
import { Citation } from '../types';

interface CitationCardProps {
  citation: Citation;
  index: number;
}

export const CitationCard: React.FC<CitationCardProps> = ({ citation }) => {
  const [expanded, setExpanded] = useState(false);
  const scorePercent = Math.min(Math.round(citation.score * 100), 100);

  return (
    <div className="border border-zinc-800/80 bg-zinc-900/60 hover:bg-zinc-900 rounded-lg text-xs transition-colors overflow-hidden">
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        aria-expanded={expanded}
        className="w-full flex items-center justify-between p-2.5 text-left gap-2 select-none focus:outline-none focus:ring-1 focus:ring-zinc-600 transition-colors"
      >
        <div className="flex items-center gap-2 min-w-0 flex-1">
          <FileText className="w-3.5 h-3.5 text-zinc-400 flex-shrink-0" />
          <span className="font-medium text-zinc-200 truncate" title={citation.document}>
            {citation.document}
          </span>
          <span className="text-[11px] font-mono text-zinc-400 bg-zinc-950 px-1.5 py-0.5 rounded border border-zinc-800 whitespace-nowrap">
            Pág. {citation.page}
          </span>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0">
          <span className="text-[11px] font-mono font-medium text-zinc-400">
            {scorePercent}%
          </span>
          <span className="text-zinc-500 hover:text-zinc-300 flex items-center">
            {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </span>
        </div>
      </button>

      {expanded && (
        <div className="mx-2.5 mb-2.5 p-3 rounded bg-zinc-950 border border-zinc-800/80 text-xs text-zinc-300 font-sans leading-relaxed whitespace-pre-wrap">
          {citation.snippet}
        </div>
      )}
    </div>
  );
};
