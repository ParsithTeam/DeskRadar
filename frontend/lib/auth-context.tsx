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
const ACCOUNTS_KEY = "deskradar_accounts_v2";

const demoAccounts: Account[] = [
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

function readAccounts() {
  const saved = window.localStorage.getItem(ACCOUNTS_KEY);
  if (!saved) return demoAccounts;
  try {
    const accounts = JSON.parse(saved) as Account[];
    const registered = accounts.filter(
      (account) => !demoAccounts.some((demo) => demo.email === account.email),
    );
    return [...demoAccounts, ...registered];
  } catch {
    return demoAccounts;
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const timer = window.setTimeout(() => {
      const savedUser = window.localStorage.getItem(CURRENT_USER_KEY);
      if (savedUser) {
        try {
          const parsed = JSON.parse(savedUser) as User;
          if (parsed.id && parsed.email && parsed.role) {
            setUser(parsed);
          }
        } catch {
          window.localStorage.removeItem(CURRENT_USER_KEY);
        }
      }
      setIsLoading(false);
    }, 0);
    return () => window.clearTimeout(timer);
  }, []);

  const login = (email: string, password: string) => {
    const normalizedEmail = email.trim().toLowerCase();
    const account = readAccounts().find(
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
    window.localStorage.setItem(
      CURRENT_USER_KEY,
      JSON.stringify(authenticatedUser),
    );
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

    const accounts = readAccounts();
    if (accounts.some((account) => account.email === normalizedEmail)) {
      return "این ایمیل قبلاً ثبت شده است.";
    }

    const account: Account = {
      id: `user-${Date.now()}`,
      name: cleanName,
      email: normalizedEmail,
      password,
      role: "user",
    };
    const updatedAccounts = [...accounts, account];
    window.localStorage.setItem(ACCOUNTS_KEY, JSON.stringify(updatedAccounts));
    const authenticatedUser: User = {
      id: account.id,
      name: account.name,
      email: account.email,
      role: account.role,
    };
    setUser(authenticatedUser);
    window.localStorage.setItem(
      CURRENT_USER_KEY,
      JSON.stringify(authenticatedUser),
    );
    router.replace("/");
    return null;
  };

  const logout = () => {
    setUser(null);
    window.localStorage.removeItem(CURRENT_USER_KEY);
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
