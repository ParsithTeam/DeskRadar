"use client";

import { RotateCcw, Save } from "lucide-react";
import { useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { useAppData } from "@/lib/app-context";
import { AccessDenied } from "@/components/loading-state";

export default function SettingsPage() {
  const { user } = useAuth();
  const { resetDemoData } = useAppData();
  const [saved, setSaved] = useState(false);
  const [notifications, setNotifications] = useState({
    critical: true,
    escalation: true,
    sla: true,
  });

  if (!user || user.role !== "admin") return <AccessDenied />;

  const save = () => {
    setSaved(true);
    window.setTimeout(() => setSaved(false), 1800);
  };

  return (
    <div className="max-w-3xl space-y-6">
      <div className="space-y-1.5">
        <h1 className="page-title">تنظیمات</h1>
        <p className="page-description">
          ترجیحات اعلان و داده‌های نسخه نمایشی فرانت‌اند
        </p>
      </div>

      <section className="panel p-5 sm:p-6 space-y-5">
        <div>
          <h2 className="text-sm font-black text-slate-800">
            اعلان‌های زنده
          </h2>
          <p className="text-[10px] text-slate-400 mt-1">
            مشخص کنید چه رخدادهایی به‌صورت Toast نمایش داده شوند.
          </p>
        </div>
        <div className="divide-y divide-slate-100">
          <SettingToggle
            label="رخدادهای بحرانی"
            description="تشخیص خوشه تیکت با شدت بحرانی"
            checked={notifications.critical}
            onChange={(checked) =>
              setNotifications((current) => ({
                ...current,
                critical: checked,
              }))
            }
          />
          <SettingToggle
            label="ارجاع جدید کاربر"
            description="زمانی که پاسخ AI مشکل کاربر را حل نکرده است"
            checked={notifications.escalation}
            onChange={(checked) =>
              setNotifications((current) => ({
                ...current,
                escalation: checked,
              }))
            }
          />
          <SettingToggle
            label="ریسک عبور از SLA"
            description="نزدیک شدن زمان پاسخ‌گویی به آستانه توافق‌شده"
            checked={notifications.sla}
            onChange={(checked) =>
              setNotifications((current) => ({ ...current, sla: checked }))
            }
          />
        </div>
        <button
          type="button"
          onClick={save}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-900 text-white text-[10px] font-bold cursor-pointer"
        >
          <Save className="w-4 h-4" />
          {saved ? "ذخیره شد" : "ذخیره تنظیمات"}
        </button>
      </section>

      <section className="panel p-5 sm:p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-sm font-black text-slate-800">
            بازنشانی داده‌های نمایشی
          </h2>
          <p className="text-[10px] text-slate-400 mt-1 leading-5">
            تمام تغییرات محلی، گفتگوها و تیکت‌های ساخته‌شده به داده اولیه
            برمی‌گردند.
          </p>
        </div>
        <button
          type="button"
          onClick={resetDemoData}
          className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-rose-50 text-rose-700 border border-rose-100 text-[10px] font-bold cursor-pointer shrink-0"
        >
          <RotateCcw className="w-4 h-4" />
          بازنشانی داده‌ها
        </button>
      </section>
    </div>
  );
}

function SettingToggle({
  label,
  description,
  checked,
  onChange,
}: {
  label: string;
  description: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}) {
  return (
    <label className="py-4 flex items-center justify-between gap-5 cursor-pointer">
      <div>
        <span className="text-xs font-bold text-slate-700 block">{label}</span>
        <span className="text-[10px] text-slate-400 mt-1 block">
          {description}
        </span>
      </div>
      <input
        type="checkbox"
        checked={checked}
        onChange={(event) => onChange(event.target.checked)}
        className="w-4 h-4 accent-slate-900"
      />
    </label>
  );
}
