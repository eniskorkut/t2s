'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { apiClient } from '@/lib/api/ApiClient';
import type { User } from '@/lib/types';
import { Button } from '@/components/UI/Button';
import { Modal } from '@/components/UI/Modal';
import { ChevronLeftIcon } from '@/components/UI/Icons';

export default function AdminPage() {
    const router = useRouter();
    const [activeTab, setActiveTab] = useState<'users' | 'database'>('users');
    const [currentUser, setCurrentUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        checkAdminAccess();
    }, []);

    const checkAdminAccess = async () => {
        try {
            const user = await apiClient.getCurrentUser();
            if (user.role !== 'admin') {
                router.push('/');
                return;
            }
            setCurrentUser(user);
        } catch (error) {
            router.push('/');
        } finally {
            setIsLoading(false);
        }
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-black"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 p-6">
            <div className="max-w-6xl mx-auto space-y-6">
                {/* Header */}
                <div className="flex items-center gap-4 mb-8">
                    <Link href="/" className="p-2 hover:bg-gray-200 rounded-full transition-colors">
                        <ChevronLeftIcon size={24} className="text-gray-600" />
                    </Link>
                    <h1 className="text-2xl font-bold text-black">Admin Yönetim Paneli</h1>
                </div>

                {/* Tabs */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                    <div className="border-b border-gray-200">
                        <nav className="flex -mb-px">
                            <button
                                onClick={() => setActiveTab('users')}
                                className={`py-4 px-6 font-medium text-sm border-b-2 transition-colors ${activeTab === 'users'
                                    ? 'border-black text-black'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    }`}
                            >
                                👥 Kullanıcı Yönetimi
                            </button>
                            <button
                                onClick={() => setActiveTab('database')}
                                className={`py-4 px-6 font-medium text-sm border-b-2 transition-colors ${activeTab === 'database'
                                    ? 'border-black text-black'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    }`}
                            >
                                🗄️ Veritabanı & Eğitim
                            </button>
                        </nav>
                    </div>

                    <div className="p-6">
                        {activeTab === 'users' ? <UserManagement /> : <DatabaseManagement />}
                    </div>
                </div>
            </div>
        </div>
    );
}

