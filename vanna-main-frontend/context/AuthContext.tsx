"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useRouter } from "next/navigation";

interface User {
  id?: number;
  email: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (token: string, role: string, email: string) => void;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Check localStorage on mount
    const storedToken = localStorage.getItem("token");
    const storedRole = localStorage.getItem("role");
    const storedEmail = localStorage.getItem("email");

    if (storedToken && storedRole) {
      setToken(storedToken);
      setUser({ email: storedEmail || "", role: storedRole });
    }
    setIsLoading(false);
  }, []);

  const login = (newToken: string, role: string, email: string) => {
    localStorage.setItem("token", newToken);
    localStorage.setItem("role", role);
    localStorage.setItem("email", email);

    setToken(newToken);
    setUser({ email, role });

    // Refresh to apply auth state deeply or redirect
    router.push("/");
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    localStorage.removeItem("email");
    setToken(null);
    setUser(null);
    router.push("/login");
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
