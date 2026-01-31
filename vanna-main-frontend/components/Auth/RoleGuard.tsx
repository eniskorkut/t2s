"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

interface RoleGuardProps {
    children: React.ReactNode;
    allowedRoles: string[];
}

export const RoleGuard = ({ children, allowedRoles }: RoleGuardProps) => {
    const { user, isLoading } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!isLoading && !user) {
            router.push("/login");
        } else if (!isLoading && user && !allowedRoles.includes(user.role)) {
            router.push("/"); // Redirect to home if authorized but wrong role
        }
    }, [user, isLoading, router, allowedRoles]);

    if (isLoading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
            </div>
        );
    }

    if (!user || !allowedRoles.includes(user.role)) {
        return null; // Don't render anything while redirecting
    }

    return <>{children}</>;
};
