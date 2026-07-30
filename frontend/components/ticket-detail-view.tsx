"use client";

import Link from "next/link";
import {
  ArrowRight,
  BookOpen,
  Check,
  Copy,
  Headphones,
  RefreshCw,
  Sparkles,
} from "lucide-react";
import { useState } from "react";
import { useAppData } from "@/lib/app-context";
import { useAuth } from "@/lib/auth-context";
import { AccessDenied, EmptyState } from "@/components/loading-state";
import EscalationConversation from "@/components/escalation-conversation";
import UrgencyBadge, {
  AnalysisStatusBadge,
  EscalationStatusBadge,
  TicketStatusBadge,
} from "@/components/status-badge";
import type { TicketStatus } from "@/types";

export default function TicketDetailView({
  ticketId,
  view,
}: {
  ticketId: number;
  view: "admin" | "user";
}) {
  const { user } = useAuth();
  const {
    tickets,
    escalations,
    analyzeTicket,
    updateTicketStatus,
    escalateTicket,
  } = useAppData();
  const [copied, setCopied] = useState(false);
  const [feedback, setFeedback] = useState<"up" | "down" | null>(null);
  const [showEscalationForm, setShowEscalationForm] = useState(false);
  const [escalationReason, setEscalationReason] = useState("");

  const ticket = tickets.find((item) => item.id === ticketId);
  const escalation = escalations.find((item) => item.ticketId === ticketId);

  if (!user) return null;
  if (view === "admin" && user.role !== "admin") return <AccessDenied />;
  if (
    view === "user" &&
    (user.role !== "user" || ticket?.requesterId !== user.id)
  ) {
    return <AccessDenied />;
  }

  if (!ticket) {
    return (
      <div className="panel">
        <EmptyState
          title="تیکت پیدا نشد"
          description="ممکن است این تیکت حذف شده یا شناسه آن نادرست باشد."
          action={
            <Link
              href={view === "admin" ? "/tickets" : "/my-tickets"}
              className="text-[11px] font-bold text-blue-600"
            >
              بازگشت به فهرست
            </Link>
          }
        />
      </div>
    );
  }

  const analysis = ticket.analysis;
  const backHref = view === "admin" ? "/tickets" : "/my-tickets";

  const handleCopyReply = async () => {
    if (!analysis) return;
    await navigator.clipboard.writeText(analysis.suggestedReplyFa);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1800);
  };

  const submitEscalation = (event: React.FormEvent) => {
    event.preventDefault();
    if (!escalationReason.trim()) return;
    escalateTicket(ticket.id, escalationReason, user);
    setEscalationReason("");
    setShowEscalationForm(false);
  };

  return (
    <div className="space-y-6">
      <Link
        href={backHref}
        className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-400 hover:text-slate-700 transition-colors"
      >
        <ArrowRight className="w-4 h-4" />
        بازگشت به {view === "admin" ? "صندوق تیکت‌ها" : "تیکت‌های من"}
      </Link>

      <div className="flex flex-col xl:flex-row xl:items-start justify-between gap-4">
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="page-title">{ticket.title}</h1>
            <span className="text-[11px] font-bold text-slate-400 bg-slate-100 px-2.5 py-1 rounded-lg">
              #{ticket.id.toLocaleString("fa-IR")}
            </span>
          </div>
          <p className="page-description">
            ثبت‌شده توسط {ticket.requesterName} از {ticket.department} ·{" "}
            {ticket.createdAt}
          </p>
        </div>

        <div className="flex items-center flex-wrap gap-2">
          <TicketStatusBadge status={ticket.status} />
          <AnalysisStatusBadge status={ticket.analysisStatus} />
          {view === "admin" && (
            <select
              aria-label="تغییر وضعیت تیکت"
              value={ticket.status}
              onChange={(event) =>
                updateTicketStatus(
                  ticket.id,
                  event.target.value as TicketStatus,
                )
              }
              className="bg-white border border-slate-200 rounded-xl px-3 py-2 text-[10px] font-bold text-slate-600 focus:outline-none cursor-pointer"
            >
              <option value="open">باز</option>
              <option value="in_progress">در حال پیگیری</option>
              <option value="escalated">ارجاع‌شده</option>
              <option value="resolved">حل‌شده</option>
              <option value="closed">بسته</option>
            </select>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2 space-y-6">
          <section className="panel p-5 space-y-2.5">
            <h2 className="text-[10px] font-black text-slate-400 tracking-wide">
              متن اصلی درخواست
            </h2>
            <p className="text-xs text-slate-700 leading-7 font-medium">
              {ticket.description}
            </p>
          </section>

          {analysis ? (
            <>
              <section className="panel p-5 sm:p-6 space-y-5">
                <div className="flex items-center justify-between gap-3 border-b border-slate-100 pb-4">
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-blue-600" />
                    <h2 className="text-xs font-black text-slate-800">
                      تحلیل هوشمند Radar
                    </h2>
                  </div>
                  <span className="text-[10px] font-bold text-blue-600 bg-blue-50 px-2.5 py-1 rounded-lg">
                    اطمینان مدل:{" "}
                    {(analysis.confidence * 100).toLocaleString("fa-IR")}٪
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 text-xs">
                  <InfoItem
                    label="دسته تشخیصی"
                    value={analysis.categoryLabelFa}
                  />
                  <InfoItem
                    label="قصد دقیق درخواست"
                    value={analysis.intentLabelFa}
                  />
                  <div className="space-y-1.5">
                    <span className="text-slate-400 block text-[10px]">
                      اولویت پیشنهادی
                    </span>
                    <UrgencyBadge level={analysis.urgency} />
                  </div>
                </div>

                <div className="space-y-1.5 pt-1">
                  <span className="text-slate-400 block text-[10px] font-bold">
                    خلاصه تحلیل
                  </span>
                  <p className="text-xs text-slate-600 leading-7 font-medium bg-slate-50/70 p-4 rounded-xl border border-slate-100">
                    {analysis.summaryFa}
                  </p>
                </div>

                <div className="space-y-2">
                  <span className="text-slate-400 block text-[10px] font-bold">
                    دلایل تصمیم سیستم
                  </span>
                  <ul className="space-y-2 text-[11px] text-slate-600">
                    {analysis.reasonsFa.map((reason) => (
                      <li key={reason} className="flex items-start gap-2">
                        <Check className="w-3.5 h-3.5 text-emerald-500 mt-1 shrink-0" />
                        <span className="leading-6">{reason}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </section>

              <section className="bg-slate-900 text-white p-5 sm:p-6 rounded-2xl shadow-sm space-y-4 relative overflow-hidden">
                <div className="absolute -top-12 -left-12 w-32 h-32 bg-blue-500/10 rounded-full blur-2xl" />
                <div className="flex items-center justify-between gap-3 relative z-10">
                  <h2 className="text-xs font-black text-slate-300">
                    پاسخ پیشنهادی فارسی
                  </h2>
                  <button
                    type="button"
                    onClick={handleCopyReply}
                    className="inline-flex items-center gap-1.5 text-[10px] font-bold bg-white/10 hover:bg-white/20 px-3 py-1.5 rounded-lg transition-colors cursor-pointer"
                  >
                    {copied ? (
                      <>
                        <Check className="w-3.5 h-3.5" /> کپی شد
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5" /> کپی متن
                      </>
                    )}
                  </button>
                </div>
                <p className="text-xs text-slate-200 leading-7 relative z-10 bg-white/[0.03] p-4 rounded-xl border border-white/[0.06]">
                  {analysis.suggestedReplyFa}
                </p>

                {view === "user" && !escalation && ticket.status !== "resolved" && (
                  <div className="relative z-10 pt-1">
                    {!showEscalationForm ? (
                      <button
                        type="button"
                        onClick={() => setShowEscalationForm(true)}
                        className="inline-flex items-center gap-2 text-[11px] font-bold text-white bg-violet-600 hover:bg-violet-500 px-4 py-2.5 rounded-xl transition-colors cursor-pointer"
                      >
                        <Headphones className="w-4 h-4" />
                        با این پاسخ مشکلم حل نشد
                      </button>
                    ) : (
                      <form
                        onSubmit={submitEscalation}
                        className="bg-white/[0.06] border border-white/10 p-4 rounded-xl space-y-3"
                      >
                        <label
                          htmlFor="escalation-reason"
                          className="text-[11px] font-bold text-slate-200"
                        >
                          چه بخشی از مشکل هنوز باقی مانده است؟
                        </label>
                        <textarea
                          id="escalation-reason"
                          required
                          rows={3}
                          value={escalationReason}
                          onChange={(event) =>
                            setEscalationReason(event.target.value)
                          }
                          placeholder="نتیجه انجام راه‌حل بالا را برای کارشناس بنویسید..."
                          className="w-full bg-white text-slate-800 rounded-xl p-3 text-xs leading-6 focus:outline-none"
                        />
                        <div className="flex items-center gap-2">
                          <button
                            type="submit"
                            className="px-4 py-2 rounded-lg bg-violet-600 text-white text-[10px] font-bold cursor-pointer"
                          >
                            ارسال برای کارشناس
                          </button>
                          <button
                            type="button"
                            onClick={() => setShowEscalationForm(false)}
                            className="px-3 py-2 text-[10px] text-slate-400 cursor-pointer"
                          >
                            انصراف
                          </button>
                        </div>
                      </form>
                    )}
                  </div>
                )}
              </section>
            </>
          ) : (
            <section className="panel p-8 flex flex-col items-center text-center">
              <div className="w-11 h-11 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mb-4">
                <RefreshCw className="w-5 h-5 animate-spin" />
              </div>
              <h2 className="text-sm font-black text-slate-800">
                تحلیل هوشمند در حال آماده‌سازی است
              </h2>
              <p className="text-xs text-slate-400 mt-2 leading-6">
                نتیجه دسته‌بندی، فوریت و پاسخ پیشنهادی تا چند لحظه دیگر نمایش
                داده می‌شود.
              </p>
              {view === "admin" && (
                <button
                  type="button"
                  onClick={() => analyzeTicket(ticket.id)}
                  className="mt-4 px-4 py-2 rounded-xl bg-slate-900 text-white text-[10px] font-bold cursor-pointer"
                >
                  اجرای مجدد تحلیل
                </button>
              )}
            </section>
          )}

          {view === "user" && escalation && (
            <EscalationConversation escalation={escalation} />
          )}
        </div>

        <aside className="space-y-5">
          {analysis?.relatedArticle && (
            <section className="panel p-5 space-y-4">
              <div className="flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-slate-400" />
                <h2 className="text-[10px] font-black text-slate-400">
                  مقاله راهنمای مرتبط
                </h2>
              </div>
              <Link
                href={`/knowledge-base/${analysis.relatedArticle.id}`}
                className="text-xs font-bold text-slate-800 hover:text-blue-600 transition-colors leading-6 block"
              >
                {analysis.relatedArticle.title}
              </Link>
              <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-[10px]">
                <span className="text-slate-400">انطباق معنایی</span>
                <span
                  className={`font-bold ${
                    analysis.relatedArticle.score < 0.8
                      ? "text-amber-600"
                      : "text-emerald-600"
                  }`}
                >
                  {analysis.relatedArticle.score < 0.8
                    ? "اطمینان پایین"
                    : `${(
                        analysis.relatedArticle.score * 100
                      ).toLocaleString("fa-IR")}٪`}
                </span>
              </div>
            </section>
          )}

          {view === "admin" && analysis && (
            <>
              <section className="panel p-5 space-y-4">
                <h2 className="text-[10px] font-black text-slate-400">
                  تیکت‌های مشابه
                </h2>
                <div className="divide-y divide-slate-100">
                  {analysis.similarTickets.map((similar) => (
                    <Link
                      key={similar.id}
                      href={`/tickets/${similar.id}`}
                      className="py-3 flex items-center justify-between gap-3 group"
                    >
                      <p className="text-[11px] font-bold text-slate-700 group-hover:text-blue-600 leading-5 line-clamp-2">
                        {similar.title}
                      </p>
                      <span className="text-[9px] font-bold text-slate-400 bg-slate-50 border border-slate-100 px-2 py-1 rounded shrink-0">
                        {(similar.score * 100).toLocaleString("fa-IR")}٪
                      </span>
                    </Link>
                  ))}
                </div>
              </section>

              <section className="panel p-5 space-y-4">
                <h2 className="text-[10px] font-black text-slate-400">
                  ارزیابی صحت تحلیل
                </h2>
                <p className="text-[11px] text-slate-500 leading-6">
                  دسته‌بندی و اولویت پیشنهادی مورد تأیید است؟
                </p>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setFeedback("up")}
                    className={`py-2.5 rounded-xl text-[10px] font-bold border transition-colors cursor-pointer ${
                      feedback === "up"
                        ? "bg-emerald-50 border-emerald-300 text-emerald-700"
                        : "border-slate-200 text-slate-500"
                    }`}
                  >
                    تأیید می‌کنم
                  </button>
                  <button
                    type="button"
                    onClick={() => setFeedback("down")}
                    className={`py-2.5 rounded-xl text-[10px] font-bold border transition-colors cursor-pointer ${
                      feedback === "down"
                        ? "bg-rose-50 border-rose-300 text-rose-700"
                        : "border-slate-200 text-slate-500"
                    }`}
                  >
                    نیاز به اصلاح
                  </button>
                </div>
                {feedback && (
                  <p className="text-[10px] font-bold text-emerald-600 bg-emerald-50 px-3 py-2 rounded-xl">
                    بازخورد شما ثبت شد.
                  </p>
                )}
              </section>
            </>
          )}

          {escalation && (
            <section className="panel p-5 space-y-3">
              <div className="flex items-center justify-between">
                <h2 className="text-[10px] font-black text-slate-400">
                  وضعیت ارجاع انسانی
                </h2>
                <EscalationStatusBadge status={escalation.status} />
              </div>
              <p className="text-[11px] text-slate-600 leading-6">
                {escalation.reason}
              </p>
              {view === "admin" && (
                <Link
                  href={`/admin/escalated/${escalation.id}`}
                  className="inline-flex text-[10px] font-bold text-blue-600"
                >
                  باز کردن گفتگوی ارجاع
                </Link>
              )}
            </section>
          )}
        </aside>
      </div>
    </div>
  );
}

function InfoItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="space-y-1.5">
      <span className="text-slate-400 block text-[10px]">{label}</span>
      <span className="font-bold text-slate-800 leading-6">{value}</span>
    </div>
  );
}

