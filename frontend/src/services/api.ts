import { 
  ChatResponse, 
  DocumentListResponse, 
  UploadResponse, 
  DeleteResponse, 
  HealthResponse 
} from '../types';

const BASE_URL = import.meta.env.VITE_API_URL || '';

export const api = {
  async getHealth(): Promise<HealthResponse> {
    const res = await fetch(`${BASE_URL}/api/health`);
    if (!res.ok) throw new Error(`Error ${res.status}: Fallo al conectar con el servidor`);
    return res.json();
  },

  async getDocuments(): Promise<DocumentListResponse> {
    const res = await fetch(`${BASE_URL}/api/documents`);
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
};
