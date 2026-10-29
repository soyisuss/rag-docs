import React, { useState } from 'react';
import { X, UserPlus, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { api } from '../services/api';

interface RegisterModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSwitchToLogin?: () => void;
}

export const RegisterModal: React.FC<RegisterModalProps> = ({ 
  isOpen, 
  onClose,
  onSwitchToLogin,
}) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!email.trim() || !password.trim()) {
      setError('Por favor completa todos los campos.');
      return;
    }

    if (password.length < 6) {
      setError('La contraseña debe tener al menos 6 caracteres.');
      return;
    }

    setLoading(true);
    try {
      const res = await api.register(email.trim(), password);
      setSuccess(`¡Cuenta creada con éxito! Bienvenido, ${res.email}.`);
      setEmail('');
      setPassword('');
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Ocurrió un error inesperado al registrar.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-zinc-950/80 backdrop-blur-sm animate-fade-in">
      <div 
        className="w-full max-w-md bg-zinc-900 border border-zinc-800 rounded-xl shadow-2xl p-6 relative"
        role="dialog"
        aria-modal="true"
        aria-labelledby="register-modal-title"
      >
        <button
          onClick={onClose}
          type="button"
          aria-label="Cerrar modal"
          className="absolute top-4 right-4 p-1.5 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3 mb-5">
          <div className="w-10 h-10 rounded-lg bg-zinc-800 border border-zinc-700 flex items-center justify-center text-zinc-100">
            <UserPlus className="w-5 h-5" />
          </div>
          <div>
            <h2 id="register-modal-title" className="text-base font-semibold text-zinc-100">
              Crear cuenta personal
            </h2>
            <p className="text-xs text-zinc-400">
              Regístrate para guardar tu actividad en Neon
            </p>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-red-950/40 border border-red-800/60 flex items-start gap-2.5 text-xs text-red-200">
            <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="mb-4 p-3 rounded-lg bg-emerald-950/40 border border-emerald-800/60 flex items-start gap-2.5 text-xs text-emerald-200">
            <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            <span>{success}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-zinc-300 mb-1.5" htmlFor="reg-email">
              Correo electrónico
            </label>
            <input
              id="reg-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="tu@correo.com"
              required
              disabled={loading}
              className="w-full px-3 py-2 text-sm bg-zinc-950 border border-zinc-700 rounded-lg text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-1 focus:ring-zinc-400 focus:border-zinc-400 transition-colors disabled:opacity-50"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-zinc-300 mb-1.5" htmlFor="reg-password">
              Contraseña
            </label>
            <input
              id="reg-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Mínimo 6 caracteres"
              required
              minLength={6}
              disabled={loading}
              className="w-full px-3 py-2 text-sm bg-zinc-950 border border-zinc-700 rounded-lg text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-1 focus:ring-zinc-400 focus:border-zinc-400 transition-colors disabled:opacity-50"
            />
          </div>

          <div className="pt-2 flex items-center justify-between">
            {onSwitchToLogin ? (
              <button
                type="button"
                onClick={() => {
                  onClose();
                  onSwitchToLogin();
                }}
                className="text-xs text-zinc-400 hover:text-zinc-200 transition-colors"
              >
                ¿Ya tienes cuenta? <span className="underline text-zinc-300 font-medium">Inicia sesión</span>
              </button>
            ) : <div />}

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={onClose}
                disabled={loading}
                className="px-3.5 py-2 text-xs font-medium text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 rounded-lg transition-colors"
              >
                Cerrar
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 text-xs font-medium text-zinc-950 bg-zinc-100 hover:bg-white rounded-lg transition-colors flex items-center gap-1.5 disabled:opacity-50 shadow-sm"
              >
                {loading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                {loading ? 'Creando cuenta...' : 'Crear cuenta'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};
