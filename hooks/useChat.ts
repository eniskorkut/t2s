/**
 * Chat hook
 * Following Single Responsibility Principle - only handles chat message logic
 * Following Dependency Inversion Principle - depends on IQueryApi interface
 * 
 * NOT: Tüm backend mantığı backend'de işlenir. Frontend sadece UI ve HTTP çağrıları yapar.
 */

import { useState, useCallback } from 'react';
import type { IQueryApi } from '@/lib/types/api.types';
import type { Message, SQLGenerationResponse, SQLExecutionResponse } from '@/lib/types';
import { apiClient } from '@/lib/api/ApiClient';
import { ApiError } from '@/lib/errors/ApiError';

interface UseChatOptions {
  queryApi?: IQueryApi; // Dependency Injection for testing
}

interface UseChatReturn {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  sessionId: string | null;
  sessionTitle: string | null;
  sendMessage: (text: string) => Promise<void>;
  clearMessages: () => void;
  clearError: () => void;
  loadSession: (sessionId: string) => Promise<void>;
  updateSessionTitle: (newTitle: string) => Promise<void>;
}

export function useChat(options: UseChatOptions = {}): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionTitle, setSessionTitle] = useState<string | null>(null);

  // Use injected API client or default singleton
  const queryApi: IQueryApi = options.queryApi || apiClient;

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: text.trim(),
      timestamp: new Date(),
    };

    // Optimistically update UI
    setMessages((prev) => [...prev, userMessage]);

    setIsLoading(true);
    setError(null);

    try {
      // İlk mesaj mı kontrol et
      const isFirstMessage = messages.length === 0 && !sessionId;
      let currentActiveSessionId = sessionId;
      
      // İlk mesajsa yeni session oluştur
      if (isFirstMessage) {
        // Geçici ID ve "New Chat" başlığı ile hemen başla
        const tempSessionId = `temp-${Date.now()}`;
        setSessionId(tempSessionId);
        setSessionTitle('New Chat');
        
        try {
          const sessionResponse = await apiClient.createChatSession(text.trim());
          if (sessionResponse.success && sessionResponse.session_id) {
            // Gerçek session ID ve başlığı ile güncelle
            currentActiveSessionId = sessionResponse.session_id;
            setSessionId(sessionResponse.session_id);
            setSessionTitle(sessionResponse.title);
          }
        } catch (sessionError) {
          console.error('Failed to create session:', sessionError);
        }
      }

      if (!currentActiveSessionId || currentActiveSessionId.startsWith('temp-')) {
        throw new Error('Sohbet başlatılamadı.');
      }

      // Mevcut geçmişi al
      const currentHistory = messages.filter(m => m.role === 'user' || m.role === 'assistant')
        .slice(-5)
        .map(m => ({
          role: m.role as 'user' | 'assistant',
          content: m.content
        }));

      // Tek bir endpoint üzerinden her şeyi hallet
      const response = await apiClient.sendMessage(currentActiveSessionId, text.trim(), currentHistory, true);
      
      if (!response.ok) {
        throw new Error('Mesaj gönderilemedi');
      }

      const reader = response.body?.getReader();
      if (!reader) return;

      const decoder = new TextDecoder();
      let buffer = '';
      let sqlText = '';
      let currentFullSql = '';
      let assistantMessageCreated = false;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const content = line.slice(6).trim();
            if (content === '[DONE]') break;
            
            try {
              const data = JSON.parse(content);
              
              if (data.token) {
                sqlText += data.token;
                setMessages((prev) => {
                  const last = prev[prev.length - 1];
                  if (last && last.role === 'assistant' && !assistantMessageCreated) {
                    // Update current assistant message
                    return [...prev.slice(0, -1), {
                      ...last,
                      content: `\`\`\`sql\n${sqlText}\n\`\`\``,
                      sql: sqlText
                    }];
                  } else if (last && last.role === 'user') {
                    assistantMessageCreated = false; 
                    return [...prev, {
                      role: 'assistant',
                      content: `\`\`\`sql\n${sqlText}\n\`\`\``,
                      sql: sqlText,
                      timestamp: new Date()
                    }];
                  }
                  return prev;
                });
              } else if (data.type === 'metadata') {
                const explanation = data.explanation;
                currentFullSql = data.sql || sqlText;
                setMessages((prev) => {
                  const last = prev[prev.length - 1];
                  if (last && last.role === 'assistant') {
                    return [...prev.slice(0, -1), {
                      ...last,
                      content: explanation ? `${explanation}\n\n\`\`\`sql\n${currentFullSql}\n\`\`\`` : `\`\`\`sql\n${currentFullSql}\n\`\`\``,
                      sql: currentFullSql
                    }];
                  }
                  return prev;
                });
              } else if (data.type === 'result') {
                setMessages((prev) => [
                  ...prev,
                  {
                    role: 'assistant',
                    content: 'Sorgu sonuçları:',
                    data: data.data,
                    plotly_json: data.plotly_json,
                    sql: currentFullSql || sqlText,
                    timestamp: new Date(),
                  }
                ]);
              } else if (data.type === 'error') {
                setError(data.error);
                setMessages((prev) => [
                  ...prev,
                  {
                    role: 'assistant',
                    content: `Hata: ${data.error}`,
                    timestamp: new Date(),
                  }
                ]);
              }
            } catch (e) {
              console.error('Error parsing stream data:', e);
            }
          }
        }
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Bilinmeyen hata oluştu';
      setError(errorMessage);
      setMessages((prev) => [...prev, {
        role: 'assistant',
        content: `Hata: ${errorMessage}`,
        timestamp: new Date(),
      }]);
    } finally {
      setIsLoading(false);
    }
  }, [queryApi, isLoading, messages, sessionId]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
    setSessionId(null);
    setSessionTitle(null);
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const loadSession = useCallback(async (loadSessionId: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.getChatSession(loadSessionId);
      
      if (response.success && response.messages) {
        setSessionId(loadSessionId);
        setSessionTitle(response.session.title);
        // Backend'den gelen mesajlarda created_at var, timestamp'e çevir
        const messagesWithTimestamp = response.messages.map((msg: any) => ({
          ...msg,
          timestamp: msg.created_at ? new Date(msg.created_at) : new Date()
        }));
        setMessages(messagesWithTimestamp);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load session';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateSessionTitle = useCallback(async (newTitle: string) => {
    if (!sessionId) return;
    
    try {
      const response = await apiClient.updateChatTitle(sessionId, newTitle);
      if (response.success) {
        setSessionTitle(newTitle);
      }
    } catch (err) {
      console.error('Failed to update title:', err);
    }
  }, [sessionId]);

  return {
    messages,
    isLoading,
    error,
    sessionId,
    sessionTitle,
    sendMessage,
    clearMessages,
    clearError,
    loadSession,
    updateSessionTitle,
  };
}
