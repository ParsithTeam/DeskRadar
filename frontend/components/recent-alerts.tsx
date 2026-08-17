"use client";

import Link from "next/link";
import { useAppData } from "@/lib/app-context";

export default function RecentAlerts() {
  const { alerts } = useAppData();
  const colorMap = {
    critical: "text-rose-600 bg-rose-50",
    high: "text-amber-600 bg-amber-50",
    medium: "text-blue-600 bg-blue-50",
    low: "text-slate-500 bg-slate-100",
  };
  const labelMap = {
    critical: "بحرانی",
    high: "بالا",
    medium: "متوسط",
    low: "اطلاع",
  };

  return (
    <div className="bg-white p-6 rounded-xl border border-slate-200/60 shadow-[0_2px_8px_rgba(0,0,0,0.01)] flex flex-col h-full">
      <div className="mb-4">
        <h3 className="text-sm font-bold text-slate-800">آخرین هشدارهای رادار</h3>
        <p className="text-[11px] text-slate-400 mt-0.5">وقایع زنده زیرساخت هوشمندی</p>
      </div>

      <div className="flex-1 divide-y divide-slate-100 overflow-hidden">
        {alerts.slice(0, 5).map((alert) => (
          <Link
            href={alert.href || "/alerts"}
            key={alert.id}
            className="py-3 flex items-center justify-between gap-3 text-xs last:pb-0 first:pt-0 group"
          >
            <div className="space-y-1 min-w-0 flex-1">
              <p className="text-slate-700 font-medium truncate leading-relaxed group-hover:text-blue-600 transition-colors">
                {alert.message}
              </p>
              <span className="text-[10px] text-slate-400 block">
                {alert.createdAt}
              </span>
            </div>
            <span
              className={`px-2 py-0.5 rounded text-[10px] font-bold whitespace-nowrap ${colorMap[alert.severity]}`}
            >
              {labelMap[alert.severity]}
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}
