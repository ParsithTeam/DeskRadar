"use client";

import Link from "next/link";
import {
  ArrowRight,
  CheckCircle2,
  Radar,
  ShieldCheck,
  XCircle,
} from "lucide-react";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { useAppData } from "@/lib/app-context";
import { useAuth } from "@/lib/auth-context";
import LoadingSkeleton, {
  AccessDenied,
  EmptyState,
} from "@/components/loading-state";
import UrgencyBadge, {
  IncidentStatusBadge,
} from "@/components/status-badge";

export default function IncidentDetailPage() {
  const params = useParams<{ id: string }>();
  const { user } = useAuth();
  const { incidents, loadIncident, updateIncidentStatus } = useAppData();
  const incidentId = Number(params.id);
  const incident = incidents.find((item) => item.id === incidentId);
  const [loadingDetail, setLoadingDetail] = useState(
    Number.isFinite(incidentId),
  );
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    let active = true;
    if (!Number.isFinite(incidentId)) {
      return;
    }
    void loadIncident(incidentId)
      .catch(() => undefined)
      .finally(() => {
        if (active) setLoadingDetail(false);
      });
    return () => {
      active = false;
    };
  }, [incidentId, loadIncident]);

  if (!user || user.role !== "admin") return <AccessDenied />;
  if (loadingDetail && !incident) return <LoadingSkeleton />;

  if (!incident) {
    return (
      <div className="panel">
        <EmptyState
          title="رخداد پیدا نشد"
          description="شناسه رخداد معتبر نیست یا این مورد حذف شده است."
        />
      </div>
    );
  }

  const changeStatus = async (status: "confirmed" | "resolved" | "dismissed") => {
    setUpdating(true);
    try {
      await updateIncidentStatus(incident.id, status);
    } catch {
      // The provider displays the backend error globally.
    } finally {
      setUpdating(false);
    }
  };

  return (
    <div className="space-y-6">
      <Link
        href="/incidents"
        className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-400 hover:text-slate-700"
      >
        <ArrowRight className="w-4 h-4" />
        بازگشت به رادار رخدادها
      </Link>

      <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="page-title">{incident.title}</h1>
            <IncidentStatusBadge status={incident.status} />
          </div>
          <p className="page-description">
            رخداد #{incident.id.toLocaleString("fa-IR")} · شناسایی در{" "}
            {incident.createdAt}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {incident.status === "candidate" && (
            <>
              <button
                type="button"
                disabled={updating}
                onClick={() => void changeStatus("confirmed")}
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-900 text-white text-[10px] font-bold cursor-pointer"
              >
                <ShieldCheck className="w-4 h-4" />
                تأیید رخداد
              </button>
              <button
                type="button"
                disabled={updating}
                onClick={() => void changeStatus("dismissed")}
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-100 text-slate-700 border border-slate-200 text-[10px] font-bold cursor-pointer"
              >
                <XCircle className="w-4 h-4" />
                رد کردن رخداد
              </button>
            </>
          )}
          {incident.status === "confirmed" && (
            <button
              type="button"
              disabled={updating}
              onClick={() => void changeStatus("resolved")}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-50 text-emerald-700 border border-emerald-100 text-[10px] font-bold cursor-pointer"
            >
              <CheckCircle2 className="w-4 h-4" />
              ثبت به‌عنوان رفع‌شده
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2 space-y-6">
          <section className="panel p-5 sm:p-6 space-y-5">
            <div className="flex items-center gap-2">
              <Radar className="w-4 h-4 text-rose-500" />
              <h2 className="text-xs font-black text-slate-800">
                چرا Radar این رخداد را ساخته است؟
              </h2>
            </div>
            <p className="text-xs text-slate-600 leading-7">
              {incident.detectedReason}
            </p>
            <div className="bg-slate-50/70 border border-slate-100 rounded-xl p-4">
              <p className="text-[11px] text-slate-500 leading-6">
                {incident.description}
              </p>
            </div>
          </section>

          <section className="panel overflow-hidden">
            <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
              <div>
                <h2 className="text-xs font-black text-slate-800">
                  خوشه تیکت‌های مرتبط
                </h2>
                <p className="text-[10px] text-slate-400 mt-1">
                  مرتب‌شده بر اساس امتیاز شباهت معنایی
                </p>
              </div>
              <span className="text-[10px] font-bold text-slate-400">
                {incident.tickets.length.toLocaleString("fa-IR")} مورد
              </span>
            </div>
            <div className="divide-y divide-slate-100">
              {incident.tickets.map((ticket) => (
                <Link
                  key={ticket.ticketId}
                  href={`/tickets/${ticket.ticketId}`}
                  className="px-5 py-4 flex items-center justify-between gap-4 hover:bg-slate-50/50 group"
                >
                  <div className="min-w-0">
                    <p className="text-xs font-bold text-slate-700 group-hover:text-blue-600 transition-colors truncate">
                      {ticket.title}
                    </p>
                    <p className="text-[9px] text-slate-400 mt-1">
                      تیکت #{ticket.ticketId.toLocaleString("fa-IR")}
                    </p>
                  </div>
                  {ticket.similarity !== undefined && (
                    <span className="text-[10px] font-black text-blue-600 bg-blue-50 px-2.5 py-1 rounded-lg shrink-0">
                      {(ticket.similarity * 100).toLocaleString("fa-IR")}٪ شباهت
                    </span>
                  )}
                </Link>
              ))}
            </div>
          </section>
        </div>

        <aside className="space-y-5">
          <section className="panel p-5 space-y-4">
            <h2 className="text-[10px] font-black text-slate-400">
              مشخصات رخداد
            </h2>
            {incident.category !== "unknown" && (
              <DetailRow label="دسته" value={incident.categoryLabelFa} />
            )}
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-slate-400">شدت</span>
              <UrgencyBadge level={incident.severity} />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-slate-400">وضعیت</span>
              <IncidentStatusBadge status={incident.status} />
            </div>
            <DetailRow
              label="تعداد تیکت"
              value={incident.tickets.length.toLocaleString("fa-IR")}
            />
            {incident.resolvedAt && (
              <DetailRow label="زمان رفع" value={incident.resolvedAt} />
            )}
          </section>

          <section className="panel p-5">
            <p className="text-[10px] text-slate-400 leading-6">
              تأیید رخداد به این معناست که تیم پشتیبانی وجود یک اختلال گسترده
              را پذیرفته است. رخدادهای اشتباه را «رد شده» و رخدادهای تأییدشده
              را پس از رفع مشکل «رفع‌شده» کنید.
            </p>
          </section>
        </aside>
      </div>
    </div>
  );
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-3 text-[10px]">
      <span className="text-slate-400">{label}</span>
      <span className="font-bold text-slate-700 text-left">{value}</span>
    </div>
  );
}