function UserManagement() {
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadUsers();
    }, []);

    const loadUsers = async () => {
        try {
            const data = await apiClient.getUsers();
            setUsers(data);
        } catch (error) {
            console.error('Failed to load users:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleRoleChange = async (userId: number, currentRole: string) => {
        const newRole = currentRole === 'admin' ? 'user' : 'admin';
        if (!confirm(`Bu kullanıcının rolünü "${newRole}" olarak değiştirmek istediğinize emin misiniz?`)) return;

        try {
            await apiClient.updateUserRole(userId, newRole);
            setUsers(users.map(u => u.id === userId ? { ...u, role: newRole } : u));
        } catch (error) {
            alert('Rol güncellenirken bir hata oluştu.');
            console.error(error);
        }
    };

    if (loading) return <div className="text-center py-4">Yükleniyor...</div>;

    return (
        <div>
            <h2 className="text-lg font-semibold mb-4 text-black">Kayıtlı Kullanıcılar</h2>
            <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="border-b border-gray-200 text-xs font-semibold text-gray-500 uppercase bg-gray-50">
                            <th className="px-4 py-3">Email</th>
                            <th className="px-4 py-3">Rol</th>
                            <th className="px-4 py-3">Kayıt Tarihi</th>
                            <th className="px-4 py-3">İşlemler</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                        {users.map((user) => (
                            <tr key={user.id} className="hover:bg-gray-50">
                                <td className="px-4 py-3 text-sm text-black">{user.email}</td>
                                <td className="px-4 py-3">
                                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${user.role === 'admin'
                                        ? 'bg-purple-100 text-purple-800'
                                        : 'bg-green-100 text-green-800'
                                        }`}>
                                        {user.role || 'user'}
                                    </span>
                                </td>
                                <td className="px-4 py-3 text-sm text-gray-500">
                                    {new Date(user.created_at || '').toLocaleDateString('tr-TR')}
                                </td>
                                <td className="px-4 py-3">
                                    <button
                                        onClick={() => handleRoleChange(user.id, user.role || 'user')}
                                        className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                                    >
                                        {user.role === 'admin' ? 'User Yap' : 'Admin Yap'}
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

function DatabaseManagement() {
    const [liveDDL, setLiveDDL] = useState('');
    const [trainingDDL, setTrainingDDL] = useState('');
    const [loadingLive, setLoadingLive] = useState(false);
    const [loadingTrain, setLoadingTrain] = useState(false);
    const [lastSaved, setLastSaved] = useState<string | null>(null);
    const [isConfirmModalOpen, setIsConfirmModalOpen] = useState(false);

    useEffect(() => {
        loadSavedDDL();
    }, []);

    const loadSavedDDL = async () => {
        try {
            const data = await apiClient.getSavedDDL();
            if (data && data.ddl_content) {
                setTrainingDDL(data.ddl_content);
                setLastSaved(new Date(data.created_at).toLocaleString('tr-TR'));
            }
        } catch (error) {
            console.error('Failed to load saved DDL:', error);
        }
    };

    const fetchLiveDDL = async () => {
        setLoadingLive(true);
        try {
            const data = await apiClient.getLiveDDL();
            setLiveDDL(data.ddl);
        } catch (error) {
            alert('Canlı veritabanı şeması çekilemedi.');
        } finally {
            setLoadingLive(false);
        }
    };

    const copyLiveToTraining = () => {
        setTrainingDDL(liveDDL);
    };

    const handleTrainClick = () => {
        if (!trainingDDL.trim()) return;
        setIsConfirmModalOpen(true);
    };

    const confirmTrain = async () => {
        console.log('confirmTrain called');
        console.log('trainingDDL length:', trainingDDL.length);
        setIsConfirmModalOpen(false);
        setLoadingTrain(true);
        try {
            console.log('Calling apiClient.trainDDL...');
            await apiClient.trainDDL(trainingDDL);
            console.log('trainDDL succeeded');
            alert('Başarıyla kaydedildi ve eğitildi! Önbellek temizlendi.');
            setLastSaved(new Date().toLocaleString('tr-TR'));
        } catch (error) {
            console.error('trainDDL error:', error);
            alert('Eğitim sırasında bir hata oluştu.');
        } finally {
            setLoadingTrain(false);
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-black">Veritabanı Şeması & Eğitim</h2>
                {lastSaved && (
                    <span className="text-xs text-gray-500">Son Güncelleme: {lastSaved}</span>
                )}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[600px]">
                {/* Left Pane: Live DB */}
                <div className="flex flex-col border border-gray-200 rounded-lg overflow-hidden">
                    <div className="bg-gray-50 px-4 py-3 border-b border-gray-200 flex items-center justify-between">
                        <h3 className="font-medium text-sm text-gray-700">Canlı Veritabanı</h3>
                        <Button
                            variant="secondary"
                            size="sm"
                            onClick={fetchLiveDDL}
                            disabled={loadingLive}
                            className="text-xs"
                        >
                            {loadingLive ? 'Çekiliyor...' : '🔄 Veritabanından Çek'}
                        </Button>
                    </div>
                    <div className="flex-1 bg-white relative">
                        <textarea
                            className="w-full h-full p-4 font-mono text-xs resize-none focus:outline-none text-gray-600 bg-gray-50"
                            value={liveDDL}
                            readOnly
                            placeholder="Veritabanından şema çekmek için butona tıklayın..."
                        />
                    </div>
                </div>

                {/* Action Buttons (Middle - for mobile logic, simpler to just put copy button in header or similar) */}

                {/* Right Pane: Training DDL */}
                <div className="flex flex-col border border-gray-200 rounded-lg overflow-hidden relative">
                    <div className="bg-gray-50 px-4 py-3 border-b border-gray-200 flex items-center justify-between gap-2">
                        <h3 className="font-medium text-sm text-gray-700">Eğitim Şeması (AI Hafızası)</h3>
                        <div className="flex gap-2">
                            <Button
                                variant="secondary"
                                size="sm"
                                onClick={copyLiveToTraining}
                                disabled={!liveDDL}
                                className="text-xs"
                                title="Soldaki içeriği kopyalar"
                            >
                                ➡️ Kopyala
                            </Button>
                            <Button
                                variant="primary"
                                size="sm"
                                onClick={handleTrainClick}
                                disabled={loadingTrain || !trainingDDL}
                                className="text-xs"
                            >
                                {loadingTrain ? 'İşleniyor...' : '💾 Kaydet ve Eğit (YENİ)'}
                            </Button>
                        </div>
                    </div>

                    <div className="flex-1 bg-white relative">
                        <div className="absolute top-0 left-0 right-0 bg-yellow-50 text-yellow-800 text-[10px] px-2 py-1 border-b border-yellow-100 text-center">
                            ⚠️ Tablo isimlerini değiştirmeyin! Sadece açıklama (-- yorum) ekleyin.
                        </div>
                        <textarea
                            className="w-full h-full p-4 pt-8 font-mono text-xs resize-none focus:outline-none text-black"
                            value={trainingDDL}
                            onChange={(e) => setTrainingDDL(e.target.value)}
                            placeholder="Eğitim için kullanılacak DDL şeması..."
                        />
                    </div>
                </div>
            </div>

            <Modal
                isOpen={isConfirmModalOpen}
                onClose={() => setIsConfirmModalOpen(false)}
                title=""
                size="sm"
            >
                <div className="text-center space-y-6">
                    {/* Icon */}
                    <div className="mx-auto w-16 h-16 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-full flex items-center justify-center shadow-lg">
                        <span className="text-3xl">🚀</span>
                    </div>

                    {/* Title */}
                    <h3 className="text-xl font-bold text-white">
                        AI Modelini Eğit
                    </h3>

                    {/* Description */}
                    <p className="text-gray-400 text-sm leading-relaxed">
                        Bu işlem veritabanı şemasını güncelleyecek ve AI modelini yeniden eğitecektir.
                    </p>

                    {/* Warning Box */}
                    <div className="bg-amber-500/10 border border-amber-500/30 p-4 rounded-xl">
                        <div className="flex items-center gap-2 justify-center">
                            <span className="text-amber-400">⚠️</span>
                            <p className="text-amber-300 text-xs font-medium">
                                Bu işlem geri alınamaz
                            </p>
                        </div>
                    </div>

                    {/* Buttons */}
                    <div className="flex gap-3 pt-2">
                        <button
                            onClick={() => setIsConfirmModalOpen(false)}
                            className="flex-1 px-4 py-3 rounded-xl border border-gray-600 text-gray-300 font-medium hover:bg-gray-700 hover:text-white transition-all duration-200"
                        >
                            İptal
                        </button>
                        <button
                            onClick={confirmTrain}
                            className="flex-1 px-4 py-3 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-medium hover:from-purple-700 hover:to-indigo-700 transition-all duration-200 shadow-lg shadow-purple-500/25"
                        >
                            Onayla ve Eğit
                        </button>
                    </div>
                </div>
            </Modal>
        </div>
    );
}
