"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import Sidebar from "@/components/sidebar";
import Header from "@/components/header";
import LiveAlertToast from "@/components/live-alert-toast";
import LoadingSkeleton from "@/components/loading-state";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login");
    }
  }, [user, isLoading, router]);
  
  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#f8fafc] p-8">
        <LoadingSkeleton />
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="flex flex-col min-h-screen bg-[#f8fafc]">
      <Header />

      <div className="flex flex-col lg:flex-row flex-1">
        <Sidebar />
        <main className="flex-1 min-w-0 p-4 sm:p-6 lg:p-8 overflow-y-auto">
          {children}
        </main>
      </div>
      <LiveAlertToast />
    </div>
  );
}
