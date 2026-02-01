/**
 * Root Layout
 * Following Single Responsibility Principle - only handles app structure
 */

import type { Metadata } from 'next';
import { AuthProvider } from '@/context/AuthContext';
import { Toaster } from 'react-hot-toast';
import './globals.css';

export const metadata: Metadata = {
  title: 'Vanna AI - SQL Asistanı',
  description: 'Doğal dilden SQL sorguları oluşturun',
  icons: {
    icon: '/vanna.svg',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="tr">
      <body>
        <AuthProvider>
          {children}
          <Toaster position="bottom-right" reverseOrder={false} />
        </AuthProvider>
      </body>
    </html>
  );
}
