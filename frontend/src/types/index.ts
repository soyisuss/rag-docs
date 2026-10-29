export interface Citation {
  document: string;
  page: number;
  score: number;
  snippet: string;
}

export interface ChatResponse {
  query: string;
  answer: string;
  max_score: number;
  threshold: number;
  guardrail_passed: boolean;
  sources: Citation[];
  message?: string;
}

export interface DocumentItem {
  name: string;
  in_storage: boolean;
  in_vector_store: boolean;
}

export interface DocumentListResponse {
  total: number;
  documents: DocumentItem[];
}

export interface UploadResponse {
  uploaded: string[];
  total_chunks: number;
  message: string;
}

export interface DeleteResponse {
  document_name: string;
  deleted: boolean;
  message: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  collection: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  guardrail_passed?: boolean;
  max_score?: number;
  sources?: Citation[];
  timestamp: Date;
}

export interface RegisterResponse {
  id: number;
  email: string;
}
