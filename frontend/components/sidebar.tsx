"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import {
  Bell,
  BookOpen,
  CircleGauge,
  Headphones,
  Inbox,
  LogOut,
  PlusCircle,
  Radar,
  TicketCheck,
  Tickets,
} from "lucide-react";
import { useAppData } from "@/lib/app-context";
import type { LucideIcon } from "lucide-react";

interface MenuItem {
  name: string;
  href: string;
  roles: ("admin" | "user")[];
  icon: LucideIcon;
  badge?: number;
}

export default function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const { escalations, alerts } = useAppData();

  if (!user) return null;

  const menuItems: MenuItem[] = [
    {
      name: "خلاصه گزارشات",
      href: "/",
      roles: ["admin", "user"],
      icon: CircleGauge,
    },
    {
      name: "صندوق تیکت‌ها",
      href: "/tickets",
      roles: ["admin"],
      icon: Inbox,
    },
    {
      name: "اینباکس ارجاعات",
      href: "/admin/escalated",
      roles: ["admin"],
      icon: Headphones,
      badge: escalations.filter((item) => item.status === "waiting").length,
    },
    {
      name: "رادار رخدادها",
      href: "/incidents",
      roles: ["admin"],
      icon: Radar,
    },
    {
      name: "تیکت‌های من",
      href: "/my-tickets",
      roles: ["user"],
      icon: TicketCheck,
    },
    {
      name: "ثبت تیکت جدید",
      href: "/my-tickets/new",
      roles: ["user"],
      icon: PlusCircle,
    },
    {
      name: "پایگاه دانش",
      href: "/knowledge-base",
      roles: ["admin", "user"],
      icon: BookOpen,
    },
    {
      name: "هشدارها",
      href: "/alerts",
      roles: ["admin"],
      icon: Bell,
      badge: alerts.filter((alert) => !alert.read).length,
    },
  ];

  const allowedItems = menuItems.filter((item) => item.roles.includes(user.role));

  return (
    <aside className="w-full lg:w-64 bg-white border-b lg:border-b-0 lg:border-l border-slate-200 p-3 lg:p-4 flex lg:flex-col justify-between shadow-[1px_0_0_0_#e2e8f0] lg:min-h-[calc(100vh-72px)]">
      <nav className="flex lg:block gap-1 lg:space-y-1 overflow-x-auto w-full">
        {allowedItems.map((item) => {
          const isActive =
            pathname === item.href ||
            (item.href !== "/" && pathname.startsWith(`${item.href}/`));
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex shrink-0 items-center gap-2.5 px-3.5 py-2.5 rounded-xl text-xs transition-all duration-150 ${
                isActive 
                  ? "bg-slate-100 text-slate-900 font-bold" 
                  : "text-slate-500 hover:bg-slate-50 hover:text-slate-800"
              }`}
            >
              <Icon className="w-4 h-4" strokeWidth={1.8} />
              <span>{item.name}</span>
              {!!item.badge && (
                <span className="mr-auto min-w-5 h-5 px-1.5 inline-flex items-center justify-center rounded-full bg-slate-900 text-white text-[9px] font-bold">
                  {item.badge.toLocaleString("fa-IR")}
                </span>
              )}
            </Link>
          );
        })}
      </nav>
      
      <div className="hidden lg:block border-t border-slate-100 pt-3 space-y-2">
        <button 
          onClick={logout}
          className="w-full flex items-center gap-2.5 text-right px-3.5 py-2 text-xs font-semibold text-rose-500 hover:bg-rose-50 rounded-xl transition-colors cursor-pointer"
        >
          <LogOut className="w-4 h-4" />
          خروج از حساب
        </button>
        <div className="px-3.5 text-[10px] text-slate-400 font-medium flex items-center gap-2">
          <Tickets className="w-3.5 h-3.5" />
          نقش: {user.role === "admin" ? "مدیر پشتیبانی" : "کاربر سازمان"}
        </div>
      </div>
    </aside>
  );
}
