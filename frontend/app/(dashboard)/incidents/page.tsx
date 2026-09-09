"use client";

import Link from "next/link";
import { Radar, Search } from "lucide-react";
import { useMemo, useState } from "react";
import { useAppData } from "@/lib/app-context";
import { useAuth } from "@/lib/auth-context";
import { AccessDenied, EmptyState } from "@/components/loading-state";
import UrgencyBadge, {
  IncidentStatusBadge,
} from "@/components/status-badge";
import type { IncidentStatus } from "@/types";

export default function IncidentsPage() {
  const { user } = useAuth();
  const { incidents } = useAppData();
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<IncidentStatus | "all">("all");

  const filtered = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return incidents.filter(
      (incident) =>
        (status === "all" || incident.status === status) &&
        (!normalized ||
          incident.title.toLowerCase().includes(normalized) ||
          incident.description.toLowerCase().includes(normalized)),
    );
  }, [incidents, query, status]);

  if (!user || user.role !== "admin") return <AccessDenied />;

  return (
    <div className="space-y-6">
      <div className="space-y-1.5">
        <h1 className="page-title">رادار رخدادها</h1>
        <p className="page-description">
          خوشه‌های تیکت مشابه که می‌توانند نشانه یک اختلال گسترده باشند
        </p>
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative w-full sm:w-80">
          <Search className="absolute inset-y-0 my-auto right-3 w-3.5 h-3.5 text-slate-400" />
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="جستجو در رخدادها..."
            className="w-full pr-9 pl-3 py-2.5 border border-slate-200 rounded-xl bg-white text-xs focus:outline-none focus:border-slate-400"
          />
        </div>
        <select
          value={status}
          onChange={(event) =>
            setStatus(event.target.value as IncidentStatus | "all")
          }
          className="bg-white border border-slate-200 rounded-xl px-3 py-2.5 text-[10px] font-bold text-slate-600 focus:outline-none"
        >
          <option value="all">همه وضعیت‌ها</option>
          <option value="candidate">نیازمند تأیید</option>
          <option value="confirmed">تأیید شده</option>
          <option value="resolved">رفع شده</option>
          <option value="dismissed">رد شده</option>
        </select>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        {filtered.map((incident) => (
          <Link
            href={`/incidents/${incident.id}`}
            key={incident.id}
            className="panel p-5 sm:p-6 hover:border-slate-300 transition-colors group"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-start gap-3 min-w-0">
                <div className="w-10 h-10 rounded-2xl bg-rose-50 text-rose-600 flex items-center justify-center shrink-0">
                  <Radar className="w-4.5 h-4.5" />
                </div>
                <div className="min-w-0">
                  <h2 className="text-xs font-black text-slate-800 group-hover:text-blue-600 transition-colors">
                    {incident.title}
                  </h2>
                  <p className="text-[10px] text-slate-400 mt-1.5">
                    #{incident.id.toLocaleString("fa-IR")} ·{" "}
                    {incident.createdAt}
                  </p>
                </div>
              </div>
              <IncidentStatusBadge status={incident.status} />
            </div>

            <p className="text-[11px] text-slate-500 leading-6 mt-4 line-clamp-2">
              {incident.description}
            </p>

            <div className="mt-5 pt-4 border-t border-slate-100 flex items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <UrgencyBadge level={incident.severity} />
                <span className="text-[10px] text-slate-400">
                  {incident.tickets.length.toLocaleString("fa-IR")} تیکت مرتبط
                </span>
              </div>
              {incident.category !== "unknown" && (
                <span className="text-[10px] font-bold text-slate-500">
                  {incident.categoryLabelFa}
                </span>
              )}
            </div>
          </Link>
        ))}
      </div>

      {!filtered.length && (
        <div className="panel">
          <EmptyState
            title="رخدادی پیدا نشد"
            description="فیلتر وضعیت یا عبارت جستجو را تغییر دهید."
          />
        </div>
      )}
    </div>
  );
}
