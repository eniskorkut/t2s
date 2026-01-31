/**
 * API Client implementation
 * Following Single Responsibility Principle - handles API communication
 * Following Dependency Inversion Principle - depends on IHttpClient abstraction
 * Following Interface Segregation Principle - implements IApiClient interface
 */

import { HttpClient, type IHttpClient } from './HttpClient';
import type { IApiClient } from '@/lib/types/api.types';
import type {
  User,
  Query,
  SQLGenerationResponse,
  SQLExecutionResponse,
  LoginResponse,
  RegisterResponse,
} from '@/lib/types';
import { configManager } from '@/lib/config';

export class ApiClient implements IApiClient {
  private httpClient: IHttpClient;

  constructor(httpClient?: IHttpClient) {
    // Dependency Injection - allows for testing with mock HttpClient
    this.httpClient = httpClient || new HttpClient(
      configManager.getApiBaseUrl(),
      configManager.getApiTimeout()
    );
  }

  private getAuthHeaders(): HeadersInit {
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }

  // Authentication methods
  async login(email: string, password: string): Promise<LoginResponse> {
    return this.httpClient.post<LoginResponse>('/api/login', { email, password });
  }

  async register(email: string, password: string): Promise<RegisterResponse> {
    return this.httpClient.post<RegisterResponse>('/api/register', { email, password });
  }

  async logout(): Promise<{ success: boolean }> {
    return this.httpClient.post<{ success: boolean }>('/api/logout');
  }

  async getCurrentUser(): Promise<User> {
    return this.httpClient.get<User>('/api/user');
  }

  async resetPassword(email: string, password: string): Promise<{ success: boolean; message: string }> {
    return this.httpClient.post<{ success: boolean; message: string }>('/api/reset-password', {
      email,
      new_password: password
    });
  }

  // Query methods
  async generateSQL(question: string, history: { role: string; content: string }[] = [], sessionId?: string): Promise<SQLGenerationResponse> {
    // SQL oluşturma işlemleri uzun sürebilir, özel bir HttpClient instance'ı kullan
    const longTimeoutClient = new HttpClient(
      configManager.getApiBaseUrl(),
      300000 // 300 saniye (5 dakika) timeout
    );
    return longTimeoutClient.post<SQLGenerationResponse>(
      '/api/v0/generate_sql',
      { question, history, session_id: sessionId }
    );
  }

  async generateSQLStream(
    question: string,
    history: { role: string; content: string }[] = [],
    onToken: (token: string) => void,
    onMetadata: (metadata: any) => void,
    sessionId?: string
  ): Promise<void> {
    const url = `${configManager.getApiBaseUrl()}/api/v0/generate_sql?stream=true`;

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...this.getAuthHeaders(),
        },
        // credentials: 'include', // Removed cookie-based credential
        body: JSON.stringify({ question, history, session_id: sessionId }),
      });

      if (!response.ok) {
        throw new Error('Streaming failed');
      }

      const reader = response.body?.getReader();
      if (!reader) return;

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const content = line.slice(6).trim();
            if (content === '[DONE]') break;

            try {
              const data = JSON.parse(content);
              if (data.token) {
                onToken(data.token);
              } else if (data.type === 'metadata') {
                onMetadata(data);
              }
            } catch (e) {
              console.error('Error parsing stream data:', e);
            }
          }
        }
      }
    } catch (error) {
      console.error('Stream error:', error);
      throw error;
    }
  }

  async runSQL(sql: string, question?: string, sessionId?: string): Promise<SQLExecutionResponse> {
    return this.httpClient.post<SQLExecutionResponse>('/api/v0/run_sql', {
      sql,
      question,
      session_id: sessionId
    });
  }

  async saveQuery(
    question: string,
    sql_query: string,
    is_trained: boolean
  ): Promise<{ success: boolean; query_id?: number; error?: string }> {
    return this.httpClient.post<{ success: boolean; query_id?: number; error?: string }>(
      '/api/save-query',
      { question, sql_query, is_trained }
    );
  }

  async getMyQueries(): Promise<{ success: boolean; queries?: Query[]; error?: string }> {
    return this.httpClient.get<{ success: boolean; queries?: Query[]; error?: string }>(
      '/api/my-queries'
    );
  }

  async deleteQuery(id: number): Promise<{ success: boolean; error?: string }> {
    return this.httpClient.delete<{ success: boolean; error?: string }>(`/api/query/${id}`);
  }

  // Chat session methods
  async createChatSession(firstMessage: string): Promise<{ success: boolean; session_id: string; title: string }> {
    return this.httpClient.post<{ success: boolean; session_id: string; title: string }>(
      '/api/chat/new',
      { first_message: firstMessage }
    );
  }

  async getChatHistory(): Promise<import('@/lib/types').ChatHistoryResponse> {
    return this.httpClient.get<import('@/lib/types').ChatHistoryResponse>('/api/chat/history');
  }

  async getChatSession(sessionId: string): Promise<{
    success: boolean;
    session: import('@/lib/types').ChatSession;
    messages: import('@/lib/types').Message[];
  }> {
    return this.httpClient.get(`/api/chat/${sessionId}`);
  }

  async updateChatTitle(sessionId: string, title: string): Promise<{ success: boolean }> {
    return this.httpClient.patch<{ success: boolean }>(`/api/chat/${sessionId}/title`, { title });
  }

  async toggleChatPin(sessionId: string): Promise<{ success: boolean }> {
    return this.httpClient.patch<{ success: boolean }>(`/api/chat/${sessionId}/pin`);
  }

  async deleteChatSession(sessionId: string): Promise<{ success: boolean }> {
    return this.httpClient.delete<{ success: boolean }>(`/api/chat/${sessionId}`);
  }

  async sendMessage(sessionId: string, question: string, history: { role: string; content: string }[] = [], stream: boolean = true): Promise<Response> {
    const url = `${configManager.getApiBaseUrl()}/api/chat/${sessionId}/message`;
    return fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...this.getAuthHeaders(),
      },
      // credentials: 'include', // Removed cookie-based credential
      body: JSON.stringify({ question, history, stream }),
    });
  }

  // Admin methods
  async getUsers(): Promise<User[]> {
    return this.httpClient.get<User[]>('/api/admin/users');
  }

  async updateUserRole(userId: number, role: string): Promise<{ success: boolean }> {
    return this.httpClient.patch<{ success: boolean }>(`/api/admin/users/${userId}/role`, { role });
  }

  async getLiveDDL(): Promise<{ ddl: string }> {
    return this.httpClient.get<{ ddl: string }>('/api/admin/ddl/live');
  }

  async getSavedDDL(): Promise<{ id: number; ddl_content: string; created_at: string }> {
    return this.httpClient.get<{ id: number; ddl_content: string; created_at: string }>('/api/admin/ddl/saved');
  }

  async trainDDL(ddl: string): Promise<{ success: boolean; message: string }> {
    // Increase timeout for training
    const longTimeoutClient = new HttpClient(
      configManager.getApiBaseUrl(),
      300000 // 300 seconds (5 minutes)
    );
    return longTimeoutClient.post<{ success: boolean; message: string }>('/api/admin/train', { ddl });
  }
}

// Singleton instance for application use
export const apiClient = new ApiClient();
