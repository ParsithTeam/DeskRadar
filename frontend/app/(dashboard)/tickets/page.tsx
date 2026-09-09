"use client";

import Link from "next/link";
import { FileUp, Search, Sparkles } from "lucide-react";
import { useMemo, useState } from "react";
import { useAppData } from "@/lib/app-context";
import { useAuth } from "@/lib/auth-context";
import { AccessDenied, EmptyState } from "@/components/loading-state";
import UrgencyBadge, {
  AnalysisStatusBadge,
  TicketStatusBadge,
} from "@/components/status-badge";
import type {
  TicketCategory,
  TicketStatus,
  Urgency,
} from "@/types";

const PAGE_SIZE = 6;

export default function TicketsPage() {
  const { user } = useAuth();
  const { tickets, analyzeTicket } = useAppData();
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<
    TicketCategory | "all"
  >("all");
  const [selectedUrgency, setSelectedUrgency] = useState<Urgency | "all">(
    "all",
  );
  const [selectedStatus, setSelectedStatus] = useState<TicketStatus | "all">(
    "all",
  );
  const [page, setPage] = useState(1);
  const [notice, setNotice] = useState("");
  const [analyzingIds, setAnalyzingIds] = useState<number[]>([]);

  const filteredTickets = useMemo(
    () =>
      tickets.filter((ticket) => {
        const normalizedSearch = searchTerm.trim().toLowerCase();
        const matchesSearch =
          !normalizedSearch ||
          ticket.title.toLowerCase().includes(normalizedSearch) ||
          ticket.description.toLowerCase().includes(normalizedSearch) ||
          ticket.requesterName.toLowerCase().includes(normalizedSearch);
        const matchesCategory =
          selectedCategory === "all" || ticket.category === selectedCategory;
        const matchesUrgency =
          selectedUrgency === "all" || ticket.urgency === selectedUrgency;
        const matchesStatus =
          selectedStatus === "all" || ticket.status === selectedStatus;
        return (
          matchesSearch &&
          matchesCategory &&
          matchesUrgency &&
          matchesStatus
        );
      }),
    [
      searchTerm,
      selectedCategory,
      selectedStatus,
      selectedUrgency,
      tickets,
    ],
  );

  if (!user || user.role !== "admin") return <AccessDenied />;

  const pageCount = Math.max(Math.ceil(filteredTickets.length / PAGE_SIZE), 1);
  const safePage = Math.min(page, pageCount);
  const pageTickets = filteredTickets.slice(
    (safePage - 1) * PAGE_SIZE,
    safePage * PAGE_SIZE,
  );

  const updateFilter = (callback: () => void) => {
    callback();
    setPage(1);
  };

  const handleAnalyze = async (ticketId: number) => {
    setAnalyzingIds((current) => [...current, ticketId]);
    setNotice("");
    try {
      await analyzeTicket(ticketId);
      setNotice(`تحلیل تیکت #${ticketId.toLocaleString("fa-IR")} شروع شد.`);
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "شروع تحلیل ناموفق بود.");
    } finally {
      setAnalyzingIds((current) => current.filter((id) => id !== ticketId));
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div className="space-y-1.5">
          <div className="flex items-baseline gap-2">
            <h1 className="page-title">صندوق ورودی تیکت‌ها</h1>
            <span className="text-xs font-bold text-slate-400">
              ({filteredTickets.length.toLocaleString("fa-IR")})
            </span>
          </div>
          <p className="page-description">
            رصد تحلیل هوشمند و وضعیت تمام تیکت‌های سازمان
          </p>
        </div>
        <div>
          <button
            type="button"
            disabled
            title="endpoint فعلی بک‌اند فایل را دریافت یا ذخیره نمی‌کند."
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white border border-slate-200 text-[11px] font-bold text-slate-400 cursor-not-allowed opacity-70"
          >
            <FileUp className="w-4 h-4" />
            ورود فایل CSV (در انتظار بک‌اند)
          </button>
        </div>
      </div>

      {notice && (
        <div className="panel px-4 py-3 flex items-center justify-between gap-4">
          <p className="text-[11px] font-bold text-slate-600">{notice}</p>
          <button
            type="button"
            onClick={() => setNotice("")}
            className="text-[10px] text-slate-400 cursor-pointer"
          >
            بستن
          </button>
        </div>
      )}

      <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-3 text-xs">
        <div className="relative w-full xl:w-80">
          <Search className="absolute inset-y-0 my-auto right-3 w-3.5 h-3.5 text-slate-400 pointer-events-none" />
          <input
            type="search"
            placeholder="جستجو در عنوان، شرح یا نام درخواست‌کننده..."
            value={searchTerm}
            onChange={(event) =>
              updateFilter(() => setSearchTerm(event.target.value))
            }
            className="w-full pr-9 pl-3 py-2.5 border border-slate-200 rounded-xl bg-white text-slate-800 placeholder-slate-400 focus:outline-none focus:border-slate-400"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <FilterSelect
            label="دسته"
            value={selectedCategory}
            onChange={(value) =>
              updateFilter(() =>
                setSelectedCategory(value as TicketCategory | "all"),
              )
            }
            options={[
              ["all", "همه"],
              ["vpn", "مشکلات VPN"],
              ["email", "سرویس ایمیل"],
              ["network", "شبکه"],
              ["printer", "پرینتر"],
              ["account", "حساب و دسترسی"],
              ["permission", "مجوزها"],
              ["software", "نرم‌افزار"],
              ["hardware", "سخت‌افزار"],
              ["unknown", "نامشخص"],
            ]}
          />
          <FilterSelect
            label="اولویت"
            value={selectedUrgency}
            onChange={(value) =>
              updateFilter(() =>
                setSelectedUrgency(value as Urgency | "all"),
              )
            }
            options={[
              ["all", "همه"],
              ["low", "کم"],
              ["medium", "متوسط"],
              ["high", "فوری"],
              ["critical", "بحرانی"],
              ["unknown", "نامشخص"],
            ]}
          />
          <FilterSelect
            label="وضعیت"
            value={selectedStatus}
            onChange={(value) =>
              updateFilter(() =>
                setSelectedStatus(value as TicketStatus | "all"),
              )
            }
            options={[
              ["all", "همه"],
              ["open", "باز"],
              ["in_progress", "در حال پیگیری"],
              ["escalated", "ارجاع‌شده"],
              ["resolved", "حل‌شده"],
            ]}
          />
        </div>
      </div>

      <div className="panel overflow-hidden">
        {pageTickets.length ? (
          <>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[970px] text-right border-collapse">
                <thead>
                  <tr className="border-b border-slate-100 text-[10px] font-bold text-slate-400 bg-slate-50/40">
                    <th className="py-3.5 px-5 w-20">شناسه</th>
                    <th className="py-3.5 px-4">شرح درخواست</th>
                    <th className="py-3.5 px-4 w-32">دسته‌بندی</th>
                    <th className="py-3.5 px-4 w-28">اولویت</th>
                    <th className="py-3.5 px-4 w-32">تحلیل AI</th>
                    <th className="py-3.5 px-4 w-28">وضعیت</th>
                    <th className="py-3.5 px-5 w-36 text-left">زمان ثبت</th>
                  </tr>
                </thead>
                <tbody className="text-xs text-slate-600 divide-y divide-slate-100">
                  {pageTickets.map((ticket) => (
                    <tr
                      key={ticket.id}
                      className="hover:bg-slate-50/40 transition-colors"
                    >
                      <td className="py-4 px-5 text-slate-400 text-[11px]">
                        #{ticket.id.toLocaleString("fa-IR")}
                      </td>
                      <td className="py-4 px-4 max-w-md">
                        <Link
                          href={`/tickets/${ticket.id}`}
                          className="group block"
                        >
                          <p className="font-bold text-slate-900 group-hover:text-blue-600 transition-colors truncate">
                            {ticket.title}
                          </p>
                          <p className="text-[10px] text-slate-400 mt-1 truncate">
                            {ticket.requesterName} · {ticket.department}
                          </p>
                        </Link>
                      </td>
                      <td className="py-4 px-4 text-[11px] font-medium">
                        {ticket.categoryLabelFa}
                      </td>
                      <td className="py-4 px-4">
                        <UrgencyBadge level={ticket.urgency} />
                      </td>
                      <td className="py-4 px-4">
                        {ticket.analysisStatus === "waiting" ||
                        ticket.analysisStatus === "failed" ? (
                          <button
                            type="button"
                            disabled={analyzingIds.includes(ticket.id)}
                            onClick={() => void handleAnalyze(ticket.id)}
                            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-100 hover:bg-amber-100 transition-colors cursor-pointer"
                          >
                            <Sparkles className="w-3 h-3" />
                            {analyzingIds.includes(ticket.id)
                              ? "در حال ارسال..."
                              : ticket.analysisStatus === "failed"
                                ? "تحلیل مجدد"
                                : "تحلیل"}
                          </button>
                        ) : (
                          <div className="space-y-1">
                            <AnalysisStatusBadge
                              status={ticket.analysisStatus}
                            />
                            {ticket.analysisStatus === "complete" &&
                              ticket.confidence > 0 && (
                                <span className="block text-[9px] text-slate-400 pr-1">
                                  اطمینان{" "}
                                  {(ticket.confidence * 100).toLocaleString(
                                    "fa-IR",
                                  )}
                                  ٪
                                </span>
                              )}
                          </div>
                        )}
                      </td>
                      <td className="py-4 px-4">
                        <TicketStatusBadge status={ticket.status} />
                      </td>
                      <td className="py-4 px-5 text-left text-slate-400 text-[10px]">
                        {ticket.createdAt}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {pageCount > 1 && (
              <div className="px-5 py-3.5 border-t border-slate-100 flex items-center justify-between">
                <p className="text-[10px] text-slate-400">
                  صفحه {safePage.toLocaleString("fa-IR")} از{" "}
                  {pageCount.toLocaleString("fa-IR")}
                </p>
                <div className="flex gap-2">
                  <button
                    type="button"
                    disabled={safePage === 1}
                    onClick={() => setPage((current) => current - 1)}
                    className="px-3 py-1.5 rounded-lg border border-slate-200 text-[10px] font-bold text-slate-600 disabled:opacity-40 cursor-pointer"
                  >
                    قبلی
                  </button>
                  <button
                    type="button"
                    disabled={safePage === pageCount}
                    onClick={() => setPage((current) => current + 1)}
                    className="px-3 py-1.5 rounded-lg border border-slate-200 text-[10px] font-bold text-slate-600 disabled:opacity-40 cursor-pointer"
                  >
                    بعدی
                  </button>
                </div>
              </div>
            )}
          </>
        ) : (
          <EmptyState
            title="تیکتی با این فیلتر پیدا نشد"
            description="عبارت جستجو یا فیلترهای انتخاب‌شده را تغییر دهید."
          />
        )}
      </div>
    </div>
  );
}

function FilterSelect({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: [string, string][];
}) {
  return (
    <label className="flex items-center bg-white border border-slate-200 rounded-xl px-2.5 py-2">
      <span className="text-slate-400 text-[10px] font-bold ml-1.5">
        {label}:
      </span>
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="bg-transparent text-slate-700 font-semibold focus:outline-none cursor-pointer text-[10px]"
      >
        {options.map(([optionValue, optionLabel]) => (
          <option key={optionValue} value={optionValue}>
            {optionLabel}
          </option>
        ))}
      </select>
    </label>
  );
}
