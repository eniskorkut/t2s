/**
 * Reset Password Modal component
 * Follows LoginModal pattern
 */

'use client';

import React, { useState } from 'react';
import { apiClient } from '@/lib/api/ApiClient';

export interface ResetPasswordModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSwitchToLogin: () => void;
    asModal?: boolean;
}

export function ResetPasswordModal({ isOpen, onClose, onSwitchToLogin, asModal = false }: ResetPasswordModalProps) {
    const [email, setEmail] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const [successMessage, setSuccessMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setSuccessMessage('');
        setIsLoading(true);

        try {
            const result = await apiClient.resetPassword(email, newPassword);
            if (result.success) {
                setSuccessMessage('Parolanız başarıyla güncellendi. Giriş yapabilirsiniz.');
                setTimeout(() => {
                    onSwitchToLogin();
                }, 2000);
            } else {
                setError(result.message || 'Bir hata oluştu.');
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'İşlem başarısız.');
        } finally {
            setIsLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div
            className={`fixed inset-0 z-50 ${asModal ? 'bg-black/50' : 'bg-white'} flex items-center justify-center`}
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
                    <h1 className="text-3xl font-bold text-black mb-2">Şifre Sıfırla</h1>
                    <p className="text-gray-600 mb-8 text-sm">
                        E-posta adresinizi ve yeni şifrenizi girin
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
                            />
                        </div>

                        {/* Yeni Parola alanı */}
                        <div>
                            <label className="block mb-2 text-sm font-medium text-black">
                                Yeni Parola
                            </label>
                            <div className="relative">
                                <input
                                    type={showPassword ? 'text' : 'password'}
                                    value={newPassword}
                                    onChange={(e) => setNewPassword(e.target.value)}
                                    className="w-full p-3 pr-12 border border-gray-300 rounded-lg text-black focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent"
                                    placeholder="En az 6 karakter"
                                    required
                                    minLength={6}
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-black"
                                >
                                    {showPassword ? 'Gizle' : 'Göster'}
                                </button>
                            </div>
                        </div>

                        {error && (
                            <div className="text-red-600 text-sm bg-red-50 p-3 rounded-lg">
                                {error}
                            </div>
                        )}

                        {successMessage && (
                            <div className="text-green-600 text-sm bg-green-50 p-3 rounded-lg">
                                {successMessage}
                            </div>
                        )}

                        {/* Gönder butonu */}
                        <button
                            type="submit"
                            disabled={isLoading || !email || !newPassword}
                            className="w-full bg-black text-white py-3 rounded-lg font-medium hover:bg-gray-800 transition disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isLoading ? 'İşleniyor...' : 'Şifreyi Güncelle'}
                        </button>
                    </form>

                    {/* Giriş yap linki */}
                    <div className="mt-6 text-center">
                        <button
                            type="button"
                            onClick={() => {
                                onClose();
                                onSwitchToLogin();
                            }}
                            className="text-sm text-gray-600 hover:text-black underline"
                        >
                            Giriş ekranına dön
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
