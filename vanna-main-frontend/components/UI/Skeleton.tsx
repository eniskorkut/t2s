/**
 * Skeleton Loading Component
 * Provides smooth loading animations for better UX
 */

'use client';

import React from 'react';

export function SkeletonText({ className = '' }: { className?: string }) {
  return (
    <div
      className={`animate-pulse bg-gray-200 rounded ${className}`}
      style={{ height: '1em' }}
    />
  );
}

export function SkeletonBlock({ className = '' }: { className?: string }) {
  return (
    <div className={`animate-pulse bg-gray-200 rounded ${className}`} />
  );
}

export function MessageSkeleton() {
  return (
    <div className="flex gap-6 max-w-4xl mx-auto">
      <div className="w-8 h-8 rounded bg-gray-200 animate-pulse flex-shrink-0" />
      <div className="flex-1 pt-1 space-y-2">
        <SkeletonText className="w-3/4" />
        <SkeletonText className="w-full" />
        <SkeletonText className="w-2/3" />
      </div>
    </div>
  );
}

export function TableSkeleton() {
  return (
    <div className="mt-3 space-y-2">
      <SkeletonBlock className="h-10 w-full" />
      {[...Array(5)].map((_, i) => (
        <SkeletonBlock key={i} className="h-12 w-full" />
      ))}
    </div>
  );
}
