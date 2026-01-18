/**
 * Chat Container component
 * Following Single Responsibility Principle - orchestrates chat functionality
 * Following Dependency Inversion Principle - depends on hooks abstractions
 */

'use client';

import React, { useRef, useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useChat } from '@/hooks/useChat';
import { useQuerySave } from '@/hooks/useQuerySave';
import Message from './Message';
import MessageInput from './MessageInput';
import ChatLanding from './ChatLanding';
import ChatSidebar from './ChatSidebar';
import QueriesList from '@/components/Queries/QueriesList';
import { LoginModal } from '@/components/Auth/LoginModal';
import { RegisterModal } from '@/components/Auth/RegisterModal';
import { ResetPasswordModal } from '@/components/Auth/ResetPasswordModal';
import { MessageSkeleton } from '@/components/UI/Skeleton';

export default function ChatContainer() {
  const { user, logout } = useAuth();
  const {
    messages,
    isLoading,
    sessionId,
    sessionTitle,
    sendMessage,
    clearMessages,
    loadSession,
    updateSessionTitle
  } = useChat();
  const { saveQuery } = useQuerySave();
  const [currentQuestion, setCurrentQuestion] = useState<string>('');
  const [showLogin, setShowLogin] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  const [showResetPassword, setShowResetPassword] = useState(false);
  const [view, setView] = useState<'chat' | 'queries'>('chat');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (text: string) => {
    // Check if user is logged in
    if (!user) {
      setShowLogin(true);
      return;
    }

    setCurrentQuestion(text);
    await sendMessage(text);
  };

  const handleSuggestionClick = async (suggestion: string) => {
    // Öneriye tıklandığında yeni bir mesaj gönder
    await handleSendMessage(suggestion);
  };

  const handleSaveQuery = async (question: string, sql: string, isCorrect: boolean) => {
    if (!isCorrect) return;

    const success = await saveQuery(question, sql, true);
    if (success) {
      // Optionally add a success message to chat
      // This could be handled by the chat hook or a notification system
    }
  };

  const handleInputClick = () => {
    if (!user) {
      setShowLogin(true);
    }
  };

  const handleNewChat = () => {
    clearMessages();
    setView('chat');
  };

  const handleLogout = async () => {
    await logout();
    clearMessages();
    setView('chat');
  };

  const handleSessionSelect = async (loadSessionId: string) => {
    await loadSession(loadSessionId);
    setView('chat');
  };

  // Find the user question for the last assistant message with SQL
  const getUserQuestionForMessage = (messageIndex: number): string | undefined => {
    if (messageIndex === 0) return undefined;

    // Look backwards for the user message
    for (let i = messageIndex - 1; i >= 0; i--) {
      if (messages[i].role === 'user') {
        return messages[i].content;
      }
    }
    return currentQuestion;
  };

  return (
    <>
      <div className={`flex h-screen bg-white text-black ${!user ? 'pt-14' : ''}`}>
        {/* Sidebar - only show when user is logged in */}
        {user && (
          <ChatSidebar
            user={user}
            onLogout={handleLogout}
            view={view}
            onViewChange={setView}
            onNewChat={handleNewChat}
            onSessionSelect={handleSessionSelect}
            currentSessionId={sessionId}
            currentSessionTitle={sessionTitle}
            isOpen={sidebarOpen}
            onToggle={() => setSidebarOpen(!sidebarOpen)}
          />
        )}

        {/* Main Content Area */}
        <div className={`flex-1 flex flex-col overflow-hidden transition-all duration-300 ${user && sidebarOpen ? '' : ''
          }`}>
          {view === 'chat' ? (
            <>
              {messages.length === 0 ? (
                <ChatLanding onInputClick={handleInputClick} />
              ) : (
                <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-white">
                  {messages.map((msg, idx) => (
                    <Message
                      key={idx}
                      message={msg}
                      userQuestion={getUserQuestionForMessage(idx)}
                      onSaveQuery={handleSaveQuery}
                      onSuggestionClick={handleSuggestionClick}
                    />
                  ))}
                  {isLoading && <MessageSkeleton />}
                  <div ref={messagesEndRef} />
                </div>
              )}
              <MessageInput
                onSend={handleSendMessage}
                disabled={isLoading}
                requireAuth={!user}
                placeholder={user ? 'Herhangi bir şey sor' : 'Giriş yaparak soru sorabilirsiniz'}
              />
            </>
          ) : (
            <div className="flex-1 overflow-y-auto p-6 bg-white">
              <QueriesList />
            </div>
          )}
        </div>
      </div>

      <LoginModal
        isOpen={showLogin}
        onClose={() => setShowLogin(false)}
        onSwitchToRegister={() => {
          setShowLogin(false);
          setShowRegister(true);
        }}
        onSwitchToResetPassword={() => {
          setShowLogin(false);
          setShowResetPassword(true);
        }}
        asModal={true}
      />
      <RegisterModal
        isOpen={showRegister}
        onClose={() => setShowRegister(false)}
        onSwitchToLogin={() => {
          setShowRegister(false);
          setShowLogin(true);
        }}
        asModal={true}
      />
      <ResetPasswordModal
        isOpen={showResetPassword}
        onClose={() => setShowResetPassword(false)}
        onSwitchToLogin={() => {
          setShowResetPassword(false);
          setShowLogin(true);
        }}
        asModal={true}
      />
    </>
  );
}
