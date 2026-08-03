"use client";

import { CheckCircle2, Send } from "lucide-react";
import { useState } from "react";
import { useAppData } from "@/lib/app-context";
import { useAuth } from "@/lib/auth-context";
import { EscalationStatusBadge } from "@/components/status-badge";
import type { Escalation } from "@/types";

export default function EscalationConversation({
  escalation,
  showHeader = true,
}: {
  escalation: Escalation;
  showHeader?: boolean;
}) {
  const { user } = useAuth();
  const { sendEscalationMessage } = useAppData();
  const [message, setMessage] = useState("");

  if (!user) return null;

  const submitMessage = (event: React.FormEvent) => {
    event.preventDefault();
    if (!message.trim() || escalation.status === "resolved") return;
    sendEscalationMessage(escalation.id, message, user);
    setMessage("");
  };

  return (
    <section className="panel overflow-hidden" id="conversation">
      {showHeader && (
        <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between gap-3">
          <div>
            <h3 className="text-xs font-black text-slate-800">
              گفتگوی مستقیم با پشتیبانی
            </h3>
            <p className="text-[10px] text-slate-400 mt-1">
              پاسخ‌ها داخل همین پرونده ذخیره می‌شوند.
            </p>
          </div>
          <EscalationStatusBadge status={escalation.status} />
        </div>
      )}

      <div className="p-4 sm:p-5 bg-slate-50/40 min-h-64 max-h-[420px] overflow-y-auto flex flex-col gap-3">
        {escalation.messages.map((item) => {
          const isMine = item.senderId === user.id;
          return (
            <div
              key={item.id}
              className={`max-w-[85%] sm:max-w-[72%] ${
                isMine ? "self-start" : "self-end"
              }`}
            >
              <div
                className={`rounded-2xl px-4 py-3 border ${
                  isMine
                    ? "bg-slate-900 text-white border-slate-900 rounded-tr-md"
                    : "bg-white text-slate-700 border-slate-200 rounded-tl-md"
                }`}
              >
                <p className="text-[11px] leading-6">{item.text}</p>
              </div>
              <div
                className={`flex items-center gap-2 mt-1.5 px-1 text-[9px] text-slate-400 ${
                  isMine ? "" : "justify-end"
                }`}
              >
                <span>{item.senderName}</span>
                <span>·</span>
                <span>{item.createdAt}</span>
              </div>
            </div>
          );
        })}
      </div>

      {escalation.status === "resolved" ? (
        <div className="px-5 py-4 border-t border-slate-100 flex items-center gap-2 text-[11px] font-bold text-emerald-700 bg-emerald-50/40">
          <CheckCircle2 className="w-4 h-4" />
          این گفتگو بسته شده و تیکت حل‌شده علامت خورده است.
        </div>
      ) : (
        <form
          onSubmit={submitMessage}
          className="p-3 sm:p-4 border-t border-slate-100 flex items-end gap-2"
        >
          <textarea
            rows={2}
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            placeholder={
              user.role === "admin"
                ? "پاسخ یا راهنمایی کارشناس..."
                : "پیام خود را برای کارشناس بنویسید..."
            }
            className="form-input text-xs leading-6 resize-none flex-1"
          />
          <button
            type="submit"
            disabled={!message.trim()}
            aria-label="ارسال پیام"
            className="w-11 h-11 rounded-xl bg-slate-900 text-white flex items-center justify-center disabled:opacity-40 cursor-pointer"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      )}
    </section>
  );
}

