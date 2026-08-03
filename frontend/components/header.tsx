"use client";

import Image from "next/image";
import Link from "next/link";
import { Bell, LifeBuoy, LogOut, Phone, UserRound } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { useAppData } from "@/lib/app-context";

export default function Header() {
  const { user, logout } = useAuth();
  const { alerts } = useAppData();
  const unreadCount = alerts.filter((alert) => !alert.read).length;

  return (
    <header className="h-[72px] bg-white border-b border-slate-200 flex items-center shadow-[0_1px_3px_rgba(0,0,0,0.02)] sticky top-0 z-30">
      <div className="w-auto lg:w-64 h-full flex items-center gap-3 px-4 lg:px-8 lg:border-l border-slate-200">
        <Image
          src="/deskino-logo.svg"
          alt="لوگو دسکینو"
          width={136}
          height={36}
          priority
          className="object-contain"
        />
      </div>

      <div className="flex-1 h-full px-4 sm:px-6 flex items-center justify-end gap-3 sm:gap-5">
        <div className="hidden md:flex items-center gap-5 text-xs text-slate-500">
          <button className="flex items-center gap-1.5 hover:text-slate-800 transition-colors cursor-pointer">
            <LifeBuoy className="w-4 h-4" />
            راهنما
          </button>
          <button className="flex items-center gap-1.5 hover:text-slate-800 transition-colors cursor-pointer">
            <Phone className="w-4 h-4" />
            پشتیبانی تلفنی
          </button>
        </div>

        {user?.role === "admin" && (
          <Link
            href="/alerts"
            aria-label="هشدارها"
            className="relative w-9 h-9 rounded-xl border border-slate-200 flex items-center justify-center text-slate-500 hover:bg-slate-50 transition-colors"
          >
            <Bell className="w-4 h-4" />
            {unreadCount > 0 && (
              <span className="absolute -top-1 -left-1 min-w-4 h-4 px-1 rounded-full bg-rose-500 text-white text-[8px] font-bold flex items-center justify-center">
                {unreadCount.toLocaleString("fa-IR")}
              </span>
            )}
          </Link>
        )}

        <div className="w-px h-6 bg-slate-200 hidden sm:block" />

        <div className="flex items-center gap-2.5">
          <div className="hidden sm:block text-left">
            <span className="text-xs font-bold text-slate-700 block">
              {user?.name || "کاربر سیستم"}
            </span>
            <span className="text-[9px] text-slate-400">
              {user?.role === "admin" ? "مدیر پشتیبانی" : "کاربر سازمان"}
            </span>
          </div>

          <div className="w-9 h-9 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-center">
            <UserRound className="text-slate-500 w-4 h-4" />
          </div>

          <button
            type="button"
            onClick={logout}
            aria-label="خروج از حساب"
            className="lg:hidden w-9 h-9 rounded-xl text-rose-500 hover:bg-rose-50 flex items-center justify-center cursor-pointer"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
}
