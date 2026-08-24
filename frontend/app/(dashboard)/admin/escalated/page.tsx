"use client";

import Link from "next/link";
import { Headphones, Search } from "lucide-react";
import { useMemo, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { useAppData } from "@/lib/app-context";
import { AccessDenied, EmptyState } from "@/components/loading-state";
import { EscalationStatusBadge } from "@/components/status-badge";
import type { EscalationStatus } from "@/types";

export default function EscalationsInboxPage() {
  const { user } = useAuth();
  const { escalations, tickets } = useAppData();
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<EscalationStatus | "all">("all");

  const filteredEscalations = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return escalations.filter((item) => {
      const ticket = tickets.find((current) => current.id === item.ticketId);
      const matchesStatus = status === "all" || item.status === status;
      const matchesQuery =
        !normalized ||
        item.requesterName.toLowerCase().includes(normalized) ||
        ticket?.title.toLowerCase().includes(normalized) ||
        item.reason.toLowerCase().includes(normalized);
      return matchesStatus && matchesQuery;
    });
  }, [escalations, query, status, tickets]);

  if (!user || user.role !== "admin") return <AccessDenied />;

  return (
    <div className="space-y-6">
      <div className="space-y-1.5">
        <div className="flex items-center gap-2.5">
          <h1 className="page-title">اینباکس ارجاعات انسانی</h1>
          <span className="min-w-6 h-6 px-2 inline-flex items-center justify-center rounded-full bg-violet-50 text-violet-700 text-[10px] font-black">
            {filteredEscalations.length.toLocaleString("fa-IR")}
          </span>
        </div>
        <p className="page-description">
          درخواست‌هایی که پاسخ هوش مصنوعی مشکل کاربر را حل نکرده است
        </p>
      </div>

      <div className="flex flex-col sm:flex-row sm:items-center gap-3">
        <div className="relative w-full sm:w-80">
          <Search className="absolute inset-y-0 my-auto right-3 w-3.5 h-3.5 text-slate-400" />
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="جستجو در نام کاربر یا عنوان تیکت..."
            className="w-full pr-9 pl-3 py-2.5 border border-slate-200 rounded-xl bg-white text-xs focus:outline-none focus:border-slate-400"
          />
        </div>
        <select
          value={status}
          onChange={(event) =>
            setStatus(event.target.value as EscalationStatus | "all")
          }
          className="bg-white border border-slate-200 rounded-xl px-3 py-2.5 text-[10px] font-bold text-slate-600 focus:outline-none"
        >
          <option value="all">همه وضعیت‌ها</option>
          <option value="waiting">در انتظار پاسخ</option>
          <option value="active">در حال گفتگو</option>
          <option value="resolved">حل‌شده</option>
        </select>
      </div>

      <div className="panel overflow-hidden">
        {filteredEscalations.length ? (
          <div className="divide-y divide-slate-100">
            {filteredEscalations.map((escalation) => {
              const ticket = tickets.find(
                (current) => current.id === escalation.ticketId,
              );
              const lastMessage =
                escalation.messages[escalation.messages.length - 1];
              return (
                <Link
                  key={escalation.id}
                  href={`/admin/escalated/${escalation.id}`}
                  className="p-5 sm:p-6 flex flex-col lg:flex-row lg:items-center justify-between gap-4 hover:bg-slate-50/40 transition-colors group"
                >
                  <div className="flex items-start gap-4 min-w-0">
                    <div className="w-10 h-10 rounded-2xl bg-violet-50 text-violet-600 flex items-center justify-center shrink-0">
                      <Headphones className="w-4.5 h-4.5" />
                    </div>
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <h2 className="text-xs font-black text-slate-800 group-hover:text-blue-600 transition-colors truncate">
                          {ticket?.title || `تیکت #${escalation.ticketId}`}
                        </h2>
                        <span className="text-[9px] font-bold text-slate-400">
                          #{escalation.ticketId.toLocaleString("fa-IR")}
                        </span>
                      </div>
                      <p className="text-[10px] font-bold text-slate-500 mt-1.5">
                        {escalation.requesterName}
                        {escalation.assignedAdminName
                          ? ` · کارشناس: ${escalation.assignedAdminName}`
                          : " · هنوز تخصیص داده نشده"}
                      </p>
                      <p className="text-[11px] text-slate-400 mt-2 truncate max-w-2xl">
                        {lastMessage?.text || escalation.reason}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center justify-between lg:justify-end gap-4 shrink-0">
                    <span className="text-[9px] text-slate-400">
                      آخرین بروزرسانی: {escalation.updatedAt}
                    </span>
                    <EscalationStatusBadge status={escalation.status} />
                  </div>
                </Link>
              );
            })}
          </div>
        ) : (
          <EmptyState
            title="ارجاعی با این شرایط پیدا نشد"
            description="فیلتر وضعیت یا عبارت جستجو را تغییر دهید."
          />
        )}
      </div>
    </div>
  );
}

