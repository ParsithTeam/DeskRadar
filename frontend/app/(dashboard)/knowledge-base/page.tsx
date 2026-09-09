"use client";

import Link from "next/link";
import { BookOpen, Plus, Search } from "lucide-react";
import { useMemo, useState } from "react";
import { useAppData } from "@/lib/app-context";
import { useAuth } from "@/lib/auth-context";
import { EmptyState } from "@/components/loading-state";
import type { TicketCategory } from "@/types";

export default function KnowledgeBasePage() {
  const { user } = useAuth();
  const { articles } = useAppData();
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState<TicketCategory | "all">("all");

  const filtered = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return articles.filter(
      (article) =>
        (category === "all" || article.category === category) &&
        (!normalized ||
          article.title.toLowerCase().includes(normalized) ||
          article.summary.toLowerCase().includes(normalized) ||
          article.tags.some((tag) => tag.toLowerCase().includes(normalized))),
    );
  }, [articles, category, query]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div className="space-y-1.5">
          <h1 className="page-title">پایگاه دانش</h1>
          <p className="page-description">
            راهنماهای فارسی برای حل سریع مشکلات پرتکرار سازمان
          </p>
        </div>
        {user?.role === "admin" && (
          <Link
            href="/knowledge-base/new"
            className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-slate-900 text-white text-[11px] font-bold"
          >
            <Plus className="w-4 h-4" />
            ساخت مقاله
          </Link>
        )}
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative w-full sm:w-80">
          <Search className="absolute inset-y-0 my-auto right-3 w-3.5 h-3.5 text-slate-400" />
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="جستجو در عنوان، خلاصه یا برچسب..."
            className="w-full pr-9 pl-3 py-2.5 border border-slate-200 rounded-xl bg-white text-xs focus:outline-none focus:border-slate-400"
          />
        </div>
        <select
          value={category}
          onChange={(event) =>
            setCategory(event.target.value as TicketCategory | "all")
          }
          className="bg-white border border-slate-200 rounded-xl px-3 py-2.5 text-[10px] font-bold text-slate-600 focus:outline-none"
        >
          <option value="all">همه دسته‌ها</option>
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

      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
        {filtered.map((article) => (
          <Link
            href={`/knowledge-base/${article.id}`}
            key={article.id}
            className="panel p-5 flex flex-col hover:border-slate-300 transition-colors group"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="w-10 h-10 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
                <BookOpen className="w-4.5 h-4.5" />
              </div>
              <span className="text-[9px] font-bold text-slate-500 bg-slate-100 px-2 py-1 rounded-lg">
                {article.categoryLabelFa}
              </span>
            </div>
            <h2 className="text-xs font-black text-slate-800 group-hover:text-blue-600 transition-colors leading-6 mt-4">
              {article.title}
            </h2>
            <p className="text-[11px] text-slate-500 leading-6 mt-2 line-clamp-3 flex-1">
              {article.summary}
            </p>
            <div className="flex flex-wrap gap-1.5 mt-4">
              {article.tags.slice(0, 3).map((tag) => (
                <span
                  key={tag}
                  className="text-[9px] text-slate-500 bg-slate-50 border border-slate-100 px-2 py-1 rounded-lg"
                >
                  {tag}
                </span>
              ))}
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[9px] text-slate-400">
              <span>{article.author}</span>
              <span>بروزرسانی {article.updatedAt}</span>
            </div>
          </Link>
        ))}
      </div>

      {!filtered.length && (
        <div className="panel">
          <EmptyState
            title="مقاله‌ای پیدا نشد"
            description="API پایگاه دانش هنوز در بک‌اند فعال نشده است."
          />
        </div>
      )}
    </div>
  );
}
