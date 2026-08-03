"use client";

import type { LucideIcon } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: number | string;
  valueColor: string;
  description?: string;
  icon?: LucideIcon;
}

export default function MetricCard({
  title,
  value,
  valueColor,
  description,
  icon: Icon,
}: MetricCardProps) {
  return (
    <div className="bg-white px-5 py-5 rounded-xl border border-slate-200/60 shadow-[0_2px_8px_rgba(0,0,0,0.02)] flex items-center justify-between gap-4 transition-all hover:border-slate-300">
      <div className="min-w-0">
        <span className="text-xs font-bold text-slate-600 block">{title}</span>
        {description && (
          <span className="text-[10px] text-slate-400 mt-1 block truncate">
            {description}
          </span>
        )}
      </div>
      <div className="flex items-center gap-2.5 shrink-0">
        {Icon && (
          <div className="w-8 h-8 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-center text-slate-400">
            <Icon className="w-4 h-4" strokeWidth={1.8} />
          </div>
        )}
        <h3 className={`text-2xl font-black ${valueColor} tracking-tight`}>
          {value}
        </h3>
      </div>
    </div>
  );
}
