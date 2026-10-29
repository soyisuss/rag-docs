import { 
  ChatResponse, 
  DocumentListResponse, 
  UploadResponse, 
  DeleteResponse, 
  HealthResponse,
  RegisterResponse,
  LoginResponse
} from '../types';

const RAW_BASE_URL = import.meta.env.VITE_API_URL || '';
const BASE_URL = RAW_BASE_URL.replace(/\/+$/, '');

function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem('yael_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export const api = {
  async getHealth(): Promise<HealthResponse> {
    const res = await fetch(`${BASE_URL}/api/health`);
    if (!res.ok) throw new Error(`Error ${res.status}: Fallo al conectar con el servidor`);
    return res.json();
  },

  async getDocuments(): Promise<DocumentListResponse> {
    const res = await fetch(`${BASE_URL}/api/documents`, {
      headers: {
        ...getAuthHeaders(),
      },
    });
    if (!res.ok) throw new Error(`Error ${res.status}: Fallo al obtener los documentos`);
    return res.json();
  },

  async uploadDocuments(files: File[]): Promise<UploadResponse> {
    const formData = new FormData();
    for (const file of files) {
      formData.append('files', file);
    }

    const res = await fetch(`${BASE_URL}/api/documents/upload`, {
      method: 'POST',
      headers: {
        ...getAuthHeaders(),
      },
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Error al subir archivos' }));
      throw new Error(err.detail || 'Fallo en la subida de documentos');
    }
    return res.json();
  },

  async deleteDocument(docName: string): Promise<DeleteResponse> {
    const res = await fetch(`${BASE_URL}/api/documents/${encodeURIComponent(docName)}`, {
      method: 'DELETE',
      headers: {
        ...getAuthHeaders(),
      },
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Error al eliminar el documento' }));
      throw new Error(err.detail || 'Fallo al eliminar el documento');
    }
    return res.json();
  },

  async sendQuery(
    query: string, 
    similarityThreshold?: number, 
    limit?: number
  ): Promise<ChatResponse> {
    const res = await fetch(`${BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify({
        query,
        similarity_threshold: similarityThreshold,
        limit,
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Error al consultar el chat' }));
      throw new Error(err.detail || 'Fallo en la consulta RAG');
    }
    return res.json();
  },

  async register(email: string, password: string): Promise<RegisterResponse> {
    const res = await fetch(`${BASE_URL}/api/v1/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Error al procesar el registro' }));
      throw new Error(err.detail || 'Fallo en el registro de usuario');
    }
    return res.json();
  },

  async login(email: string, password: string): Promise<LoginResponse> {
    const res = await fetch(`${BASE_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Credenciales inválidas' }));
      throw new Error(err.detail || 'Fallo al iniciar sesión');
    }
    return res.json();
  },

  async logout(): Promise<{ message: string }> {
    const res = await fetch(`${BASE_URL}/api/v1/auth/logout`, {
      method: 'POST',
    });
    return res.json().catch(() => ({ message: 'Sesión cerrada' }));
  },
};
