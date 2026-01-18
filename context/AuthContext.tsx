/**
 * Authentication Context
 * Following Single Responsibility Principle - only handles authentication state
 * Following Dependency Inversion Principle - depends on IApiClient interface
 */

'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import type { IAuthApi } from '@/lib/types/api.types';
import type { User } from '@/lib/types';
import { apiClient } from '@/lib/api/ApiClient';

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

interface AuthProviderProps {
  children: React.ReactNode;
  apiClient?: IAuthApi; // Dependency Injection for testing
}

export function AuthProvider({ children, apiClient: injectedApiClient }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Use injected API client or default singleton
  const authApi: IAuthApi = injectedApiClient || apiClient;

  const checkAuth = useCallback(async () => {
    try {
      const userData = await authApi.getCurrentUser();
      setUser(userData);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, [authApi]);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const login = useCallback(async (email: string, password: string) => {
    const response = await authApi.login(email, password);
    if (response.success && response.user) {
      setUser(response.user);
    } else {
      throw new Error(response.error || 'Giriş başarısız');
    }
  }, [authApi]);

  const register = useCallback(async (email: string, password: string) => {
    const response = await authApi.register(email, password);
    if (response.success && response.user) {
      setUser(response.user);
    } else {
      throw new Error(response.error || 'Kayıt başarısız');
    }
  }, [authApi]);

  const logout = useCallback(async () => {
    await authApi.logout();
    setUser(null);
  }, [authApi]);

  const refreshUser = useCallback(async () => {
    await checkAuth();
  }, [checkAuth]);

  const value: AuthContextValue = {
    user,
    loading,
    login,
    register,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
