"use client";

import Link from "next/link";
import { ArrowRight, CheckCircle2, UserCheck } from "lucide-react";
import { useParams } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { useAppData } from "@/lib/app-context";
import { AccessDenied, EmptyState } from "@/components/loading-state";
import EscalationConversation from "@/components/escalation-conversation";
import {
  EscalationStatusBadge,
  TicketStatusBadge,
} from "@/components/status-badge";

export default function EscalationDetailPage() {
  const params = useParams<{ id: string }>();
  const { user } = useAuth();
  const {
    escalations,
    tickets,
    updateEscalationStatus,
  } = useAppData();
  const escalation = escalations.find((item) => item.id === params.id);
  const ticket = tickets.find(
    (item) => item.id === escalation?.ticketId,
  );

  if (!user || user.role !== "admin") return <AccessDenied />;

  if (!escalation || !ticket) {
    return (
      <div className="panel">
        <EmptyState
          title="پرونده ارجاع پیدا نشد"
          description="ممکن است این پرونده حذف شده یا شناسه آن نادرست باشد."
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Link
        href="/admin/escalated"
        className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-400 hover:text-slate-700"
      >
        <ArrowRight className="w-4 h-4" />
        بازگشت به اینباکس ارجاعات
      </Link>

      <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="page-title">{ticket.title}</h1>
            <EscalationStatusBadge status={escalation.status} />
          </div>
          <p className="page-description">
            ارجاع از {escalation.requesterName} · تیکت #
            {ticket.id.toLocaleString("fa-IR")} · {escalation.createdAt}
          </p>
        </div>

        <div className="flex items-center gap-2">
          {escalation.status === "waiting" && (
            <button
              type="button"
              onClick={() =>
                updateEscalationStatus(escalation.id, "active", user)
              }
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-900 text-white text-[10px] font-bold cursor-pointer"
            >
              <UserCheck className="w-4 h-4" />
              پذیرش و شروع گفتگو
            </button>
          )}
          {escalation.status !== "resolved" && (
            <button
              type="button"
              onClick={() =>
                updateEscalationStatus(escalation.id, "resolved", user)
              }
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-50 text-emerald-700 border border-emerald-100 text-[10px] font-bold cursor-pointer"
            >
              <CheckCircle2 className="w-4 h-4" />
              حل شد و بستن پرونده
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2">
          <EscalationConversation escalation={escalation} />
        </div>

        <aside className="space-y-5">
          <section className="panel p-5 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-[10px] font-black text-slate-400">
                خلاصه تیکت
              </h2>
              <TicketStatusBadge status={ticket.status} />
            </div>
            <p className="text-xs font-black text-slate-800 leading-6">
              {ticket.title}
            </p>
            <p className="text-[11px] text-slate-500 leading-6">
              {ticket.description}
            </p>
            <Link
              href={`/tickets/${ticket.id}`}
              className="inline-flex text-[10px] font-bold text-blue-600"
            >
              مشاهده تحلیل کامل تیکت
            </Link>
          </section>

          <section className="panel p-5 space-y-3">
            <h2 className="text-[10px] font-black text-slate-400">
              دلیل ارجاع کاربر
            </h2>
            <p className="text-[11px] text-slate-600 leading-6">
              {escalation.reason}
            </p>
          </section>

          <section className="panel p-5 space-y-3 text-[11px]">
            <h2 className="text-[10px] font-black text-slate-400">
              مسئول رسیدگی
            </h2>
            <p className="font-bold text-slate-700">
              {escalation.assignedAdminName || "هنوز تخصیص داده نشده"}
            </p>
            <p className="text-slate-400">
              آخرین بروزرسانی: {escalation.updatedAt}
            </p>
          </section>
        </aside>
      </div>
    </div>
  );
}
