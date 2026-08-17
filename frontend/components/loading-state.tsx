"use client";

import { Inbox } from "lucide-react";

export default function LoadingSkeleton() {
  return (
    <div className="space-y-8 animate-pulse">
      <div className="space-y-2">
        <div className="h-6 bg-slate-200 rounded-md w-48"></div>
        <div className="h-4 bg-slate-150 rounded-md w-72"></div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white px-6 py-6 rounded-xl border border-slate-100 h-24 flex items-center justify-between">
            <div className="h-4 bg-slate-200 rounded w-24"></div>
            <div className="h-6 bg-slate-200 rounded w-12"></div>
          </div>
        ))}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white p-6 rounded-xl border border-slate-100 h-80"></div>
        <div className="bg-white p-6 rounded-xl border border-slate-100 h-80"></div>
      </div>
    </div>
  );
}

export function EmptyState({
  title = "موردی برای نمایش وجود ندارد",
  description = "با تغییر فیلترها یا ثبت داده جدید دوباره بررسی کنید.",
  action,
}: {
  title?: string;
  description?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="py-16 px-6 flex flex-col items-center text-center">
      <div className="w-11 h-11 rounded-2xl bg-slate-50 border border-slate-100 flex items-center justify-center text-slate-400 mb-4">
        <Inbox className="w-5 h-5" />
      </div>
      <p className="text-sm font-bold text-slate-800">{title}</p>
      <p className="text-xs text-slate-400 mt-1.5 max-w-sm leading-6">
        {description}
      </p>
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}

export function AccessDenied() {
  return (
    <EmptyState
      title="دسترسی به این بخش محدود است"
      description="این صفحه فقط برای نقش تعیین‌شده در سامانه قابل مشاهده است."
    />
  );
}
