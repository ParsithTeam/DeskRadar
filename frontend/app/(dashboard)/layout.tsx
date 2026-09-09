"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { AlertCircle, RefreshCw, X } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { useAppData } from "@/lib/app-context";
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
  const { isReady, dataError, clearDataError, refreshAll } = useAppData();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login");
    }
  }, [user, isLoading, router]);
  
  if (isLoading || !isReady) {
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
          {dataError && (
            <div
              role="alert"
              className="mb-5 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 flex items-start gap-3 text-[11px] text-rose-700"
            >
              <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
              <p className="leading-6 flex-1">{dataError}</p>
              <button
                type="button"
                onClick={() => void refreshAll()}
                className="inline-flex items-center gap-1 font-bold shrink-0 cursor-pointer"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                تلاش دوباره
              </button>
              <button
                type="button"
                onClick={clearDataError}
                aria-label="بستن خطا"
                className="cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          )}
          {children}
        </main>
      </div>
      <LiveAlertToast />
    </div>
  );
}
