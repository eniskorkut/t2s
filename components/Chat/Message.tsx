/**
 * Message component with CSV export and Chart/Table toggle
 * Following Single Responsibility Principle - only handles message rendering
 * Following Open/Closed Principle - extensible via props
 */

'use client';

import React, { useState, useMemo } from 'react';
import type { Message as MessageType } from '@/lib/types';
import { Button } from '@/components/UI/Button';
import { downloadCSV } from '@/lib/utils/csvExport';
import { MessageSkeleton } from '@/components/UI/Skeleton';
import { useTypewriter } from '@/hooks/useTypewriter';
import dynamic from 'next/dynamic';

// SVG Icons
function ChartIcon({ className = '' }: { className?: string }) {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <line x1="18" y1="20" x2="18" y2="10"></line>
      <line x1="12" y1="20" x2="12" y2="4"></line>
      <line x1="6" y1="20" x2="6" y2="14"></line>
    </svg>
  );
}

function TableIcon({ className = '' }: { className?: string }) {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M9 3H5a2 2 0 0 0-2 2v4m6-6h10a2 2 0 0 1 2 2v4M9 3v18m0 0h10a2 2 0 0 0 2-2V9M9 21H5a2 2 0 0 1-2-2V9m0 0h18"></path>
    </svg>
  );
}

// Dynamic import for Plotly to reduce bundle size
const Plot = dynamic(() => import('react-plotly.js'), {
  ssr: false,
  loading: () => (
    <div className="mt-3 bg-white border border-gray-300 rounded-lg p-4">
      <div className="animate-pulse bg-gray-200 rounded h-96" />
    </div>
  ),
});

export interface MessageProps {
  message: MessageType;
  userQuestion?: string;
  onSaveQuery?: (question: string, sql: string, isCorrect: boolean) => void;
  onSuggestionClick?: (suggestion: string) => void;
}

type ViewMode = 'table' | 'chart';

