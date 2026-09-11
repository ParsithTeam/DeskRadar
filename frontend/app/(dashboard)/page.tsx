"use client";

import Link from "next/link";
import {
  AlertTriangle,
  CheckCircle2,
  Clock3,
  Headphones,
  Plus,
  Radar,
  Tickets,
} from "lucide-react";
import MetricCard from "@/components/metric-card";
import CategoryChart from "@/components/category-chart";
import RecentAlerts from "@/components/recent-alerts";
import { useAuth } from "@/lib/auth-context";
import { useAppData } from "@/lib/app-context";
import { TicketStatusBadge } from "@/components/status-badge";

export default function DashboardPage() {
  const { user } = useAuth();
  const { tickets, incidents, escalations } = useAppData();

  if (!user) return null;

  if (user.role === "user") {
    const myTickets = tickets.filter(
      (ticket) => ticket.requesterId === user.id,
    );
    const openCount = myTickets.filter(
      (ticket) =>
        ticket.status === "open" ||
        ticket.status === "in_progress" ||
        ticket.status === "escalated",
    ).length;
    const resolvedCount = myTickets.filter(
      (ticket) => ticket.status === "resolved",
    ).length;
    const activeEscalations = escalations.filter(
      (item) => item.requesterId === user.id && item.status !== "resolved",
    ).length;

    return (
      <div className="space-y-6">
        <section className="panel p-6 sm:p-7 flex flex-col sm:flex-row sm:items-center justify-between gap-5 overflow-hidden relative">
          <div className="absolute -top-20 -left-14 w-48 h-48 bg-blue-500/[0.05] rounded-full blur-2xl" />
          <div className="relative z-10 space-y-2">
            <p className="text-[11px] font-bold text-blue-600">
              سلام {user.name}،
            </p>
            <h1 className="page-title">چطور می‌توانیم کمکتان کنیم؟</h1>
            <p className="page-description max-w-lg">
              مشکل را با زبان خودتان بنویسید؛ Radar آن را تحلیل می‌کند و یک
              راه‌حل پیشنهادی به شما می‌دهد.
            </p>
          </div>
          <Link
            href="/my-tickets/new"
            className="relative z-10 inline-flex items-center justify-center gap-2 bg-slate-900 text-white text-xs font-bold px-5 py-3 rounded-xl hover:bg-slate-800 transition-colors shrink-0"
          >
            <Plus className="w-4 h-4" />
            ثبت تیکت جدید
          </Link>
        </section>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <MetricCard
            title="تیکت‌های باز من"
            value={openCount}
            valueColor="text-blue-600"
            description="در حال بررسی یا پاسخ"
            icon={Clock3}
          />
          <MetricCard
            title="ارجاع به کارشناس"
            value={activeEscalations}
            valueColor="text-violet-600"
            description="گفتگوهای فعال"
            icon={Headphones}
          />
          <MetricCard
            title="حل شده"
            value={resolvedCount}
            valueColor="text-emerald-600"
            description="درخواست‌های تکمیل‌شده"
            icon={CheckCircle2}
          />
        </div>

        <section className="panel overflow-hidden">
          <div className="px-5 sm:px-6 py-4 border-b border-slate-100 flex items-center justify-between">
            <div>
              <h2 className="text-sm font-black text-slate-800">
                آخرین تیکت‌های من
              </h2>
              <p className="text-[10px] text-slate-400 mt-1">
                آخرین وضعیت درخواست‌های ثبت‌شده
              </p>
            </div>
            <Link
              href="/my-tickets"
              className="text-[11px] font-bold text-blue-600 hover:text-blue-700"
            >
              مشاهده همه
            </Link>
          </div>
          <div className="divide-y divide-slate-100">
            {myTickets.slice(0, 4).map((ticket) => (
              <Link
                key={ticket.id}
                href={`/my-tickets/${ticket.id}`}
                className="px-5 sm:px-6 py-4 flex items-center justify-between gap-4 hover:bg-slate-50/50 transition-colors"
              >
                <div className="min-w-0">
                  <p className="text-xs font-bold text-slate-800 truncate">
                    {ticket.title}
                  </p>
                  <p className="text-[10px] text-slate-400 mt-1">
                    #{ticket.id.toLocaleString("fa-IR")} · {ticket.createdAt}
                  </p>
                </div>
                <TicketStatusBadge status={ticket.status} />
              </Link>
            ))}
          </div>
        </section>
      </div>
    );
  }

  const openTickets = tickets.filter(
    (ticket) => ticket.status !== "resolved" && ticket.status !== "closed",
  ).length;
  const urgentTickets = tickets.filter(
    (ticket) =>
      ticket.urgency === "high" || ticket.urgency === "critical",
  ).length;
  const activeIncidents = incidents.filter(
    (incident) =>
      incident.status !== "resolved" && incident.status !== "dismissed",
  ).length;
  const waitingEscalations = escalations.filter(
    (item) => item.status === "waiting",
  ).length;

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h1 className="page-title">خلاصه گزارشات</h1>
        <p className="page-description">
          نمای زنده وضعیت تیکت‌ها، رخدادها و ارجاعات تیم پشتیبانی
        </p>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <MetricCard
          title="تیکت‌های باز"
          value={openTickets}
          valueColor="text-blue-600"
          description="نیازمند رسیدگی تیم"
          icon={Tickets}
        />
        <MetricCard
          title="فوری و بحرانی"
          value={urgentTickets}
          valueColor="text-rose-500"
          description="اولویت رسیدگی بالا"
          icon={AlertTriangle}
        />
        <MetricCard
          title="رخدادهای احتمالی"
          value={activeIncidents}
          valueColor="text-amber-500"
          description="خوشه‌های فعال Radar"
          icon={Radar}
        />
        <MetricCard
          title="ارجاع منتظر پاسخ"
          value={waitingEscalations}
          valueColor="text-violet-600"
          description="نیازمند اپراتور انسانی"
          icon={Headphones}
        />
      </div>
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
        <CategoryChart />
        <RecentAlerts />
      </div>
    </div>
  );
}
