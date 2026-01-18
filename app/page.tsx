/**
 * Home Page
 * Following Single Responsibility Principle - only handles routing and auth state
 * Following Dependency Inversion Principle - depends on context and component abstractions
 */

'use client';

import React from 'react';
import { useAuth } from '@/context/AuthContext';
import ChatContainer from '@/components/Chat/ChatContainer';
import Header from '@/components/Layout/Header';

export default function Home() {
  const { loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-[#343541]">
        <div className="text-center">
          <div className="inline-block w-12 h-12 border-4 border-white/30 border-t-[#10a37f] rounded-full animate-spin mb-4" />
          <p className="text-[#ececf1]">Yükleniyor...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Header />
      <ChatContainer />
    </>
  );
}
