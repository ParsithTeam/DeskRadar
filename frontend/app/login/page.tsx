"use client";

import Image from "next/image";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

export default function LoginPage() {
  const { user, isLoading, login, register } = useAuth();
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isLoading && user) {
      router.replace("/");
    }
  }, [isLoading, router, user]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    const message =
      mode === "login"
        ? login(email, password)
        : register(name, email, password);
    if (message) setError(message);
  };

  const handleDemoLogin = (role: "admin" | "user") => {
    setError("");
    const message = login(
      role === "admin" ? "admin@deskino.ir" : "user@deskino.ir",
      role === "admin" ? "admin123" : "user123",
    );
    if (message) setError(message);
  };

  return (
    <main className="min-h-screen bg-[#f8fafc] flex items-center justify-center p-4 sm:p-6">
      <div className="w-full max-w-[820px] bg-white rounded-2xl border border-slate-200/60 shadow-[0_12px_45px_rgba(15,23,42,0.05)] overflow-hidden grid grid-cols-1 md:grid-cols-[0.9fr_1.1fr]">
        <section className="bg-slate-900 text-white p-8 sm:p-10 flex flex-col justify-between min-h-[250px] md:min-h-[540px] relative overflow-hidden">
          <div className="absolute -top-20 -left-20 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl" />
          <div className="relative z-10">
            <div className="bg-white rounded-xl px-4 py-2.5 inline-flex">
              <Image
                src="/deskino-logo.svg"
                alt="لوگو دسکینو"
                width={142}
                height={38}
                priority
              />
            </div>
            <p className="text-[11px] text-slate-400 mt-4">
              میز کار هوشمند پشتیبانی سازمان
            </p>
          </div>

          <div className="relative z-10 space-y-4 mt-10 md:mt-0">
            <h1 className="text-2xl sm:text-2xl font-black leading-relaxed">
               ثبت مشکل تا حل مشکل
            </h1>
            <p className="text-xs leading-7 text-slate-400 max-w-sm">
              تیکت خود را ثبت کنید، تحلیل و پاسخ پیشنهادی هوش مصنوعی را ببینید
              و اگر مسئله حل نشد، مستقیماً با تیم پشتیبانی گفتگو کنید.
            </p>
          </div>

          <p className="relative z-10 text-[10px] text-slate-600 hidden md:block">
            ۱.۰
          </p>
        </section>

        <section className="p-7 sm:p-10 flex flex-col justify-center">
          <div className="space-y-1.5 mb-7">
            <h2 className="text-xl font-black text-slate-900">
              {mode === "login" ? "ورود به رادار" : "ساخت حساب کاربری"}
            </h2>
            <p className="text-xs text-slate-400">
              {mode === "login"
                ? "با ایمیل سازمانی خود وارد شوید."
                : "حساب‌های جدید با نقش کاربر عادی ساخته می‌شوند."}
            </p>
          </div>

          <div className="bg-slate-100/80 p-1 rounded-xl grid grid-cols-2 mb-6 text-xs">
            <button
              type="button"
              onClick={() => {
                setMode("login");
                setError("");
              }}
              className={`py-2 rounded-lg font-bold transition-all cursor-pointer ${
                mode === "login"
                  ? "bg-white text-slate-900 shadow-sm"
                  : "text-slate-400"
              }`}
            >
              ورود
            </button>
            <button
              type="button"
              onClick={() => {
                setMode("register");
                setError("");
              }}
              className={`py-2 rounded-lg font-bold transition-all cursor-pointer ${
                mode === "register"
                  ? "bg-white text-slate-900 shadow-sm"
                  : "text-slate-400"
              }`}
            >
              ثبت‌نام
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4 text-xs">
            {mode === "register" && (
              <div className="space-y-2">
                <label htmlFor="name" className="block font-bold text-slate-600">
                  نام و نام خانوادگی
                </label>
                <input
                  id="name"
                  type="text"
                  required
                  autoComplete="name"
                  placeholder="مثلاً حسین احمدی"
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                  className="form-input"
                />
              </div>
            )}

            <div className="space-y-2">
              <label htmlFor="email" className="block font-bold text-slate-600">
                ایمیل
              </label>
              <input
                id="email"
                type="email"
                required
                dir="ltr"
                autoComplete="email"
                placeholder="name@company.ir"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                className="form-input text-left"
              />
            </div>

            <div className="space-y-2">
              <label
                htmlFor="password"
                className="block font-bold text-slate-600"
              >
                رمز عبور
              </label>
              <input
                id="password"
                type="password"
                required
                dir="ltr"
                minLength={6}
                autoComplete={
                  mode === "login" ? "current-password" : "new-password"
                }
                placeholder="حداقل ۶ کاراکتر"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="form-input text-left"
              />
            </div>

            {error && (
              <p
                role="alert"
                className="text-[11px] font-bold text-rose-600 bg-rose-50 border border-rose-100 px-3 py-2 rounded-xl"
              >
                {error}
              </p>
            )}

            <button
              type="submit"
              className="w-full bg-slate-900 text-white font-bold py-3 rounded-xl hover:bg-slate-800 transition-colors shadow-sm cursor-pointer text-xs"
            >
              {mode === "login" ? "ورود به سیستم" : "ثبت‌نام و ورود"}
            </button>
          </form>

          {mode === "login" && (
            <div className="mt-6 pt-5 border-t border-slate-100">
              <p className="text-[10px] text-slate-400 mb-3 text-center">
                ورود موقت برای بررسی نقش‌ها تا آماده‌شدن Auth بک‌اند
              </p>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => handleDemoLogin("user")}
                  className="py-2.5 rounded-xl border border-slate-200 text-[11px] font-bold text-slate-600 hover:bg-slate-50 transition-colors cursor-pointer"
                >
                  ورود کاربر
                </button>
                <button
                  type="button"
                  onClick={() => handleDemoLogin("admin")}
                  className="py-2.5 rounded-xl border border-slate-200 text-[11px] font-bold text-slate-600 hover:bg-slate-50 transition-colors cursor-pointer"
                >
                  ورود ادمین
                </button>
              </div>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
