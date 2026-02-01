/**
 * Type definitions for Vanna Frontend
 * Following Interface Segregation Principle (ISP) - separate interfaces for different concerns
 */

// User domain types
export interface User {
  id: number;
  email: string;
  created_at?: string;
  role?: string;
}

// Message domain types
export interface Message {
  id?: string;
  role: 'user' | 'assistant';
  content: string;
  sql?: string;
  data?: Record<string, any>[];
  plotly_json?: any; // Plotly grafik verisi
  timestamp?: Date;
  suggestions?: string[]; // Öneriler için
  from_cache?: boolean; // Semantic cache'den geldiyse true
}

// Query domain types
export interface Query {
  id: number;
  question: string;
  sql_query: string;
  saved_at: string;
  is_trained: boolean;
}

// Chat Session types
export interface ChatSession {
  id: string;
  title: string;
  is_pinned: boolean;
  created_at: string;
  updated_at: string;
}

export interface ChatHistoryResponse {
  success: boolean;
  sessions: ChatSession[];
}

// API Response types
export interface ApiResponse<T = unknown> {
  success?: boolean;
  error?: string;
  data?: T;
}

export interface LoginResponse {
  success: boolean;
  user?: User;
  error?: string;
}

export interface RegisterResponse {
  success: boolean;
  user?: User;
  error?: string;
}

export interface SQLGenerationResponse {
  type: 'sql' | 'error' | 'clarification';
  id?: string;
  text?: string;
  explanation?: string; // Backend'den gelen açıklama
  error?: string;
  message?: string; // Clarification mesajı için
  suggestions?: string[]; // Öneriler için
  original_question?: string; // Orijinal soru için
  from_cache?: boolean; // Semantic cache'den geldi mi?
}

export interface SQLExecutionResponse {
  type: 'df' | 'sql_error' | 'error';
  df?: string;
  data?: Record<string, any>[];
  plotly_json?: any;
  error?: string;
  sql?: string;
}

export interface QueriesResponse {
  success: boolean;
  queries?: Query[];
  error?: string;
}

// Error types
export interface ApiError {
  message: string;
  code?: string;
  status?: number;
}
