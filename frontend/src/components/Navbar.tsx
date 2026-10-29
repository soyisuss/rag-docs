import React from 'react';
import { PanelLeft, UserPlus } from 'lucide-react';

interface NavbarProps {
  onToggleSidebar: () => void;
  onOpenRegister: () => void;
  sidebarOpen: boolean;
  docCount: number;
  serverStatus: 'online' | 'offline' | 'checking';
}

export const Navbar: React.FC<NavbarProps> = ({
  onToggleSidebar,
  onOpenRegister,
  sidebarOpen,
  serverStatus,
}) => {
  return (
    <header className="h-14 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-md px-4 sm:px-6 flex items-center justify-between sticky top-0 z-30 select-none">
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onToggleSidebar}
          aria-label={sidebarOpen ? "Ocultar panel lateral" : "Mostrar panel lateral"}
          className="p-1.5 rounded-md text-zinc-400 hover:text-zinc-100 hover:bg-zinc-900 md:hidden transition-colors focus:outline-none focus:ring-1 focus:ring-zinc-600"
          title={sidebarOpen ? "Ocultar panel lateral" : "Mostrar panel lateral"}
        >
          <PanelLeft className="w-4 h-4" />
        </button>

        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-zinc-100 text-zinc-950 flex items-center justify-center font-bold text-xs tracking-tight shadow-sm">
            Y
          </div>
          <span className="text-sm font-semibold tracking-tight text-zinc-100">
            Yael
          </span>
          <span className="text-[11px] text-zinc-500 font-mono hidden sm:inline">
            / Document Intelligence
          </span>
        </div>
      </div>

      <div className="flex items-center gap-4 text-xs">
        {/* Subtle Status Telemetry */}
        <div className="flex items-center gap-2 text-zinc-400 text-xs">
          <button
            type="button"
            onClick={onOpenRegister}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-zinc-200 hover:text-white transition-colors"
          >
            <UserPlus className="w-3.5 h-3.5" />
            <span>Registrarse</span>
          </button>

          <span
            className={`w-2 h-2 rounded-full transition-colors ${
              serverStatus === 'online'
                ? 'bg-emerald-500'
                : serverStatus === 'checking'
                ? 'bg-amber-500'
                : 'bg-red-500'
            }`}
          />
          <span className="hidden sm:inline font-medium text-zinc-400">
            {serverStatus === 'online'
              ? 'Sistema Operativo'
              : serverStatus === 'checking'
              ? 'Conectando...'
              : 'Desconectado'}
          </span>
        </div>
      </div>
    </header>
  );
};
