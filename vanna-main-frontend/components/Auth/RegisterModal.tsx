/**
 * Register Modal component
 * Following Single Responsibility Principle - only handles registration UI
 * Following Dependency Inversion Principle - depends on useAuth hook abstraction
 */

'use client';

import React, { useState } from 'react';
import { apiClient } from '@/lib/api/HttpClient';
import { useAuth } from '@/context/AuthContext';

export interface RegisterModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSwitchToLogin: () => void;
  asModal?: boolean; // true = modal overlay, false = full page
}

export function RegisterModal({ isOpen, onClose, onSwitchToLogin, asModal = false }: RegisterModalProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth(); // We might use login to auto-login after registration

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    if (password.length < 6) {
      setError('Parola en az 6 karakter olmalıdır.');
      setIsLoading(false);
      return;
    }

    try {
      // API call to register
      const res = await apiClient.post<any>('/api/register', {
        email,
        password,
      });

      if (res.success) {
        // Auto login or prompt user
        // If the backend returns a token immediately or sets a cookie, we can redirect or close
        // The /register endpoint in backend returns LoginResponse with success=True and sets a cookie.
        // It does NOT return a token directly in the body based on current api/auth.py code inspection,
        // but let's check if it auto-logs in via cookie.
        // Actually, let's look at api/auth.py again. It returns LoginResponse which has user object.
        // It sets cookie "user_id".
        // It does NOT return "access_token".
        // However, the frontend usually expects a JWT token for localStorage if we stick to the LoginModal pattern.
        // But LoginModal uses /api/login which returns "access_token".
        // If /register only sets cookie, we might need to call /login immediately or
        // redirect to login page.
        // Let's assume we show success message and switch to login for now, or auto-login if backend supports it.
        // Given current backend api/auth.py adds cookie but maybe not token, explicit login is safer.
        // Actually, wait, let's just switch to login to be safe.

        // BETTER UX: Auto-login
        // We can call /api/login right after registration if we want.

        try {
          const loginRes = await apiClient.post<any>('/api/login', {
            email,
            password
          });
          if (loginRes.token) {
            localStorage.setItem('token', loginRes.token);
            localStorage.setItem('role', loginRes.role);
            localStorage.setItem('email', email);
            onClose();
            window.location.reload();
            return;
          }
        } catch (loginErr) {
          // If auto-login fails, fall back to switching to login modal
          onSwitchToLogin();
        }

      } else {
        throw new Error(res.error || 'Kayıt başarısız.');
      }
    } catch (err: any) {
      setError(err.message || 'Kayıt işlemi başarısız. Lütfen tekrar deneyin.');
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
          <h1 className="text-3xl font-bold text-black mb-2">Hesap Oluştur</h1>
          <p className="text-gray-600 mb-8 text-sm">
            Vanna AI kullanmaya başlamak için kaydolun
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
              <label className="block mb-2 text-sm font-medium text-black">
                Parola
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full p-3 pr-12 border border-gray-300 rounded-lg text-black focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent"
                  placeholder="En az 6 karakter"
                  required
                  autoComplete="new-password"
                  minLength={6}
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

            {/* Kayıt ol butonu */}
            <button
              type="submit"
              disabled={isLoading || !email || !password}
              className="w-full bg-black text-white py-3 rounded-lg font-medium hover:bg-gray-800 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Hesap oluşturuluyor...' : 'Kayıt Ol'}
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

          {/* Giriş yap linki */}
          <div className="mt-6 text-center">
            <button
              type="button"
              onClick={() => {
                onClose();
                onSwitchToLogin();
              }}
              className="text-sm font-semibold text-blue-600 hover:text-blue-800 hover:underline"
            >
              Zaten hesabın var mı? Giriş yap
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
