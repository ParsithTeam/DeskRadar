"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import type { Role, User } from "@/types";

interface Account extends User {
  password: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => string | null;
  register: (
    name: string,
    email: string,
    password: string,
  ) => string | null;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);
const CURRENT_USER_KEY = "deskradar_user_v2";

function readSavedUser(): User | null {
  try {
    const savedUser = window.localStorage?.getItem(CURRENT_USER_KEY);
    if (!savedUser) return null;
    const parsed = JSON.parse(savedUser) as User;
    return parsed.id && parsed.email && parsed.role ? parsed : null;
  } catch {
    return null;
  }
}

function persistUser(user: User | null) {
  try {
    if (user) {
      window.localStorage?.setItem(CURRENT_USER_KEY, JSON.stringify(user));
    } else {
      window.localStorage?.removeItem(CURRENT_USER_KEY);
    }
  } catch {
    // Authentication still works for the current tab when storage is unavailable.
  }
}

const temporaryAccounts: Account[] = [
  {
    id: "admin-1",
    name: "مدیر پشتیبانی",
    email: "admin@deskino.ir",
    password: "admin123",
    role: "admin",
  },
  {
    id: "user-1",
    name: "حسین احمدی",
    email: "user@deskino.ir",
    password: "user123",
    role: "user",
  },
];

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setUser(readSavedUser());
      setIsLoading(false);
    }, 0);
    return () => window.clearTimeout(timer);
  }, []);

  const login = (email: string, password: string) => {
    const normalizedEmail = email.trim().toLowerCase();
    const account = temporaryAccounts.find(
      (item) =>
        item.email.toLowerCase() === normalizedEmail &&
        item.password === password,
    );

    if (!account) {
      return "ایمیل یا رمز عبور صحیح نیست.";
    }

    const authenticatedUser: User = {
      id: account.id,
      name: account.name,
      email: account.email,
      role: account.role as Role,
    };
    setUser(authenticatedUser);
    persistUser(authenticatedUser);
    router.replace("/");
    return null;
  };

  const register = (name: string, email: string, password: string) => {
    const cleanName = name.trim();
    const normalizedEmail = email.trim().toLowerCase();
    if (cleanName.length < 3) return "نام و نام خانوادگی را کامل وارد کنید.";
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalizedEmail)) {
      return "یک ایمیل معتبر وارد کنید.";
    }
    if (password.length < 6) return "رمز عبور باید حداقل ۶ کاراکتر باشد.";

    return "API ثبت‌نام هنوز در بک‌اند پیاده‌سازی نشده است.";
  };

  const logout = () => {
    setUser(null);
    persistUser(null);
    router.replace("/login");
  };

  return (
    <AuthContext.Provider
      value={{ user, isLoading, login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth باید داخل AuthProvider استفاده شود");
  }
  return context;
}
