/**
 * HTTP Client abstraction
 * Following Dependency Inversion Principle - high-level modules depend on abstractions
 * Following Single Responsibility Principle - only handles HTTP communication
 */

import { ApiError, NetworkError } from '@/lib/errors/ApiError';

export interface IHttpClient {
  get<T>(endpoint: string, options?: RequestInit): Promise<T>;
  post<T>(endpoint: string, body?: unknown, options?: RequestInit): Promise<T>;
  put<T>(endpoint: string, body?: unknown, options?: RequestInit): Promise<T>;
  patch<T>(endpoint: string, body?: unknown, options?: RequestInit): Promise<T>;
  delete<T>(endpoint: string, options?: RequestInit): Promise<T>;
}

export class HttpClient implements IHttpClient {
  private baseUrl: string;
  private timeout: number;

  constructor(baseUrl: string, timeout: number = 30000) {
    this.baseUrl = baseUrl;
    this.timeout = timeout;
  }

  private getAuthHeaders(): HeadersInit {
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        // credentials: 'include', // Removed for JWT
        headers: {
          'Content-Type': 'application/json',
          ...this.getAuthHeaders(),
          ...options.headers,
        },
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        if (response.status === 401) {
          if (typeof window !== 'undefined') {
            localStorage.removeItem('token');
            localStorage.removeItem('role');
            localStorage.removeItem('email');
            window.location.href = '/login';
          }
        }

        const errorData = await response.json().catch(() => ({
          error: response.statusText,
        }));
        throw new ApiError(
          errorData.error || `HTTP ${response.status}`,
          undefined,
          response.status
        );
      }

      return response.json();
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof ApiError) {
        throw error;
      }

      if (error instanceof Error && error.name === 'AbortError') {
        throw new NetworkError('İstek zaman aşımına uğradı. Lütfen internet bağlantınızı kontrol edin.');
      }

      throw new NetworkError(
        error instanceof Error
          ? (error.message === 'Failed to fetch' ? 'Sunucuya bağlanılamadı. Backend çalışıyor mu?' : error.message)
          : 'Bir ağ hatası oluştu'
      );
    }
  }

  async get<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'GET' });
  }

  async post<T>(endpoint: string, body?: unknown, options: RequestInit = {}): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async put<T>(endpoint: string, body?: unknown, options: RequestInit = {}): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async patch<T>(endpoint: string, body?: unknown, options: RequestInit = {}): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async delete<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' });
  }
}

const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8084';
export const apiClient = new HttpClient(apiUrl);
