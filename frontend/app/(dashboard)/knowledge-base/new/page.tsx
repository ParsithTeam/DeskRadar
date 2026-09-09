"use client";

import Link from "next/link";
import { ArrowRight, Save } from "lucide-react";
import { useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { AccessDenied } from "@/components/loading-state";
import type { TicketCategory } from "@/types";

export default function NewArticlePage() {
  const { user } = useAuth();
  const [title, setTitle] = useState("");
  const [summary, setSummary] = useState("");
  const [category, setCategory] = useState<TicketCategory>("vpn");
  const [tags, setTags] = useState("");
  const [content, setContent] = useState("");

  if (!user || user.role !== "admin") return <AccessDenied />;

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Link
        href="/knowledge-base"
        className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-400 hover:text-slate-700"
      >
        <ArrowRight className="w-4 h-4" />
        بازگشت به پایگاه دانش
      </Link>
      <div className="space-y-1.5">
        <h1 className="page-title">ساخت مقاله راهنما</h1>
        <p className="page-description">
          یک راهنمای کوتاه و قابل اجرا برای مشکلات پرتکرار بسازید.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="panel p-5 sm:p-7 space-y-5">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div className="space-y-2">
            <label htmlFor="title" className="text-xs font-bold text-slate-700">
              عنوان مقاله
            </label>
            <input
              id="title"
              required
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              className="form-input text-xs"
              placeholder="عنوان روشن و قابل جستجو"
            />
          </div>
          <div className="space-y-2">
            <label
              htmlFor="category"
              className="text-xs font-bold text-slate-700"
            >
              دسته‌بندی
            </label>
            <select
              id="category"
              value={category}
              onChange={(event) =>
                setCategory(event.target.value as TicketCategory)
              }
              className="form-input text-xs"
            >
              <option value="vpn">VPN</option>
              <option value="email">ایمیل</option>
              <option value="network">شبکه</option>
              <option value="printer">پرینتر</option>
              <option value="account">حساب و دسترسی</option>
              <option value="permission">مجوزها</option>
              <option value="software">نرم‌افزار</option>
              <option value="hardware">سخت‌افزار</option>
            </select>
          </div>
        </div>

        <div className="space-y-2">
          <label
            htmlFor="summary"
            className="text-xs font-bold text-slate-700"
          >
            خلاصه
          </label>
          <textarea
            id="summary"
            required
            rows={3}
            value={summary}
            onChange={(event) => setSummary(event.target.value)}
            className="form-input text-xs leading-6 resize-y"
            placeholder="این مقاله چه مسئله‌ای را حل می‌کند؟"
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="tags" className="text-xs font-bold text-slate-700">
            برچسب‌ها
          </label>
          <input
            id="tags"
            value={tags}
            onChange={(event) => setTags(event.target.value)}
            className="form-input text-xs"
            placeholder="با ویرگول جدا کنید؛ مثل VPN، احراز هویت، دورکاری"
          />
        </div>

        <div className="space-y-2">
          <label
            htmlFor="content"
            className="text-xs font-bold text-slate-700"
          >
            محتوای مقاله
          </label>
          <textarea
            id="content"
            required
            rows={14}
            value={content}
            onChange={(event) => setContent(event.target.value)}
            className="form-input text-xs leading-7 resize-y"
            placeholder={"## عنوان بخش\n\nتوضیح مرحله...\n\n1. مرحله اول"}
          />
          <p className="text-[10px] text-slate-400">
            برای تیتر از ## و برای مراحل از شماره و نقطه استفاده کنید.
          </p>
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled
            title="API پایگاه دانش در بک‌اند پیاده‌سازی نشده است."
            className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-slate-300 text-white text-xs font-bold cursor-not-allowed"
          >
            <Save className="w-4 h-4" />
            ذخیره مقاله (در انتظار بک‌اند)
          </button>
        </div>
      </form>
    </div>
  );
}
