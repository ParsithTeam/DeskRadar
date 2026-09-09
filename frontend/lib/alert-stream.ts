import type { Alert } from "@/types";
import { mapAlertFromApi } from "@/lib/api-client";

interface AlertStreamOptions {
  onAlert: (alert: Alert) => void;
}

export function connectAlertStream({ onAlert }: AlertStreamOptions) {
  const wsUrl = process.env.NEXT_PUBLIC_ALERTS_WS_URL;
  let socket: WebSocket | null = null;
  let pollingTimer: number | null = null;
  let stopped = false;
  const seenVersions = new Map<string, string>();

  const emitIfChanged = (alert: Alert) => {
    if (!alert.id) return;
    const version = JSON.stringify(alert);
    if (seenVersions.get(alert.id) === version) return;
    seenVersions.set(alert.id, version);
    onAlert(alert);
  };

  const startPolling = () => {
    if (pollingTimer || stopped) return;
    pollingTimer = window.setInterval(async () => {
      try {
        const response = await fetch("/backend-api/alerts", {
          cache: "no-store",
        });
        if (!response.ok) return;
        const alerts = (await response.json()) as unknown[];
        alerts.map(mapAlertFromApi).forEach(emitIfChanged);
      } catch {
        // Polling will try again on the next interval.
      }
    }, 15000);
  };

  if (wsUrl) {
    try {
      socket = new WebSocket(wsUrl);
      socket.addEventListener("message", (event) => {
        try {
          const alert = mapAlertFromApi(JSON.parse(event.data));
          emitIfChanged(alert);
        } catch {
          // Ignore malformed messages and keep the stream alive.
        }
      });
      socket.addEventListener("close", startPolling);
      socket.addEventListener("error", () => {
        socket?.close();
        startPolling();
      });
    } catch {
      startPolling();
    }
  } else {
    startPolling();
  }

  return () => {
    stopped = true;
    socket?.close();
    if (pollingTimer) window.clearInterval(pollingTimer);
  };
}
