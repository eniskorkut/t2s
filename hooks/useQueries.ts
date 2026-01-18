/**
 * Queries hook
 * Following Single Responsibility Principle - only handles saved queries logic
 * Following Dependency Inversion Principle - depends on IQueryApi interface
 */

import { useState, useCallback, useEffect } from 'react';
import type { IQueryApi } from '@/lib/types/api.types';
import type { Query } from '@/lib/types';
import { apiClient } from '@/lib/api/ApiClient';
import { ApiError } from '@/lib/errors/ApiError';

interface UseQueriesOptions {
  queryApi?: IQueryApi; // Dependency Injection for testing
  autoLoad?: boolean;
}

interface UseQueriesReturn {
  queries: Query[];
  isLoading: boolean;
  error: string | null;
  loadQueries: () => Promise<void>;
  deleteQuery: (id: number) => Promise<void>;
  clearError: () => void;
}

export function useQueries(options: UseQueriesOptions = {}): UseQueriesReturn {
  const { queryApi, autoLoad = false } = options;
  const [queries, setQueries] = useState<Query[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Use injected API client or default singleton
  const api: IQueryApi = queryApi || apiClient;

  const loadQueries = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.getMyQueries();
      if (response.success && response.queries) {
        setQueries(response.queries);
      } else {
        throw new ApiError(response.error || 'Sorgular yüklenemedi');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Bilinmeyen hata oluştu';
      setError(errorMessage);
      setQueries([]);
    } finally {
      setIsLoading(false);
    }
  }, [api]);

  const deleteQuery = useCallback(async (id: number) => {
    try {
      const response = await api.deleteQuery(id);
      if (response.success) {
        setQueries((prev) => prev.filter((q) => q.id !== id));
      } else {
        throw new ApiError(response.error || 'Sorgu silinemedi');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Sorgu silinirken hata oluştu';
      setError(errorMessage);
      throw err;
    }
  }, [api]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  useEffect(() => {
    if (autoLoad) {
      loadQueries();
    }
  }, [autoLoad, loadQueries]);

  return {
    queries,
    isLoading,
    error,
    loadQueries,
    deleteQuery,
    clearError,
  };
}
