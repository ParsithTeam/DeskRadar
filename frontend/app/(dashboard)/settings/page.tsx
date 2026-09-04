"use client";

import { RotateCcw } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { useAppData } from "@/lib/app-context";
import { AccessDenied } from "@/components/loading-state";

export default function SettingsPage() {
  const { user } = useAuth();
  const { resetDemoData } = useAppData();

  if (!user || user.role !== "admin") return <AccessDenied />;

  return (
    <div className="max-w-3xl space-y-6">
      <div className="space-y-1.5">
        <h1 className="page-title">تنظیمات</h1>
        <p className="page-description">
          مدیریت داده‌های نسخه نمایشی فرانت‌اند
        </p>
      </div>

      <section className="panel p-5 sm:p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-sm font-black text-slate-800">
            بازنشانی داده‌های نمایشی
          </h2>
          <p className="text-[10px] text-slate-400 mt-1 leading-5">
            تمام تغییرات محلی، گفتگوها و تیکت‌های ساخته‌شده به داده اولیه
            برمی‌گردند.
          </p>
        </div>
        <button
          type="button"
          onClick={resetDemoData}
          className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-rose-50 text-rose-700 border border-rose-100 text-[10px] font-bold cursor-pointer shrink-0"
        >
          <RotateCcw className="w-4 h-4" />
          بازنشانی داده‌ها
        </button>
      </section>
    </div>
  );
}
