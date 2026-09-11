"use client";

import Link from "next/link";
import {
  BellRing,
  CircleAlert,
  UserCheck,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { useAppData } from "@/lib/app-context";
import { AccessDenied, EmptyState } from "@/components/loading-state";

const severityStyles = {
  critical: "bg-rose-50 text-rose-600 border-rose-100",
  high: "bg-amber-50 text-amber-600 border-amber-100",
  medium: "bg-blue-50 text-blue-600 border-blue-100",
  low: "bg-slate-50 text-slate-500 border-slate-100",
};

export default function AlertsPage() {
  const { user } = useAuth();
  const {
    alerts,
    markAlertRead,
  } = useAppData();

  if (!user || user.role !== "admin") return <AccessDenied />;

  const unreadCount = alerts.filter((alert) => !alert.read).length;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2.5">
            <h1 className="page-title">مرکز هشدارها</h1>
            {unreadCount > 0 && (
              <span className="min-w-6 h-6 px-2 inline-flex items-center justify-center rounded-full bg-rose-50 text-rose-700 text-[10px] font-black">
                {unreadCount.toLocaleString("fa-IR")}
              </span>
            )}
          </div>
          <p className="page-description">
            هشدارهای رخداد، تیکت فوری و ارجاع‌های جدید
          </p>
        </div>

      </div>

      <div className="panel overflow-hidden">
        {alerts.length ? (
          <div className="divide-y divide-slate-100">
            {alerts.map((alert) => {
              const content = (
                <>
                  <div
                    className={`w-10 h-10 rounded-2xl border flex items-center justify-center shrink-0 ${severityStyles[alert.severity]}`}
                  >
                    {alert.type === "incident" ? (
                      <CircleAlert className="w-4.5 h-4.5" />
                    ) : (
                      <BellRing className="w-4.5 h-4.5" />
                    )}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <h2 className="text-xs font-black text-slate-800">
                        {alert.title}
                      </h2>
                      {!alert.read && (
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
                      )}
                    </div>
                    <p className="text-[11px] text-slate-500 leading-6 mt-1">
                      {alert.message}
                    </p>
                    <p className="text-[9px] text-slate-400 mt-1.5">
                      {alert.createdAt}
                    </p>
                  </div>
                </>
              );

              return (
                <div
                  key={alert.id}
                  className={`p-5 flex items-start gap-4 ${
                    alert.read ? "bg-white" : "bg-blue-50/[0.18]"
                  }`}
                >
                  {alert.href ? (
                    <Link
                      href={alert.href}
                      onClick={() => void markAlertRead(alert.id, user).catch(() => undefined)}
                      className="flex items-start gap-4 flex-1 min-w-0"
                    >
                      {content}
                    </Link>
                  ) : (
                    <div className="flex items-start gap-4 flex-1 min-w-0">
                      {content}
                    </div>
                  )}
                  <div className="shrink-0 flex flex-col items-end gap-2">
                    {alert.assignedAdminName && (
                      <span className="inline-flex items-center gap-1.5 text-[9px] font-bold text-violet-700 bg-violet-50 border border-violet-100 px-2.5 py-1.5 rounded-lg">
                        <UserCheck className="w-3.5 h-3.5" />
                        مسئول: {alert.assignedAdminName}
                      </span>
                    )}
                    {!alert.read && (
                      <button
                        type="button"
                        onClick={() => void markAlertRead(alert.id, user).catch(() => undefined)}
                        className="text-[9px] font-bold text-blue-600 hover:text-blue-700 cursor-pointer"
                      >
                        علامت‌گذاری به‌عنوان خوانده‌شده
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <EmptyState
            title="هشداری وجود ندارد"
            description="هشدارهای جدید بدون نیاز به بارگذاری دوباره اینجا ظاهر می‌شوند."
          />
        )}
      </div>
    </div>
  );
}
