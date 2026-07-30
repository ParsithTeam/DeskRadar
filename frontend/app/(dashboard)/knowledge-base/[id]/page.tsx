"use client";

import Link from "next/link";
import { ArrowRight, BookOpen, CalendarDays, UserRound } from "lucide-react";
import { useParams } from "next/navigation";
import { useAppData } from "@/lib/app-context";
import { EmptyState } from "@/components/loading-state";

export default function ArticleDetailPage() {
  const params = useParams<{ id: string }>();
  const { articles } = useAppData();
  const article = articles.find((item) => item.id === Number(params.id));

  if (!article) {
    return (
      <div className="panel">
        <EmptyState
          title="مقاله پیدا نشد"
          description="شناسه مقاله معتبر نیست یا این محتوا حذف شده است."
        />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Link
        href="/knowledge-base"
        className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-400 hover:text-slate-700"
      >
        <ArrowRight className="w-4 h-4" />
        بازگشت به پایگاه دانش
      </Link>

      <article className="panel overflow-hidden">
        <header className="p-6 sm:p-8 border-b border-slate-100">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
              <BookOpen className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[10px] font-bold text-blue-600">
                {article.categoryLabelFa}
              </span>
              <h1 className="text-xl sm:text-2xl font-black text-slate-900 leading-relaxed mt-1.5">
                {article.title}
              </h1>
              <p className="text-xs text-slate-500 leading-7 mt-3">
                {article.summary}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-x-5 gap-y-2 mt-6 text-[10px] text-slate-400">
            <span className="inline-flex items-center gap-1.5">
              <UserRound className="w-3.5 h-3.5" />
              {article.author}
            </span>
            <span className="inline-flex items-center gap-1.5">
              <CalendarDays className="w-3.5 h-3.5" />
              آخرین بروزرسانی {article.updatedAt}
            </span>
          </div>
        </header>

        <div className="p-6 sm:p-8">
          <ArticleContent content={article.content} />
        </div>

        <footer className="px-6 sm:px-8 py-5 border-t border-slate-100 bg-slate-50/40 flex flex-wrap gap-2">
          {article.tags.map((tag) => (
            <span
              key={tag}
              className="text-[10px] font-bold text-slate-500 bg-white border border-slate-200 px-2.5 py-1 rounded-lg"
            >
              {tag}
            </span>
          ))}
        </footer>
      </article>
    </div>
  );
}

function ArticleContent({ content }: { content: string }) {
  return (
    <div className="space-y-3 text-xs text-slate-600 leading-8">
      {content.split("\n").map((line, index) => {
        const trimmed = line.trim();
        if (!trimmed) return <div key={index} className="h-1" />;
        if (trimmed.startsWith("## ")) {
          return (
            <h2
              key={index}
              className="text-sm font-black text-slate-900 pt-4 pb-1"
            >
              {trimmed.slice(3)}
            </h2>
          );
        }
        if (/^\d+\.\s/.test(trimmed)) {
          const [number, ...rest] = trimmed.split(/\.\s/);
          return (
            <div key={index} className="flex items-start gap-3">
              <span className="w-6 h-6 rounded-lg bg-slate-100 text-slate-700 flex items-center justify-center text-[10px] font-black shrink-0 mt-0.5">
                {Number(number).toLocaleString("fa-IR")}
              </span>
              <p>{rest.join(". ")}</p>
            </div>
          );
        }
        return <p key={index}>{trimmed}</p>;
      })}
    </div>
  );
}
