"use client";

import { useAppData } from "@/lib/app-context";
import { categoryLabels } from "@/lib/ticket-categories";
import type { TicketCategory } from "@/types";

export default function CategoryChart() {
  const { tickets } = useAppData();
  const categories: { key: TicketCategory; color: string }[] = [
    { key: "vpn", color: "bg-blue-500" },
    { key: "email", color: "bg-amber-500" },
    { key: "network", color: "bg-rose-500" },
    { key: "printer", color: "bg-slate-400" },
    { key: "account", color: "bg-emerald-500" },
    { key: "permission", color: "bg-violet-500" },
    { key: "software", color: "bg-cyan-500" },
    { key: "hardware", color: "bg-orange-500" },
    { key: "unknown", color: "bg-slate-300" },
  ];
  const chartData = categories.map((item) => ({
    category: categoryLabels[item.key],
    count: tickets.filter((ticket) => ticket.category === item.key).length,
    color: item.color,
  }));
  const largest = Math.max(...chartData.map((item) => item.count), 1);

  return (
    <div className="bg-white p-6 rounded-xl border border-slate-200/60 shadow-[0_2px_8px_rgba(0,0,0,0.01)] flex flex-col justify-between h-full">
      <div className="mb-4">
        <h3 className="text-sm font-bold text-slate-800">تفکیک موضوعی تیکت‌ها (AI Cat)</h3>
        <p className="text-[11px] text-slate-400 mt-0.5">میزان تکرار تیکت‌های فارسی در دپارتمان‌ها</p>
      </div>

      <div className="space-y-4 flex-1 flex flex-col justify-center">
        {chartData.map((item, idx) => (
          <div key={idx} className="space-y-1.5">
            <div className="flex justify-between items-center text-xs">
              <span className="font-medium text-slate-600">{item.category}</span>
              <span className="font-bold text-slate-800">{item.count} تیکت</span>
            </div>
            <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full ${item.color} transition-all duration-500`}
                style={{ width: `${Math.max((item.count / largest) * 100, 4)}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
