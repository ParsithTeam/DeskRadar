"use client";

import Link from "next/link";
import {
  BellRing,
  CheckCheck,
  CircleAlert,
  Radio,
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
    markAllAlertsRead,
    emitDemoAlert,
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
            هشدارهای رخداد، SLA، تیکت فوری و ارجاع‌های جدید
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={emitDemoAlert}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-900 text-white text-[10px] font-bold cursor-pointer"
          >
            <Radio className="w-4 h-4" />
            تست هشدار زنده
          </button>
          <button
            type="button"
            onClick={markAllAlertsRead}
            disabled={!unreadCount}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white border border-slate-200 text-slate-600 text-[10px] font-bold disabled:opacity-40 cursor-pointer"
          >
            <CheckCheck className="w-4 h-4" />
            خواندن همه
          </button>
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
                      onClick={() => markAlertRead(alert.id)}
                      className="flex items-start gap-4 flex-1 min-w-0"
                    >
                      {content}
                    </Link>
                  ) : (
                    <div className="flex items-start gap-4 flex-1 min-w-0">
                      {content}
                    </div>
                  )}
                  {!alert.read && (
                    <button
                      type="button"
                      onClick={() => markAlertRead(alert.id)}
                      className="text-[9px] font-bold text-blue-600 hover:text-blue-700 cursor-pointer shrink-0"
                    >
                      خواندم
                    </button>
                  )}
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

