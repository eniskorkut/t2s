"use client";

import { useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { apiClient } from "@/lib/api/HttpClient";

function ResetPasswordForm() {
    const searchParams = useSearchParams();
    const router = useRouter();
    const token = searchParams.get("token");
    const [newPassword, setNewPassword] = useState("");
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setMessage("");

        if (!token) {
            setError("Geçersiz token.");
            return;
        }

        if (newPassword.length < 6) {
            setError("Şifre en az 6 karakter olmalıdır.");
            return;
        }

        setLoading(true);

        try {
            // Decoding token to get email is handled backend side, 
            // but we need to send email in request body based on schema.
            // However, the backend verify_reset_token gets email from token content.
            // Wait, schema requires email + token + new_password.
            // We need to extract email from token (frontend decode) OR change backend to not require email.
            // Based on backend implementation: verify_reset_token returns email from payload.
            // But verify logic checks: if not token_email or token_email != request.email
            // So we MUST provide the correct email.

            // To fix this without complex frontend decoding lib:
            // Let's assume the user knows their email? No, that's bad UX.
            // The link usually contains the email or we decode the token.
            // Simple solution: Decode base64 parts of JWT manually.

            const payload = JSON.parse(atob(token.split('.')[1]));
            const email = payload.sub;

            await apiClient.post<any>("/api/reset-password", {
                email,
                token,
                new_password: newPassword
            });

            setMessage("Şifreniz başarıyla güncellendi. Giriş sayfasına yönlendiriliyorsunuz...");
            setTimeout(() => router.push("/login"), 2000);

        } catch (err: any) {
            setError(err.message || "Şifre sıfırlama başarısız.");
        } finally {
            setLoading(false);
        }
    };

    if (!token) {
        return <div className="text-center text-red-500">Geçersiz veya eksik token.</div>;
    }

    return (
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
            <div className="rounded-md shadow-sm -space-y-px">
                <div>
                    <label htmlFor="new-password" className="sr-only">
                        Yeni Şifre
                    </label>
                    <input
                        id="new-password"
                        name="new-password"
                        type="password"
                        required
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        className="appearance-none rounded relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                        placeholder="Yeni Şifre"
                        minLength={6}
                    />
                </div>
            </div>

            {message && (
                <div className="text-green-600 text-sm text-center bg-green-50 p-2 rounded">
                    {message}
                </div>
            )}

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
                        } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors shadow-md`}
                >
                    {loading ? "Güncelleniyor..." : "Şifreyi Güncelle"}
                </button>
            </div>
        </form>
    );
}

export default function ResetPasswordPage() {
    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-xl shadow-lg border border-gray-100">
                <div>
                    <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900 tracking-tight">
                        Yeni Şifre Belirle
                    </h2>
                </div>
                <Suspense fallback={<div>Yükleniyor...</div>}>
                    <ResetPasswordForm />
                </Suspense>
            </div>
        </div>
    );
}
