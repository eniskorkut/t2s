/**
 * Chat Landing component - ChatGPT style
 * Following Single Responsibility Principle - only handles landing UI
 */
'use client';

import React from 'react';
import { useAuth } from '@/context/AuthContext';

export interface ChatLandingProps {
  onInputClick: () => void;
}

export default function ChatLanding({ onInputClick }: ChatLandingProps) {
  const { user } = useAuth();

  return (
    <div className="flex-1 flex flex-col items-center justify-center px-4 bg-white">
      <div className="w-full max-w-3xl">
        <h1 className="text-4xl md:text-5xl font-semibold text-center text-black mb-8">
          Bugün aklında ne var?
        </h1>

        <div className="flex items-center justify-center gap-2 mt-4 flex-wrap">
          <button
            onClick={onInputClick}
            className="px-3 py-2 text-sm text-black hover:bg-gray-100 rounded-lg transition flex items-center gap-2"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M8 2L2 6L8 10L14 6L8 2Z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2 10L8 14L14 10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Ekle
          </button>
          <button
            onClick={onInputClick}
            className="px-3 py-2 text-sm text-black hover:bg-gray-100 rounded-lg transition flex items-center gap-2"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="1.5"/>
              <path d="M8 4V8L11 11" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
            Ara
          </button>
          <button
            onClick={onInputClick}
            className="px-3 py-2 text-sm text-black hover:bg-gray-100 rounded-lg transition flex items-center gap-2"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <rect x="2" y="3" width="12" height="10" rx="1" stroke="currentColor" strokeWidth="1.5"/>
              <path d="M2 6H14" stroke="currentColor" strokeWidth="1.5"/>
            </svg>
            Çalış
          </button>
          <button
            onClick={onInputClick}
            className="px-3 py-2 text-sm text-black hover:bg-gray-100 rounded-lg transition flex items-center gap-2"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <rect x="2" y="2" width="12" height="12" rx="1" stroke="currentColor" strokeWidth="1.5"/>
              <circle cx="6" cy="6" r="1.5" fill="currentColor"/>
              <path d="M2 10L6 6L10 10L14 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
            Görsel oluştur
          </button>
          <button
            onClick={onInputClick}
            className="px-3 py-2 text-sm text-black hover:bg-gray-100 rounded-lg transition flex items-center gap-2"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M8 2V14M2 8H14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
              <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="1.5"/>
            </svg>
            Ses
          </button>
        </div>
      </div>
    </div>
  );
}
