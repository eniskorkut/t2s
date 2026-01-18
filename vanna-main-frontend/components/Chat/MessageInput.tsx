/**
 * Message Input component
 * Following Single Responsibility Principle - only handles message input
 * Following Open/Closed Principle - extensible via props
 */

'use client';

import React, { useState, useRef, useEffect } from 'react';

export interface MessageInputProps {
  onSend: (message: string) => Promise<void>;
  disabled?: boolean;
  placeholder?: string;
  requireAuth?: boolean;
}

export default function MessageInput({
  onSend,
  disabled = false,
  placeholder = 'Bir soru sorun...',
  requireAuth = false,
}: MessageInputProps) {
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || isLoading || disabled || requireAuth) return;

    const messageToSend = message.trim();
    setMessage('');
    setIsLoading(true);

    try {
      await onSend(messageToSend);
    } finally {
      setIsLoading(false);
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        200
      )}px`;
    }
  }, [message]);

  return (
    <div className="p-6 bg-white border-t border-gray-200">
      <form onSubmit={handleSubmit} className="max-w-4xl mx-auto relative">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          onClick={requireAuth ? () => {} : undefined}
          placeholder={placeholder}
          className="w-full p-3 pr-12 bg-white border border-gray-300 rounded-xl text-black resize-none min-h-[52px] max-h-[200px] focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent placeholder:text-gray-500"
          rows={1}
          disabled={disabled || isLoading || requireAuth}
        />
        <button
          type="submit"
          disabled={!message.trim() || isLoading || disabled}
          className="absolute right-2 bottom-2 w-9 h-9 rounded-lg bg-black text-white flex items-center justify-center hover:bg-gray-800 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path
                d="M17.5 2.5L2.5 10L8.75 11.25L17.5 2.5Z"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M17.5 2.5L12.5 17.5L8.75 11.25L2.5 10L12.5 17.5"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          )}
        </button>
      </form>
    </div>
  );
}
