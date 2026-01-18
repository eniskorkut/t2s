/**
 * Queries List component
 * Following Single Responsibility Principle - only handles queries list display
 * Following Dependency Inversion Principle - depends on useQueries hook
 */

'use client';

import React from 'react';
import { useQueries } from '@/hooks/useQueries';
import { Button } from '@/components/UI/Button';

export default function QueriesList() {
  const { queries, isLoading, error, loadQueries, deleteQuery } = useQueries({
    autoLoad: true,
  });

  const handleDelete = async (id: number) => {
    if (confirm('Bu sorguyu silmek istediğinize emin misiniz?')) {
      try {
        await deleteQuery(id);
      } catch (err) {
        alert('Sorgu silinirken hata oluştu');
      }
    }
  };

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block w-8 h-8 border-4 border-gray-300 border-t-[#10a37f] rounded-full animate-spin" />
        <p className="mt-4 text-gray-500">Yükleniyor...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500 mb-4">{error}</p>
        <Button variant="primary" onClick={loadQueries}>
          Tekrar Dene
        </Button>
      </div>
    );
  }

  if (queries.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Henüz kaydedilmiş sorgu yok</p>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6 text-black">Kaydettiğim Sorgular</h2>
      <div className="space-y-3">
        {queries.map((query) => (
          <div
            key={query.id}
            className="bg-gray-50 p-4 rounded-lg border border-gray-300"
          >
            <div className="mb-2 font-semibold text-black">{query.question}</div>
            <pre className="bg-gray-100 p-2 rounded text-xs overflow-x-auto mb-2 text-black">
              {query.sql_query}
            </pre>
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-500">
                {new Date(query.saved_at).toLocaleString('tr-TR')}
              </span>
              <div className="flex items-center gap-2">
                {query.is_trained && (
                  <span className="bg-[#10a37f] px-2 py-1 rounded text-xs text-white">
                    Eğitime Eklendi
                  </span>
                )}
                <Button
                  variant="danger"
                  size="sm"
                  onClick={() => handleDelete(query.id)}
                >
                  Sil
                </Button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
