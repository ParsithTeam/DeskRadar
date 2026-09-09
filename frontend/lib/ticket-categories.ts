import type { TicketCategory } from "@/types";

export const categoryLabels: Record<TicketCategory, string> = {
  vpn: "مشکلات VPN",
  email: "سرویس ایمیل",
  network: "شبکه",
  printer: "پرینتر",
  account: "حساب کاربری",
  permission: "دسترسی و مجوز",
  software: "نرم‌افزار",
  hardware: "سخت‌افزار",
  unknown: "نامشخص",
};
