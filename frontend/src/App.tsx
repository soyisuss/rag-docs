import React, { useState, useEffect } from 'react';
import { CheckCircle2, AlertCircle, X } from 'lucide-react';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { ChatArea } from './components/ChatArea';
import { DeleteModal } from './components/DeleteModal';
import { RegisterModal } from './components/RegisterModal';
import { LoginModal } from './components/LoginModal';
import { api } from './services/api';
import { DocumentItem, ChatMessage, UserProfile } from './types';

export const App: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [isLoadingDocs, setIsLoadingDocs] = useState<boolean>(true);
  const [serverStatus, setServerStatus] = useState<'online' | 'offline' | 'checking'>('checking');
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(false);

  // Chat State
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isQuerying, setIsQuerying] = useState<boolean>(false);

  // Toast Notification State
  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  // Auth & Modal States
  const [registerModalOpen, setRegisterModalOpen] = useState<boolean>(false);
  const [loginModalOpen, setLoginModalOpen] = useState<boolean>(false);
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(() => {
    try {
      const stored = localStorage.getItem('yael_user');
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  });

  const handleLoginSuccess = (user: UserProfile, token: string) => {
    localStorage.setItem('yael_token', token);
    localStorage.setItem('yael_user', JSON.stringify(user));
    setCurrentUser(user);
    setToast({
      type: 'success',
      message: `¡Bienvenido de nuevo, ${user.email}!`
    });
  };

  const handleLogout = async () => {
    try {
      await api.logout();
    } catch {
      // Ignorar errores de red en logout
    }
    localStorage.removeItem('yael_token');
    localStorage.removeItem('yael_user');
    setCurrentUser(null);
    setToast({
      type: 'success',
      message: 'Sesión cerrada correctamente.'
    });
  };

  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(() => setToast(null), 5000);
    return () => clearTimeout(timer);
  }, [toast]);

  // Deletion Modal State
  const [deleteModal, setDeleteModal] = useState<{
    isOpen: boolean;
    docName: string;
    isDeleting: boolean;
  }>({
    isOpen: false,
    docName: '',
    isDeleting: false,
  });

  // Load initial health & documents
  const loadInitialData = async () => {
    setIsLoadingDocs(true);
    try {
      await api.getHealth();
      setServerStatus('online');

      const docsData = await api.getDocuments();
      setDocuments(docsData.documents);
    } catch (err) {
      console.error('Connection error:', err);
      setServerStatus('offline');
    } finally {
      setIsLoadingDocs(false);
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  // Handlers
  const handleUpload = async (files: File[]) => {
    await api.uploadDocuments(files);
    const docsData = await api.getDocuments();
    setDocuments(docsData.documents);
    setToast({
      type: 'success',
      message: `${files.length} documento(s) indexado(s).`
    });
  };

  const handleOpenDelete = (docName: string) => {
    setDeleteModal({
      isOpen: true,
      docName,
      isDeleting: false,
    });
  };

  const handleConfirmDelete = async () => {
    const docToDelete = deleteModal.docName;
    if (!docToDelete) return;

    setDeleteModal(prev => ({ ...prev, isDeleting: true }));
    try {
      await api.deleteDocument(docToDelete);
      setDocuments(prev => prev.filter(d => d.name !== docToDelete));
      setDeleteModal({ isOpen: false, docName: '', isDeleting: false });
      setToast({
        type: 'success',
        message: `"${docToDelete}" eliminado correctamente.`
      });
    } catch (err: any) {
      setToast({
        type: 'error',
        message: `Error al eliminar: ${err.message || 'Error del servidor'}`
      });
      setDeleteModal(prev => ({ ...prev, isDeleting: false }));
    }
  };

  const handleSendMessage = async (queryText: string) => {
    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: queryText,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMsg]);
    setIsQuerying(true);

    try {
      const response = await api.sendQuery(queryText);

      const assistantMsg: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.answer,
        guardrail_passed: response.guardrail_passed,
        max_score: response.max_score,
        sources: response.sources,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: `assistant-err-${Date.now()}`,
        role: 'assistant',
        content: `No se pudo conectar con el servidor: ${err.message || 'Verifica la conexión.'}`,
        guardrail_passed: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsQuerying(false);
    }
  };

  const handleClearChat = () => {
    if (messages.length === 0) return;
    setMessages([]);
    setToast({
      type: 'success',
      message: 'Conversación reiniciada.'
    });
  };

  return (
    <div className="flex flex-col h-screen bg-zinc-950 text-zinc-100 overflow-hidden font-sans">
      <Navbar
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        onOpenRegister={() => setRegisterModalOpen(true)}
        onOpenLogin={() => setLoginModalOpen(true)}
        onLogout={handleLogout}
        currentUser={currentUser}
        sidebarOpen={sidebarOpen}
        docCount={documents.length}
        serverStatus={serverStatus}
      />

      <div className="flex flex-1 overflow-hidden relative">
        <Sidebar
          documents={documents}
          isLoading={isLoadingDocs}
          onRefresh={loadInitialData}
          onUpload={handleUpload}
          onSelectDelete={handleOpenDelete}
          isOpen={sidebarOpen}
        />

        <ChatArea
          messages={messages}
          isLoading={isQuerying}
          onSendMessage={handleSendMessage}
          onClearChat={handleClearChat}
        />
      </div>

      <DeleteModal
        isOpen={deleteModal.isOpen}
        documentName={deleteModal.docName}
        isDeleting={deleteModal.isDeleting}
        onConfirm={handleConfirmDelete}
        onCancel={() => setDeleteModal({ isOpen: false, docName: '', isDeleting: false })}
      />

      <RegisterModal
        isOpen={registerModalOpen}
        onClose={() => setRegisterModalOpen(false)}
        onSwitchToLogin={() => setLoginModalOpen(true)}
      />

      <LoginModal
        isOpen={loginModalOpen}
        onClose={() => setLoginModalOpen(false)}
        onSuccess={handleLoginSuccess}
        onSwitchToRegister={() => setRegisterModalOpen(true)}
      />

      {/* Minimalist Floating Toast */}
      {toast && (
        <div
          role="alert"
          className={`fixed bottom-4 right-4 z-50 max-w-sm px-3.5 py-2.5 rounded-lg border shadow-xl flex items-center gap-2.5 transition-all animate-fadeIn ${
            toast.type === 'error'
              ? 'bg-zinc-900 border-red-900/60 text-red-300'
              : 'bg-zinc-900 border-zinc-800 text-zinc-200'
          }`}
        >
          {toast.type === 'error' ? (
            <AlertCircle className="w-3.5 h-3.5 text-red-400 flex-shrink-0" />
          ) : (
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
          )}
          <span className="flex-1 text-xs">
            {toast.message}
          </span>
          <button
            type="button"
            onClick={() => setToast(null)}
            className="text-zinc-500 hover:text-zinc-300 p-0.5 rounded transition-colors"
            aria-label="Cerrar notificación"
          >
            <X className="w-3 h-3" />
          </button>
        </div>
      )}
    </div>
  );
};

export default App;
