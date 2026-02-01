'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import toast from 'react-hot-toast';
import { apiClient } from '@/lib/api/ApiClient';
import type { User } from '@/lib/types';
import { Button } from '@/components/UI/Button';
import { Modal } from '@/components/UI/Modal';
import {
    ChevronLeftIcon, SearchIcon, DatabaseIcon, UserIcon,
    ZapIcon, RefreshCwIcon, SaveIcon, AlertTriangleIcon
} from '@/components/UI/Icons';

export default function AdminPage() {
    const router = useRouter();
    const [activeTab, setActiveTab] = useState<'users' | 'database' | 'scanner'>('users');
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

    const renderContent = () => {
        switch (activeTab) {
            case 'users': return <UserManagement />;
            case 'database': return <DatabaseManagement />;
            case 'scanner': return <DataScannerManagement />;
            default: return null;
        }
    };

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
                                className={`flex items-center gap-2 py-4 px-6 font-medium text-sm border-b-2 transition-colors ${activeTab === 'users'
                                    ? 'border-black text-black'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    }`}
                            >
                                <UserIcon size={16} />
                                Kullanıcı Yönetimi
                            </button>
                            <button
                                onClick={() => setActiveTab('database')}
                                className={`flex items-center gap-2 py-4 px-6 font-medium text-sm border-b-2 transition-colors ${activeTab === 'database'
                                    ? 'border-black text-black'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    }`}
                            >
                                <DatabaseIcon size={16} />
                                Veritabanı & Eğitim
                            </button>
                            <button
                                onClick={() => setActiveTab('scanner')}
                                className={`flex items-center gap-2 py-4 px-6 font-medium text-sm border-b-2 transition-colors ${activeTab === 'scanner'
                                    ? 'border-black text-black'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    }`}
                            >
                                <SearchIcon size={16} />
                                Veri Tarayıcı
                            </button>
                        </nav>
                    </div>

                    <div className="p-6">
                        {renderContent()}
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

function DataScannerManagement() {
    const [status, setStatus] = useState<{ last_run: string | null; next_run: string | null; is_running: boolean } | null>(null);
    const [timeLeft, setTimeLeft] = useState<string>('');
    const [loading, setLoading] = useState(false);
    const [isScanModalOpen, setIsScanModalOpen] = useState(false);

    const [prevRunning, setPrevRunning] = useState(false);

    useEffect(() => {
        fetchStatus();
        const interval = setInterval(fetchStatus, 30000); // Sync with server every 30s
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        if (status) {
            // Check for completion: was running, now not running
            if (prevRunning && !status.is_running) {
                toast.success('Veri tarama işlemi başarıyla tamamlandı!', {
                    duration: 5000,
                    icon: '✅',
                    style: {
                        background: '#10B981',
                        color: '#fff',
                    }
                });
            }
            setPrevRunning(status.is_running);
        }
    }, [status]);

    useEffect(() => {
        if (!status?.next_run) return;

        const timer = setInterval(() => {
            const now = new Date();
            const target = new Date(status.next_run!);
            const diff = target.getTime() - now.getTime();

            if (diff <= 0) {
                setTimeLeft('Şuan çalışıyor...');
            } else {
                const hours = Math.floor(diff / (1000 * 60 * 60));
                const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((diff % (1000 * 60)) / 1000);
                setTimeLeft(`${hours}sa ${minutes}dk ${seconds}sn`);
            }
        }, 1000);

        return () => clearInterval(timer);
    }, [status]);

    const fetchStatus = async () => {
        try {
            const data = await apiClient.getScannerStatus();
            setStatus(data);
        } catch (error) {
            console.error('Failed to fetch scanner status:', error);
        }
    };

    const handleScanClick = () => {
        setIsScanModalOpen(true);
    };

    const confirmScan = async () => {
        setIsScanModalOpen(false);
        setLoading(true);
        try {
            toast.loading('Veri taraması başlatılıyor...', { id: 'scan-toast' });
            const res = await apiClient.scanData();
            if (res.success) {
                toast.success('Tarama işlemi arka planda başlatıldı!', { id: 'scan-toast' });
                // Optimistically update status to running to trigger the logic correctly if needed
                setPrevRunning(true);
                fetchStatus();
            }
        } catch (e) {
            toast.error('İşlem başlatılamadı.', { id: 'scan-toast' });
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
            <div className="flex flex-col md:flex-row md:items-start justify-between gap-6">
                <div>
                    <div className="flex items-center gap-2 mb-2">
                        <SearchIcon size={20} className="text-gray-700" />
                        <h3 className="text-lg font-semibold text-black">Akıllı Veri Tarayıcı</h3>
                        {status?.is_running && (
                            <span className="px-2 py-0.5 text-[10px] font-bold bg-green-100 text-green-700 rounded-full animate-pulse">
                                ÇALIŞIYOR
                            </span>
                        )}
                    </div>
                    <p className="text-gray-600 text-sm max-w-2xl">
                        Bu özellik, veritabanınızdaki kategorik verileri (Departman İsimleri, Ürün Kategorileri, Şehirler vb.)
                        otomatik olarak tarar ve Yapay Zeka'ya öğretir. <br />
                        <span className="font-medium mt-1 inline-block text-purple-700 flex items-center gap-1">
                            <ZapIcon size={12} />
                            Faydası: AI'nın olmayan verileri uydurmasını engeller ve filtreleme sorgularında %95+ başarı sağlar.
                        </span>
                    </p>

                    <div className="mt-4 flex flex-wrap gap-4">
                        <div className="bg-gray-50 px-3 py-2 rounded-md border border-gray-100">
                            <span className="text-xs text-gray-500 block mb-1">Otomatik Tarama (Her gece 23:59)</span>
                            <div className="text-sm font-mono font-medium text-black flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                                {timeLeft || 'Hesaplanıyor...'}
                            </div>
                        </div>

                        <div className="bg-gray-50 px-3 py-2 rounded-md border border-gray-100">
                            <span className="text-xs text-gray-500 block mb-1">Son Tarama</span>
                            <div className="text-sm font-medium text-black">
                                {status?.last_run
                                    ? new Date(status.last_run).toLocaleString('tr-TR')
                                    : 'Henüz taranmadı'}
                            </div>
                        </div>
                    </div>
                </div>

                <Button
                    variant="primary"
                    className="flex items-center gap-2 whitespace-nowrap"
                    onClick={handleScanClick}
                    disabled={loading || status?.is_running}
                >
                    <RefreshCwIcon size={14} className={loading || status?.is_running ? 'animate-spin' : ''} />
                    {loading || status?.is_running ? 'Taranıyor...' : 'Şimdi Tara'}
                </Button>
            </div>

            <Modal
                isOpen={isScanModalOpen}
                onClose={() => setIsScanModalOpen(false)}
                title=""
                size="sm"
            >
                <div className="text-center space-y-6">
                    {/* Icon */}
                    <div className="mx-auto w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center">
                        <RefreshCwIcon size={32} className="text-blue-600" />
                    </div>

                    {/* Title */}
                    <h3 className="text-xl font-bold text-black">
                        Veri Taraması Başlatılsın mı?
                    </h3>

                    {/* Description */}
                    <p className="text-gray-500 text-sm leading-relaxed">
                        Bu işlem veritabanı boyutuna göre <strong>1-2 dakika</strong> sürebilir.
                        İşlem arka planda çalışacağı için sayfayı kapatabilirsiniz.
                    </p>

                    {/* Warning Box */}
                    <div className="bg-blue-50 border border-blue-100 p-4 rounded-xl">
                        <div className="flex items-center gap-2 justify-center">
                            <ZapIcon size={16} className="text-blue-600" />
                            <p className="text-blue-700 text-xs font-medium">
                                AI doğruluğunu anında artırır
                            </p>
                        </div>
                    </div>

                    {/* Buttons */}
                    <div className="flex gap-3 pt-2">
                        <button
                            onClick={() => setIsScanModalOpen(false)}
                            className="flex-1 px-4 py-3 rounded-xl border border-gray-300 text-gray-600 font-medium hover:bg-gray-50 transition-all duration-200"
                        >
                            İptal
                        </button>
                        <button
                            onClick={confirmScan}
                            className="flex-1 px-4 py-3 rounded-xl bg-black text-white font-medium hover:bg-gray-800 transition-all duration-200 shadow-md"
                        >
                            Taramayı Başlat
                        </button>
                    </div>
                </div>
            </Modal>
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
            const response = await apiClient.trainDDL(trainingDDL);
            console.log('trainDDL succeeded');

            // Show toast based on response
            if (response.success) {
                toast.success('Eğitim işlemi arka planda başlatıldı! Tamamlandığında önbellek temizlenecek.', {
                    duration: 5000,
                    style: {
                        background: '#10B981',
                        color: '#fff',
                    },
                    iconTheme: {
                        primary: '#fff',
                        secondary: '#10B981',
                    },
                });
            } else {
                toast.success('İşlem alındı.', {
                    duration: 4000
                });
            }

            setLastSaved(new Date().toLocaleString('tr-TR'));
        } catch (error) {
            console.error('trainDDL error:', error);
            toast.error('Eğitim başlatılırken bir hata oluştu.', {
                duration: 4000
            });
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
                            className="text-xs flex items-center gap-1"
                        >
                            <RefreshCwIcon size={12} className={loadingLive ? 'animate-spin' : ''} />
                            {loadingLive ? 'Çekiliyor...' : 'Veritabanından Çek'}
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
                                Kopyala
                            </Button>
                            <Button
                                variant="primary"
                                size="sm"
                                onClick={handleTrainClick}
                                disabled={loadingTrain || !trainingDDL}
                                className="text-xs flex items-center gap-1"
                            >
                                {loadingTrain ? (
                                    <>İşleniyor...</>
                                ) : (
                                    <>
                                        <SaveIcon size={12} />
                                        Kaydet ve Eğit (YENİ)
                                    </>
                                )}
                            </Button>
                        </div>
                    </div>

                    <div className="flex-1 bg-white relative">
                        <div className="absolute top-0 left-0 right-0 bg-yellow-50 text-yellow-800 text-[10px] px-2 py-1 border-b border-yellow-100 text-center flex items-center justify-center gap-1">
                            <AlertTriangleIcon size={10} />
                            Tablo isimlerini değiştirmeyin! Sadece açıklama (-- yorum) ekleyin.
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
                    <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
                        <SaveIcon size={32} className="text-black" />
                    </div>

                    {/* Title */}
                    <h3 className="text-xl font-bold text-black">
                        AI Modelini Eğit
                    </h3>

                    {/* Description */}
                    <p className="text-gray-500 text-sm leading-relaxed">
                        Bu işlem veritabanı şemasını güncelleyecek ve AI modelini yeniden eğitecektir.
                    </p>

                    {/* Warning Box */}
                    <div className="bg-amber-50 border border-amber-200 p-4 rounded-xl">
                        <div className="flex items-center gap-2 justify-center">
                            <AlertTriangleIcon size={16} className="text-amber-600" />
                            <p className="text-amber-700 text-xs font-medium">
                                Bu işlem geri alınamaz
                            </p>
                        </div>
                    </div>

                    {/* Buttons */}
                    <div className="flex gap-3 pt-2">
                        <button
                            onClick={() => setIsConfirmModalOpen(false)}
                            className="flex-1 px-4 py-3 rounded-xl border border-gray-300 text-gray-600 font-medium hover:bg-gray-50 transition-all duration-200"
                        >
                            İptal
                        </button>
                        <button
                            onClick={confirmTrain}
                            className="flex-1 px-4 py-3 rounded-xl bg-black text-white font-medium hover:bg-gray-800 transition-all duration-200 shadow-md"
                        >
                            Onayla ve Eğit
                        </button>
                    </div>
                </div>
            </Modal>
        </div>
    );
}
