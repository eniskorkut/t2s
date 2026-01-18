/**
 * Header component
 * Following Single Responsibility Principle - only handles header UI
 */
'use client';

import React, { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { LoginModal } from '@/components/Auth/LoginModal';
import { RegisterModal } from '@/components/Auth/RegisterModal';
import { ResetPasswordModal } from '@/components/Auth/ResetPasswordModal';
import { Button } from '@/components/UI/Button';

export default function Header() {
  const { user } = useAuth();
  const [showLogin, setShowLogin] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  const [showResetPassword, setShowResetPassword] = useState(false);

  return (
    <>
      {!user && (
        <header className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-gray-300">
          <div className="h-14 flex items-center pr-4 justify-end gap-3">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setShowLogin(true)}
            >
              Oturum aç
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={() => setShowRegister(true)}
            >
              Ücretsiz kaydol
            </Button>
          </div>
        </header>
      )}
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
        asModal={false}
      />
      <RegisterModal
        isOpen={showRegister}
        onClose={() => setShowRegister(false)}
        onSwitchToLogin={() => {
          setShowRegister(false);
          setShowLogin(true);
        }}
        asModal={false}
      />
      <ResetPasswordModal
        isOpen={showResetPassword}
        onClose={() => setShowResetPassword(false)}
        onSwitchToLogin={() => {
          setShowResetPassword(false);
          setShowLogin(true);
        }}
        asModal={false}
      />
    </>
  );
}
