import type { Alert } from "@/types";

interface AlertStreamOptions {
  onAlert: (alert: Alert) => void;
}

export function connectAlertStream({ onAlert }: AlertStreamOptions) {
  const wsUrl = process.env.NEXT_PUBLIC_ALERTS_WS_URL;
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;
  let socket: WebSocket | null = null;
  let pollingTimer: number | null = null;
  let stopped = false;
  const seenIds = new Set<string>();

  const startPolling = () => {
    if (!apiUrl || pollingTimer || stopped) return;
    pollingTimer = window.setInterval(async () => {
      try {
        const response = await fetch(`${apiUrl}/alerts?unread=true`);
        if (!response.ok) return;
        const alerts = (await response.json()) as Alert[];
        alerts.forEach((alert) => {
          if (!seenIds.has(alert.id)) {
            seenIds.add(alert.id);
            onAlert(alert);
          }
        });
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
          const alert = JSON.parse(event.data) as Alert;
          if (alert.id && !seenIds.has(alert.id)) {
            seenIds.add(alert.id);
            onAlert(alert);
          }
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

