/**
 * Chat Sidebar component - Professional Minimal Design
 * Following Single Responsibility Principle - handles sidebar UI and chat history
 * Following Open/Closed Principle - extensible via props
 */

'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import type { User, ChatSession } from '@/lib/types';
import { Button } from '@/components/UI/Button';
import { apiClient } from '@/lib/api/ApiClient';
import {
  PlusIcon,
  MoreVerticalIcon,
  EditIcon,
  PinIcon,
  TrashIcon,
  ChevronDownIcon,
  LogOutIcon,
  ChevronLeftIcon
} from '@/components/UI/Icons';

export interface ChatSidebarProps {
  user: User;
  onLogout: () => void;
  view: 'chat' | 'queries';
  onViewChange: (view: 'chat' | 'queries') => void;
  onNewChat: () => void;
  onSessionSelect: (sessionId: string) => void;
  currentSessionId?: string | null;
  currentSessionTitle?: string | null;
  isOpen: boolean;
  onToggle: () => void;
}

export default function ChatSidebar({
  user,
  onLogout,
  view,
  onViewChange,
  onNewChat,
  onSessionSelect,
  currentSessionId,
  currentSessionTitle,
  isOpen,
  onToggle,
}: ChatSidebarProps) {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const lastFetchedIdRef = useRef<string | null>(null);
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const userMenuRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  // Load chat history initially
  useEffect(() => {
    loadChatHistory();
  }, []);

  // Reload chat history when a new session is created
  useEffect(() => {
    if (currentSessionId &&
      !currentSessionId.startsWith('temp-') &&
      currentSessionId !== lastFetchedIdRef.current &&
      !sessions.find(s => s.id === currentSessionId)) {
      lastFetchedIdRef.current = currentSessionId;
      loadChatHistory();
    }
  }, [currentSessionId, sessions]);

  // Close menus when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setOpenMenuId(null);
      }
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setUserMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const loadChatHistory = async () => {
    try {
      const response = await apiClient.getChatHistory();
      if (response.success) {
        setSessions(response.sessions);
      }
    } catch (error) {
      console.error('Failed to load chat history:', error);
    }
  };

  const handleEditStart = (session: ChatSession) => {
    setEditingSessionId(session.id);
    setEditTitle(session.title);
    setOpenMenuId(null);
  };

  const handleEditSave = async (sessionId: string) => {
    if (!editTitle.trim()) return;

    try {
      await apiClient.updateChatTitle(sessionId, editTitle.trim());
      setSessions(prev =>
        prev.map(s => (s.id === sessionId ? { ...s, title: editTitle.trim() } : s))
      );
      setEditingSessionId(null);
      setEditTitle('');
    } catch (error) {
      console.error('Failed to update title:', error);
    }
  };

  const handleEditCancel = () => {
    setEditingSessionId(null);
    setEditTitle('');
  };

  const handleTogglePin = async (sessionId: string) => {
    try {
      await apiClient.toggleChatPin(sessionId);
      await loadChatHistory(); // Reload to get updated order
      setOpenMenuId(null);
    } catch (error) {
      console.error('Failed to toggle pin:', error);
    }
  };

  const handleDelete = async (sessionId: string) => {
    if (!confirm('Bu sohbeti silmek istediğinizden emin misiniz?')) return;

    try {
      await apiClient.deleteChatSession(sessionId);
      setSessions(prev => prev.filter(s => s.id !== sessionId));
      setOpenMenuId(null);

      // Eğer şu anki session siliniyorsa, yeni sohbet başlat
      if (sessionId === currentSessionId) {
        onNewChat();
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
    }
  };

  // Optimistic new session (geçici session ekle - loading efekti ile)
  const optimisticSession: ChatSession | null =
    currentSessionId && currentSessionTitle && !sessions.find(s => s.id === currentSessionId)
      ? {
        id: currentSessionId,
        title: currentSessionTitle,
        is_pinned: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }
      : null;

  // Combine real sessions with optimistic session
  const allSessions = optimisticSession
    ? [optimisticSession, ...sessions]
    : sessions;

  // Separate pinned and unpinned sessions
  const pinnedSessions = allSessions.filter(s => s.is_pinned);
  const unpinnedSessions = allSessions.filter(s => !s.is_pinned);

  return (
    <>
      {/* Toggle Button - Fixed Position, Always Visible */}
      <button
        onClick={onToggle}
        className={`fixed top-4 z-50 p-2.5 bg-white border border-gray-200 shadow-lg hover:bg-gray-50 transition-all duration-300 ${isOpen ? 'left-64 rounded-r-lg' : 'left-0 rounded-r-lg'
          }`}
        title={isOpen ? 'Sidebar\'ı Kapat' : 'Sidebar\'ı Aç'}
      >
        <ChevronLeftIcon
          size={20}
          className={`text-gray-600 transition-transform duration-300 ${isOpen ? '' : 'rotate-180'
            }`}
        />
      </button>

      <div className={`bg-white flex flex-col border-r border-gray-200 h-full transition-all duration-300 ${isOpen ? 'w-64' : 'w-0'
        } overflow-hidden`}>
        {/* Header with Logo */}
        <div className="px-4 pt-4 pb-3 border-b border-gray-200 flex-shrink-0">
          <h1 className="text-xl font-bold text-black mb-3">Vanna AI</h1>
          <Button
            variant="primary"
            onClick={onNewChat}
            className="w-full flex items-center justify-center gap-2"
          >
            <PlusIcon size={18} />
            <span>Yeni Sohbet</span>
          </Button>
        </div>

        {/* Menu Navigation - Top */}
        <div className="border-b border-gray-200">
          <button
            onClick={() => onViewChange('chat')}
            className={`w-full px-4 py-2.5 text-sm font-medium text-left transition-colors ${view === 'chat'
              ? 'bg-gray-100 text-black'
              : 'text-gray-600 hover:bg-gray-50 hover:text-black'
              }`}
          >
            Sohbet
          </button>
          <button
            onClick={() => onViewChange('queries')}
            className={`w-full px-4 py-2.5 text-sm font-medium text-left transition-colors border-t border-gray-200 ${view === 'queries'
              ? 'bg-gray-100 text-black'
              : 'text-gray-600 hover:bg-gray-50 hover:text-black'
              }`}
          >
            Kayıtlı Sorgular
          </button>
        </div>

        {/* Content Area - Scrollable (flex-1) */}
        <div className="flex-1 overflow-y-auto">
          {view === 'chat' && (
            <>
              {allSessions.length === 0 && (
                <div className="px-4 py-8 text-center text-sm text-gray-400">
                  Henüz sohbet yok
                </div>
              )}

              {allSessions.length > 0 && (
                <div className="py-2">
                  {/* Pinned Section */}
                  {pinnedSessions.length > 0 && (
                    <>
                      <div className="px-4 py-2 text-xs font-semibold text-gray-400 uppercase">
                        Sabitlenenler
                      </div>
                      {pinnedSessions.map((session) => (
                        <ChatListItem
                          key={session.id}
                          session={session}
                          isActive={session.id === currentSessionId}
                          isEditing={editingSessionId === session.id}
                          editTitle={editTitle}
                          onEditTitleChange={setEditTitle}
                          onEditSave={() => handleEditSave(session.id)}
                          onEditCancel={handleEditCancel}
                          onClick={() => onSessionSelect(session.id)}
                          onMenuToggle={() => setOpenMenuId(openMenuId === session.id ? null : session.id)}
                          isMenuOpen={openMenuId === session.id}
                          onEdit={() => handleEditStart(session)}
                          onPin={() => handleTogglePin(session.id)}
                          onDelete={() => handleDelete(session.id)}
                          menuRef={menuRef}
                          isOptimistic={session.id === optimisticSession?.id}
                        />
                      ))}
                    </>
                  )}

                  {/* Unpinned Section */}
                  {unpinnedSessions.length > 0 && (
                    <>
                      {pinnedSessions.length > 0 && (
                        <div className="px-4 py-2 text-xs font-semibold text-gray-400 uppercase mt-2">
                          Diğerleri
                        </div>
                      )}
                      {unpinnedSessions.map((session) => (
                        <ChatListItem
                          key={session.id}
                          session={session}
                          isActive={session.id === currentSessionId}
                          isEditing={editingSessionId === session.id}
                          editTitle={editTitle}
                          onEditTitleChange={setEditTitle}
                          onEditSave={() => handleEditSave(session.id)}
                          onEditCancel={handleEditCancel}
                          onClick={() => onSessionSelect(session.id)}
                          onMenuToggle={() => setOpenMenuId(openMenuId === session.id ? null : session.id)}
                          isMenuOpen={openMenuId === session.id}
                          onEdit={() => handleEditStart(session)}
                          onPin={() => handleTogglePin(session.id)}
                          onDelete={() => handleDelete(session.id)}
                          menuRef={menuRef}
                          isOptimistic={session.id === optimisticSession?.id}
                        />
                      ))}
                    </>
                  )}
                </div>
              )}
            </>
          )}

          {view === 'queries' && (
            <div className="px-4 py-8 text-center text-sm text-gray-400">
              {/* Queries content will be shown in main area */}
            </div>
          )}
        </div>

        {/* User Profile - Fixed at Bottom */}
        <div className="relative border-t border-gray-200" ref={userMenuRef}>
          <button
            onClick={() => setUserMenuOpen(!userMenuOpen)}
            className="w-full px-4 py-3 flex items-center gap-2 hover:bg-gray-50 transition-colors"
          >
            <div className="w-8 h-8 rounded-full bg-[#10a37f] flex items-center justify-center text-white text-xs font-semibold flex-shrink-0">
              {user.email.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 min-w-0 text-left">
              <div className="text-xs text-gray-500">Kullanıcı Bilgileri</div>
            </div>
            <ChevronDownIcon
              size={16}
              className={`text-gray-500 transition-transform ${userMenuOpen ? 'rotate-180' : ''}`}
            />
          </button>

          {/* User Dropdown Menu */}
          {userMenuOpen && (
            <div className="absolute bottom-full left-0 right-0 mb-1 mx-2 bg-white border border-gray-200 rounded-lg shadow-lg">
              <div className="px-4 py-3 border-b border-gray-200">
                <div className="text-xs text-gray-500 mb-1">Giriş Yapılan Hesap</div>
                <div className="text-sm text-black font-medium truncate">{user.email}</div>
              </div>
              {user.role === 'admin' && (
                <Link
                  href="/admin"
                  className="w-full px-4 py-2.5 text-sm text-left hover:bg-gray-50 flex items-center gap-2 text-black"
                  onClick={() => setUserMenuOpen(false)}
                >
                  <span>⚙️ Admin Paneli</span>
                </Link>
              )}

              <button
                onClick={() => {
                  setUserMenuOpen(false);
                  onLogout();
                }}
                className="w-full px-4 py-2.5 text-sm text-left hover:bg-gray-50 flex items-center gap-2 text-red-600"
              >
                <LogOutIcon size={16} />
                <span>Çıkış Yap</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

// Chat List Item Component
interface ChatListItemProps {
  session: ChatSession;
  isActive: boolean;
  isEditing: boolean;
  editTitle: string;
  onEditTitleChange: (value: string) => void;
  onEditSave: () => void;
  onEditCancel: () => void;
  onClick: () => void;
  onMenuToggle: () => void;
  isMenuOpen: boolean;
  onEdit: () => void;
  onPin: () => void;
  onDelete: () => void;
  menuRef: React.RefObject<HTMLDivElement | null>;
  isOptimistic?: boolean;
}

function ChatListItem({
  session,
  isActive,
  isEditing,
  editTitle,
  onEditTitleChange,
  onEditSave,
  onEditCancel,
  onClick,
  onMenuToggle,
  isMenuOpen,
  onEdit,
  onPin,
  onDelete,
  menuRef,
  isOptimistic = false,
}: ChatListItemProps) {
  const [displayTitle, setDisplayTitle] = useState(session.title);
  const [isTyping, setIsTyping] = useState(false);

  // Typewriter effect when title changes from "New Chat" to real title
  useEffect(() => {
    // Eğer başlık "New Chat"tan başka bir şeye değiştiyse typewriter başlat
    if (displayTitle === 'New Chat' && session.title !== 'New Chat' && session.title !== displayTitle) {
      setIsTyping(true);
      let currentIndex = 0;
      const targetTitle = session.title;

      const TYPING_SPEED = 480; // ms per character (daha yavaş = daha gerçekçi: 80-100ms önerilen)

      const typeInterval = setInterval(() => {
        currentIndex++;
        setDisplayTitle(targetTitle.slice(0, currentIndex));

        if (currentIndex >= targetTitle.length) {
          clearInterval(typeInterval);
          setIsTyping(false);
        }
      }, TYPING_SPEED);

      return () => clearInterval(typeInterval);
    } else if (session.title !== displayTitle && !isTyping) {
      // Başlık doğrudan değiştiyse (edit vs.), typewriter olmadan güncelle
      setDisplayTitle(session.title);
    }
  }, [session.title]);

  if (isEditing) {
    return (
      <div className="px-4 py-2" onClick={(e) => e.stopPropagation()}>
        <input
          type="text"
          value={editTitle}
          onChange={(e) => onEditTitleChange(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') onEditSave();
            if (e.key === 'Escape') onEditCancel();
          }}
          className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-black text-black"
          autoFocus
        />
      </div>
    );
  }

  return (
    <div
      className={`relative group px-4 py-2.5 cursor-pointer transition-colors ${isActive ? 'bg-gray-100' : 'hover:bg-gray-50'
        }`}
      onClick={onClick}
    >
      <div className="flex items-center gap-2">
        <div className="flex-1 min-w-0">
          <div className="text-sm text-black truncate">
            {displayTitle}
            {isTyping && <span className="animate-pulse">|</span>}
          </div>
        </div>
        {!isOptimistic && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onMenuToggle();
            }}
            className="p-1 hover:bg-gray-200 rounded opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <MoreVerticalIcon size={16} className="text-gray-600" />
          </button>
        )}
      </div>

      {/* Dropdown Menu */}
      {isMenuOpen && !isOptimistic && (
        <div
          ref={menuRef}
          className="absolute right-2 top-10 bg-white border border-gray-200 rounded-lg shadow-lg z-50 min-w-[160px]"
          onClick={(e) => e.stopPropagation()}
        >
          <button
            onClick={onEdit}
            className="w-full px-4 py-2 text-sm text-left hover:bg-gray-50 flex items-center gap-2 text-black"
          >
            <EditIcon size={14} />
            <span>Yeniden Adlandır</span>
          </button>
          <button
            onClick={onPin}
            className="w-full px-4 py-2 text-sm text-left hover:bg-gray-50 flex items-center gap-2 text-black"
          >
            <PinIcon size={14} />
            <span>{session.is_pinned ? 'Sabitlemeyi Kaldır' : 'Sabitle'}</span>
          </button>
          <div className="border-t border-gray-200"></div>
          <button
            onClick={onDelete}
            className="w-full px-4 py-2 text-sm text-left hover:bg-red-50 flex items-center gap-2 text-red-600"
          >
            <TrashIcon size={14} />
            <span>Sil</span>
          </button>
        </div>
      )}
    </div>
  );
}
