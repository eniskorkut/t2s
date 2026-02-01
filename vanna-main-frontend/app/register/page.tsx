"use client";

import { useState } from "react";
import { apiClient } from "@/lib/api/HttpClient";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function RegisterPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const router = useRouter();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        if (password.length < 6) {
            setError("Parola en az 6 karakter olmalıdır.");
            setLoading(false);
            return;
        }

        try {
            const res = await apiClient.post<any>("/api/register", {
                email,
                password,
            });

            if (res.success) {
                // Auto-login attempt
                try {
                    const loginRes = await apiClient.post<any>("/api/login", {
                        email,
                        password,
                    });
                    if (loginRes.token) {
                        localStorage.setItem('token', loginRes.token);
                        localStorage.setItem('role', loginRes.role);
                        localStorage.setItem('email', email);
                        // Redirect to home or dashboard
                        window.location.href = '/';
                        return;
                    }
                } catch (loginErr) {
                    // If auto-login fails, redirect to login page
                    router.push("/login");
                }
            } else {
                throw new Error(res.error || "Kayıt başarısız.");
            }

        } catch (err: any) {
            setError(err.message || "Kayıt işlemi başarısız.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-xl shadow-lg border border-gray-100">
                <div>
                    <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900 tracking-tight">
                        Yeni Hesap Oluşturun
                    </h2>
                    <p className="mt-2 text-center text-sm text-gray-600">
                        Vanna AI ile SQL sorguları oluşturmaya başlayın
                    </p>
                </div>
                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    <div className="rounded-md shadow-sm -space-y-px">
                        <div>
                            <label htmlFor="email-address" className="sr-only">
                                Email adresi
                            </label>
                            <input
                                id="email-address"
                                name="email"
                                type="email"
                                autoComplete="email"
                                required
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="appearance-none rounded-none relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm transition-colors"
                                placeholder="Email adresi"
                            />
                        </div>
                        <div>
                            <label htmlFor="password" className="sr-only">
                                Şifre
                            </label>
                            <input
                                id="password"
                                name="password"
                                type="password"
                                autoComplete="new-password"
                                required
                                minLength={6}
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="appearance-none rounded-none relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm transition-colors"
                                placeholder="Şifre (En az 6 karakter)"
                            />
                        </div>
                    </div>

                    {error && (
                        <div className="text-red-500 text-sm text-center bg-red-50 p-2 rounded">
                            {error}
                        </div>
                    )}

                    <div>
                        <button
                            type="submit"
                            disabled={loading}
                            className={`group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white ${loading ? "bg-blue-400" : "bg-blue-600 hover:bg-blue-700"
                                } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors shadow-md hover:shadow-lg`}
                        >
                            {loading ? (
                                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                            ) : (
                                "Kayıt Ol"
                            )}
                        </button>
                    </div>

                    <div className="flex items-center justify-center mt-4">
                        <div className="text-sm">
                            <span className="text-gray-600">Zaten hesabınız var mı? </span>
                            <Link href="/login" className="font-medium text-blue-600 hover:text-blue-500">
                                Giriş Yap
                            </Link>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    );
}