export default function Message({ message, userQuestion, onSaveQuery, onSuggestionClick }: MessageProps) {
  // Typewriter effect sadece yeni mesajlar için (3 saniyeden eski mesajlarda animasyon yok)
  const isNewMessage = useMemo(() => {
    if (!message.timestamp) return true; // Timestamp yoksa yeni kabul et
    const messageTime = message.timestamp instanceof Date 
      ? message.timestamp.getTime() 
      : new Date(message.timestamp).getTime();
    const now = Date.now();
    const ageInSeconds = (now - messageTime) / 1000;
    return ageInSeconds < 3; // 3 saniyeden yeni ise animasyon göster
  }, [message.timestamp]);

  const { displayText, isTyping } = useTypewriter({
    text: message.content,
    speed: 30, // 30ms per character
    enabled: message.role === 'assistant' && isNewMessage, // Sadece yeni AI mesajları için
  });

  // State for chart/table toggle
  const [viewMode, setViewMode] = useState<ViewMode>(() => {
    // Default to chart if plotly_json exists, otherwise table
    return message.plotly_json ? 'chart' : 'table';
  });

  const handleSave = (isCorrect: boolean) => {
    if (message.sql && onSaveQuery && userQuestion) {
      onSaveQuery(userQuestion, message.sql, isCorrect);
    }
  };

  const handleDownloadCSV = () => {
    if (message.data && message.data.length > 0) {
      const timestamp = new Date().toISOString().split('T')[0];
      downloadCSV(message.data, `sorgu-sonucu-${timestamp}.csv`);
    }
  };

  const formatContent = (content: string): React.ReactNode => {
    // Simple markdown-like formatting
    const parts = content.split(/(```[\s\S]*?```|`[^`]+`)/g);
    
    return parts.map((part, index) => {
      if (part.startsWith('```sql')) {
        const code = part.replace(/```sql\n?/g, '').replace(/```/g, '').trim();
        return (
          <pre key={index} className="bg-gray-100 border border-gray-300 p-3 rounded my-2 overflow-x-auto">
            <code className="text-sm text-black">{code}</code>
          </pre>
        );
      }
      if (part.startsWith('```')) {
        const code = part.replace(/```/g, '').trim();
        return (
          <pre key={index} className="bg-gray-100 border border-gray-300 p-3 rounded my-2 overflow-x-auto">
            <code className="text-sm text-black">{code}</code>
          </pre>
        );
      }
      if (part.startsWith('`') && part.endsWith('`')) {
        const code = part.slice(1, -1);
        return (
          <code key={index} className="bg-gray-100 border border-gray-300 px-1.5 py-0.5 rounded text-sm text-black">
            {code}
          </code>
        );
      }
      return <span key={index}>{part}</span>;
    });
  };

  const hasData = message.data && message.data.length > 0;
  const hasChart = message.plotly_json;
  const showToggle = hasData && hasChart;

  return (
    <div
      className={`flex gap-6 max-w-4xl mx-auto ${
        message.role === 'user' ? 'bg-white' : 'bg-gray-50'
      }`}
    >
      <div
        className={`w-8 h-8 rounded flex items-center justify-center font-semibold flex-shrink-0 ${
          message.role === 'user'
            ? 'bg-black text-white'
            : 'bg-gray-800 text-white'
        }`}
      >
        {message.role === 'user' ? 'U' : 'AI'}
      </div>
      <div className="flex-1 pt-1">
        <div className="whitespace-pre-wrap break-words text-black">
          {formatContent(displayText)}
          {isTyping && <span className="inline-block w-0.5 h-5 bg-black animate-pulse ml-0.5 align-middle"></span>}
        </div>
        
        {/* Önerileri göster - Sadece typewriter tamamlandıktan sonra */}
        {!isTyping && message.suggestions && message.suggestions.length > 0 && onSuggestionClick && (
          <div className="mt-4 space-y-2">
            <p className="text-sm font-medium text-gray-700 mb-2">Öneriler:</p>
            <div className="flex flex-wrap gap-2">
              {message.suggestions.map((suggestion, idx) => (
                <button
                  key={idx}
                  onClick={() => onSuggestionClick(suggestion)}
                  className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm text-black hover:bg-gray-50 hover:border-gray-400 transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}
        
        {/* Data Toolbar - Toggle and Download buttons - Sadece typewriter tamamlandıktan sonra */}
        {!isTyping && hasData && (
          <div className="mt-3 mb-2 flex items-center justify-between bg-gray-100 p-2 rounded-lg border border-gray-300">
            {/* Left side - View toggle */}
            {showToggle && (
              <div className="flex items-center gap-1 bg-white rounded-md p-1 border border-gray-300">
                <button
                  onClick={() => setViewMode('chart')}
                  className={`px-3 py-1.5 text-sm font-medium rounded transition-colors flex items-center gap-1.5 ${
                    viewMode === 'chart'
                      ? 'bg-blue-500 text-white'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <ChartIcon />
                  <span>Grafik</span>
                </button>
                <button
                  onClick={() => setViewMode('table')}
                  className={`px-3 py-1.5 text-sm font-medium rounded transition-colors flex items-center gap-1.5 ${
                    viewMode === 'table'
                      ? 'bg-blue-500 text-white'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <TableIcon />
                  <span>Tablo</span>
                </button>
              </div>
            )}
            
            {!showToggle && <div />}
            
            {/* Right side - Download button */}
            <button
              onClick={handleDownloadCSV}
              className="flex items-center gap-2 px-3 py-1.5 bg-green-500 text-white text-sm font-medium rounded hover:bg-green-600 transition-colors"
              title="CSV olarak indir"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              CSV İndir
            </button>
          </div>
        )}
        
        {/* Chart View - Sadece typewriter tamamlandıktan sonra */}
        {!isTyping && hasChart && viewMode === 'chart' && (
          <div className="mt-3 bg-white border border-gray-300 rounded-lg p-4">
            <Plot
              data={message.plotly_json.data}
              layout={{
                ...message.plotly_json.layout,
                autosize: true,
              }}
              config={{
                responsive: true,
                displayModeBar: 'hover',
                displaylogo: false,
                modeBarButtonsToRemove: ['lasso2d', 'select2d'],
              }}
              style={{ width: '100%', height: '450px' }}
              useResizeHandler={true}
            />
          </div>
        )}
        
        {/* Table View - Sadece typewriter tamamlandıktan sonra */}
        {!isTyping && hasData && message.data && (!hasChart || viewMode === 'table') && (
          <div className="mt-3 overflow-x-auto">
            <table className="w-full border-collapse bg-white border border-gray-300 rounded overflow-hidden">
              <thead>
                <tr>
                  {Object.keys(message.data[0]).map((key) => (
                    <th
                      key={key}
                      className="p-3 text-left bg-gray-100 font-semibold border-b border-gray-300 text-black"
                    >
                      {key}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {message.data.map((row, idx) => (
                  <tr key={idx} className="border-b border-gray-200 hover:bg-gray-50">
                    {Object.values(row).map((val: unknown, i) => (
                      <td key={i} className="p-3 text-black">
                        {String(val ?? '')}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Boş veri uyarısı - SQL var ama data boşsa */}
        {!isTyping && message.sql && message.data && message.data.length === 0 && (
          <div className="mt-3 p-4 bg-yellow-50 border border-yellow-200 rounded-lg flex items-center gap-3 text-yellow-800">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <span className="text-sm font-medium">Yapmak istediğiniz sorguya ait hiçbir veri bulunamadı.</span>
          </div>
        )}
        
        {/* Save Query buttons - Sadece typewriter tamamlandıktan sonra */}
        {!isTyping && message.data && message.sql && onSaveQuery && userQuestion && (
          <div className="mt-4 flex gap-2">
            <Button
              variant="primary"
              size="sm"
              onClick={() => handleSave(true)}
            >
              Evet, eğitime ekle
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => handleSave(false)}
            >
              Hayır
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
