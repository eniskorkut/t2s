/**
 * Query save hook
 * Following Single Responsibility Principle - only handles query saving logic
 * Following Dependency Inversion Principle - depends on IQueryApi interface
 */

import { useState, useCallback } from 'react';
import type { IQueryApi } from '@/lib/types/api.types';
import { apiClient } from '@/lib/api/ApiClient';
import { ApiError } from '@/lib/errors/ApiError';

interface UseQuerySaveOptions {
  queryApi?: IQueryApi; // Dependency Injection for testing
}

interface UseQuerySaveReturn {
  isSaving: boolean;
  error: string | null;
  saveQuery: (question: string, sql: string, isTrained: boolean) => Promise<boolean>;
  clearError: () => void;
}

export function useQuerySave(options: UseQuerySaveOptions = {}): UseQuerySaveReturn {
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Use injected API client or default singleton
  const queryApi: IQueryApi = options.queryApi || apiClient;

  const saveQuery = useCallback(async (
    question: string,
    sql: string,
    isTrained: boolean
  ): Promise<boolean> => {
    setIsSaving(true);
    setError(null);

    try {
      const response = await queryApi.saveQuery(question, sql, isTrained);
      if (response.success) {
        return true;
      } else {
        throw new ApiError(response.error || 'Sorgu kaydedilemedi');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Bilinmeyen hata oluştu';
      setError(errorMessage);
      return false;
    } finally {
      setIsSaving(false);
    }
  }, [queryApi]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    isSaving,
    error,
    saveQuery,
    clearError,
  };
}
