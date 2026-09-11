"use client";

import Link from "next/link";
import { Plus, Search } from "lucide-react";
import { useMemo, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { useAppData } from "@/lib/app-context";
import { AccessDenied, EmptyState } from "@/components/loading-state";
import {
  AnalysisStatusBadge,
  TicketStatusBadge,
} from "@/components/status-badge";

export default function MyTicketsPage() {
  const { user } = useAuth();
  const { tickets } = useAppData();
  const [query, setQuery] = useState("");

  const myTickets = useMemo(() => {
    if (!user) return [];
    const normalized = query.trim().toLowerCase();
    return tickets.filter(
      (ticket) =>
        ticket.requesterId === user.id &&
        (!normalized ||
          ticket.title.toLowerCase().includes(normalized) ||
          ticket.description.toLowerCase().includes(normalized)),
    );
  }, [query, tickets, user]);

  if (!user || user.role !== "user") return <AccessDenied />;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div className="space-y-1.5">
          <h1 className="page-title">تیکت‌های من</h1>
          <p className="page-description">
            نتیجه تحلیل، پاسخ AI و وضعیت پیگیری درخواست‌ها
          </p>
        </div>
        <Link
          href="/my-tickets/new"
          className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-slate-900 text-white text-[11px] font-bold hover:bg-slate-800 transition-colors"
        >
          <Plus className="w-4 h-4" />
          ثبت تیکت جدید
        </Link>
      </div>

      <div className="relative w-full sm:w-80">
        <Search className="absolute inset-y-0 my-auto right-3 w-3.5 h-3.5 text-slate-400" />
        <input
          type="search"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="جستجو در تیکت‌های من..."
          className="w-full pr-9 pl-3 py-2.5 border border-slate-200 rounded-xl bg-white text-xs focus:outline-none focus:border-slate-400"
        />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        {myTickets.map((ticket) => (
          <Link
            href={`/my-tickets/${ticket.id}`}
            key={ticket.id}
            className="panel p-5 hover:border-slate-300 transition-colors group"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="min-w-0">
                <p className="text-xs font-black text-slate-800 group-hover:text-blue-600 transition-colors truncate">
                  {ticket.title}
                </p>
                <p className="text-[10px] text-slate-400 mt-1.5">
                  #{ticket.id.toLocaleString("fa-IR")} · {ticket.createdAt}
                </p>
              </div>
              <TicketStatusBadge status={ticket.status} />
            </div>
            <p className="text-[11px] text-slate-500 leading-6 mt-4 line-clamp-2">
              {ticket.description}
            </p>
            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
              <AnalysisStatusBadge status={ticket.analysisStatus} />
              <span className="text-[10px] font-bold text-slate-400">
                {ticket.analysisStatus === "complete" && ticket.confidence > 0
                  ? `${(ticket.confidence * 100).toLocaleString("fa-IR")}٪ اطمینان`
                  : ticket.analysisStatus === "complete"
                    ? "تحلیل آماده است"
                  : ticket.analysisStatus === "pending"
                    ? "در حال پردازش"
                    : ticket.analysisStatus === "failed"
                      ? "تحلیل ناموفق"
                      : "منتظر شروع تحلیل"}
              </span>
            </div>
          </Link>
        ))}
      </div>

      {!myTickets.length && (
        <div className="panel">
          <EmptyState
            title={query ? "نتیجه‌ای پیدا نشد" : "هنوز تیکتی ثبت نکرده‌اید"}
            description={
              query
                ? "عبارت جستجو را تغییر دهید."
                : "اولین درخواست خود را ثبت کنید تا Radar آن را تحلیل کند."
            }
            action={
              !query ? (
                <Link
                  href="/my-tickets/new"
                  className="inline-flex px-4 py-2.5 rounded-xl bg-slate-900 text-white text-[11px] font-bold"
                >
                  ثبت اولین تیکت
                </Link>
              ) : undefined
            }
          />
        </div>
      )}
    </div>
  );
}
