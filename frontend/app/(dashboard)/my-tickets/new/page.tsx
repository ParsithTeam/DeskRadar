"use client";

import { ArrowRight, Send, Sparkles } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useAppData } from "@/lib/app-context";
import { useAuth } from "@/lib/auth-context";
import { AccessDenied } from "@/components/loading-state";

export default function NewTicketPage() {
  const { user } = useAuth();
  const { createTicket } = useAppData();
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [department, setDepartment] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  if (!user || user.role !== "user") return <AccessDenied />;

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!title.trim() || !description.trim() || !department.trim()) return;
    setSubmitting(true);
    setError("");
    try {
      const id = await createTicket({
        title: title.trim(),
        description: description.trim(),
        department: department.trim(),
        requesterId: user.id,
        requesterName: user.name,
      });
      router.push(`/my-tickets/${id}`);
    } catch (submitError) {
      setError(
        submitError instanceof Error
          ? submitError.message
          : "ثبت تیکت انجام نشد.",
      );
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <Link
        href="/my-tickets"
        className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-400 hover:text-slate-700"
      >
        <ArrowRight className="w-4 h-4" />
        بازگشت به تیکت‌های من
      </Link>

      <div className="space-y-1.5">
        <h1 className="page-title">ثبت تیکت جدید</h1>
        <p className="page-description">
          مشکل را با جزئیات بنویسید تا تحلیل و پاسخ دقیق‌تری دریافت کنید.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="panel p-5 sm:p-7 space-y-5">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div className="space-y-2">
            <label htmlFor="title" className="text-xs font-bold text-slate-700">
              عنوان کوتاه مشکل
            </label>
            <input
              id="title"
              required
              maxLength={120}
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              placeholder="مثلاً اتصال VPN برقرار نمی‌شود"
              className="form-input text-xs"
            />
          </div>
          <div className="space-y-2">
            <label
              htmlFor="department"
              className="text-xs font-bold text-slate-700"
            >
              واحد سازمانی
            </label>
            <input
              id="department"
              required
              value={department}
              onChange={(event) => setDepartment(event.target.value)}
              placeholder="مثلاً واحد فروش"
              className="form-input text-xs"
            />
          </div>
        </div>

        <div className="space-y-2">
          <label
            htmlFor="description"
            className="text-xs font-bold text-slate-700"
          >
            شرح کامل درخواست
          </label>
          <textarea
            id="description"
            required
            rows={7}
            minLength={15}
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            placeholder="چه اتفاقی افتاده، چه خطایی می‌بینید و این مشکل چه اثری روی کار شما گذاشته است؟"
            className="form-input text-xs leading-7 resize-y"
          />
          <p className="text-[10px] text-slate-400">
            لطفاً رمز عبور یا اطلاعات محرمانه را داخل تیکت ننویسید.
          </p>
        </div>

        <div className="bg-blue-50/60 border border-blue-100 rounded-xl p-4 flex items-start gap-3">
          <Sparkles className="w-4 h-4 text-blue-600 mt-0.5 shrink-0" />
          <p className="text-[11px] text-blue-700 leading-6">
            پس از ثبت، Radar دسته‌بندی، فوریت و راه‌حل پیشنهادی را به‌صورت
            خودکار آماده می‌کند. اگر راه‌حل مشکل را برطرف نکرد، می‌توانید همان
            تیکت را به کارشناس واقعی ارجاع دهید.
          </p>
        </div>

        {error && (
          <p className="text-[11px] font-bold text-rose-600 bg-rose-50 border border-rose-100 px-3 py-2 rounded-xl">
            {error}
          </p>
        )}

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={submitting}
            className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-slate-900 text-white text-xs font-bold hover:bg-slate-800 disabled:opacity-60 transition-colors cursor-pointer"
          >
            <Send className="w-4 h-4" />
            {submitting ? "در حال ثبت..." : "ثبت و شروع تحلیل"}
          </button>
        </div>
      </form>
    </div>
  );
}
