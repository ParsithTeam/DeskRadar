"use client";

import Link from "next/link";
import { BellRing, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useAppData } from "@/lib/app-context";
import { useAuth } from "@/lib/auth-context";
import { connectAlertStream } from "@/lib/alert-stream";
import type { Alert } from "@/types";

export default function LiveAlertToast() {
  const { user } = useAuth();
  const { alerts, ingestAlert, markAlertRead } = useAppData();
  const firstAlertId = useRef<string | null>(null);
  const [visibleAlert, setVisibleAlert] = useState<Alert | null>(null);

  useEffect(() => {
    if (user?.role !== "admin") return;
    return connectAlertStream({ onAlert: ingestAlert });
  }, [ingestAlert, user?.role]);

  useEffect(() => {
    if (!alerts[0]) return;
    if (firstAlertId.current === null) {
      firstAlertId.current = alerts[0].id;
      return;
    }
    if (alerts[0].id !== firstAlertId.current) {
      firstAlertId.current = alerts[0].id;
      setVisibleAlert(alerts[0]);
    }
  }, [alerts]);

  useEffect(() => {
    if (!visibleAlert) return;
    const timer = window.setTimeout(() => setVisibleAlert(null), 6500);
    return () => window.clearTimeout(timer);
  }, [visibleAlert]);

  if (!visibleAlert || user?.role !== "admin") return null;

  const content = (
    <>
      <div className="w-9 h-9 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center shrink-0">
        <BellRing className="w-4 h-4" />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-xs font-black text-slate-900">
          {visibleAlert.title}
        </p>
        <p className="text-[11px] text-slate-500 mt-1 leading-5">
          {visibleAlert.message}
        </p>
      </div>
    </>
  );

  return (
    <div className="fixed top-20 left-4 sm:left-6 z-50 w-[min(360px,calc(100vw-32px))] panel p-4 flex items-start gap-3 animate-toast-in shadow-[0_16px_45px_rgba(15,23,42,0.14)]">
      {visibleAlert.href ? (
        <Link
          href={visibleAlert.href}
          onClick={() => void markAlertRead(visibleAlert.id, user).catch(() => undefined)}
          className="flex items-start gap-3 flex-1"
        >
          {content}
        </Link>
      ) : (
        <div className="flex items-start gap-3 flex-1">{content}</div>
      )}
      <button
        type="button"
        onClick={() => setVisibleAlert(null)}
        aria-label="بستن هشدار"
        className="text-slate-300 hover:text-slate-600 cursor-pointer"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
}
