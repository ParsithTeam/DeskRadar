import { cloneSeedSnapshot } from "@/lib/mock-data";
import type { AppSnapshot } from "@/types";

const STORAGE_KEY = "deskradar_app_data_v2";

function isSnapshot(value: unknown): value is AppSnapshot {
  if (!value || typeof value !== "object") return false;
  const snapshot = value as Partial<AppSnapshot>;
  return (
    Array.isArray(snapshot.tickets) &&
    Array.isArray(snapshot.escalations) &&
    Array.isArray(snapshot.incidents) &&
    Array.isArray(snapshot.articles) &&
    Array.isArray(snapshot.alerts)
  );
}

export const apiClient = {
  getSnapshot(): AppSnapshot {
    if (typeof window === "undefined") return cloneSeedSnapshot();

    const saved = window.localStorage.getItem(STORAGE_KEY);
    if (!saved) return cloneSeedSnapshot();

    try {
      const parsed: unknown = JSON.parse(saved);
      return isSnapshot(parsed) ? parsed : cloneSeedSnapshot();
    } catch {
      return cloneSeedSnapshot();
    }
  },

  saveSnapshot(snapshot: AppSnapshot) {
    if (typeof window === "undefined") return;
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(snapshot));
  },

  resetSnapshot() {
    if (typeof window !== "undefined") {
      window.localStorage.removeItem(STORAGE_KEY);
    }
    return cloneSeedSnapshot();
  },
};

