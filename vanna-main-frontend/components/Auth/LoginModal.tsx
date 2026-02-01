/**
 * Login Modal component - ChatGPT style
 * Following Single Responsibility Principle - only handles login UI
 * Following Dependency Inversion Principle - depends on useAuth hook abstraction
 */

'use client';

import React, { useState } from 'react';
import { apiClient } from '@/lib/api/HttpClient';
import { useAuth } from '@/context/AuthContext';

export interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSwitchToRegister: () => void;
  onSwitchToResetPassword?: () => void;
  asModal?: boolean; // true = modal overlay, false = full page
}

export function LoginModal({ isOpen, onClose, onSwitchToRegister, onSwitchToResetPassword, asModal = false }: LoginModalProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // Use ApiClient or fetch directly
      const res = await apiClient.post<any>('/api/login', {
        email,
        password,
      });

      if (res.token) {
        localStorage.setItem('token', res.token);
        localStorage.setItem('role', res.role);
        localStorage.setItem('email', email);
        // The original code called login(data.access_token, data.role, email);
        // The provided snippet replaces this with localStorage and window.location.reload().
        // Assuming the user wants this new behavior.
        // if (onSuccess) onSuccess(); // 'onSuccess' prop is not defined in LoginModalProps
        onClose();
        window.location.reload();
      } else {
        // If no token is returned but the request was successful, handle as an error
        throw new Error(res.detail || 'Giriş başarısız.');
      }
    } catch (err: any) {
      setError(err.message || 'Giriş başarısız');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className={`fixed inset-0 z-50 ${asModal ? 'bg-black/50' : 'bg-white'} flex items-center justify-center overflow-y-auto py-10`}
      onClick={asModal ? onClose : undefined}
    >
      <div
        className={`w-full max-w-md ${asModal ? 'bg-white rounded-xl shadow-2xl p-6 mx-4' : 'px-6'}`}
        onClick={(e) => asModal && e.stopPropagation()}
      >
        {/* Logo - Sol üst */}
        {!asModal && (
          <button
            onClick={onClose}
            className="absolute top-6 left-6"
          >
            <h1 className="text-2xl font-semibold text-black hover:opacity-70 transition cursor-pointer">Vanna AI</h1>
          </button>
        )}

        {/* Ana içerik */}
        <div className="w-full">
          <h1 className="text-3xl font-bold text-black mb-2">Giriş Yap</h1>
          <p className="text-gray-600 mb-8 text-sm">
            Vanna AI hesabınıza giriş yapın
          </p>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email alanı */}
            <div>
              <label className="block mb-2 text-sm font-medium text-black">
                E-posta adresi
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg text-black focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent"
                placeholder="ornek@email.com"
                required
                autoComplete="email"
              />
            </div>

            {/* Parola alanı */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-black">
                  Parola
                </label>
                {onSwitchToResetPassword && (
                  <button
                    type="button"
                    onClick={() => {
                      onClose();
                      window.location.href = '/forgot-password';
                    }}
                    className="text-xs text-gray-500 hover:text-black hover:underline"
                  >
                    Şifremi unuttum
                  </button>
                )}
              </div>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full p-3 pr-12 border border-gray-300 rounded-lg text-black focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent"
                  placeholder="Parolanızı girin"
                  required
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-black"
                >
                  {showPassword ? (
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                      <path
                        d="M10 3C5 3 1.73 7.11 1 10C1.73 12.89 5 17 10 17C15 17 18.27 12.89 19 10C18.27 7.11 15 3 10 3ZM10 15C7.24 15 5 12.76 5 10C5 7.24 7.24 5 10 5C12.76 5 15 7.24 15 10C15 12.76 12.76 15 10 15ZM10 7C8.34 7 7 8.34 7 10C7 11.66 8.34 13 10 13C11.66 13 13 11.66 13 10C13 8.34 11.66 7 10 7Z"
                        fill="currentColor"
                      />
                    </svg>
                  ) : (
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                      <path
                        d="M10 3C5 3 1.73 7.11 1 10C1.73 12.89 5 17 10 17C15 17 18.27 12.89 19 10C18.27 7.11 15 3 10 3ZM10 15C7.24 15 5 12.76 5 10C5 7.24 7.24 5 10 5C12.76 5 15 7.24 15 10C15 12.76 12.76 15 10 15Z"
                        fill="currentColor"
                      />
                      <path
                        d="M2 2L18 18"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                      />
                    </svg>
                  )}
                </button>
              </div>
            </div>

            {error && (
              <div className="text-red-600 text-sm bg-red-50 p-3 rounded-lg">
                {error}
              </div>
            )}

            {/* Giriş yap butonu */}
            <button
              type="submit"
              disabled={isLoading || !email || !password}
              className="w-full bg-black text-white py-3 rounded-lg font-medium hover:bg-gray-800 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Yükleniyor...' : 'Giriş Yap'}
            </button>
          </form>

          {/* Alt linkler */}
          <div className="mt-8 text-center">
            <div className="flex items-center justify-center gap-4 text-xs text-gray-500">
              <a href="#" className="hover:text-black underline">
                Kullanım Şartları
              </a>
              <span>|</span>
              <a href="#" className="hover:text-black underline">
                Gizlilik Politikası
              </a>
            </div>
          </div>

          {/* Kayıt ol linki */}
          <div className="mt-6 text-center">
            <button
              type="button"
              onClick={() => {
                onClose();
                onSwitchToRegister();
              }}
              className="text-sm font-semibold text-blue-600 hover:text-blue-800 hover:underline"
            >
              Hesabın yok mu? Hemen ücretsiz kaydol
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
