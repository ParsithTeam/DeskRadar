"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { apiClient } from "@/lib/api-client";
import {
  buildMockAnalysis,
  categoryLabels,
  cloneSeedSnapshot,
} from "@/lib/mock-data";
import type {
  Alert,
  AlertSeverity,
  AppSnapshot,
  Escalation,
  IncidentStatus,
  KnowledgeArticle,
  Role,
  Ticket,
  TicketCreateInput,
  TicketStatus,
  User,
} from "@/types";

interface ImportedTicket {
  title: string;
  description: string;
  department: string;
  createdAt?: string;
}

interface AppContextValue extends AppSnapshot {
  isReady: boolean;
  createTicket: (input: TicketCreateInput) => number;
  importTickets: (rows: ImportedTicket[], actor: User) => number;
  analyzeTicket: (ticketId: number) => void;
  updateTicketStatus: (ticketId: number, status: TicketStatus) => void;
  escalateTicket: (
    ticketId: number,
    reason: string,
    actor: User,
  ) => string | null;
  sendEscalationMessage: (
    escalationId: string,
    text: string,
    actor: User,
  ) => void;
  updateEscalationStatus: (
    escalationId: string,
    status: Escalation["status"],
    admin?: User,
  ) => void;
  updateIncidentStatus: (incidentId: number, status: IncidentStatus) => void;
  createArticle: (
    article: Omit<KnowledgeArticle, "id" | "updatedAt">,
  ) => number;
  markAlertRead: (alertId: string, admin: User) => void;
  ingestAlert: (alert: Alert) => void;
  emitDemoAlert: () => void;
  resetDemoData: () => void;
}

const AppContext = createContext<AppContextValue | undefined>(undefined);

function nowFa() {
  return new Intl.DateTimeFormat("fa-IR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date());
}

function shortTimeFa() {
  return new Intl.DateTimeFormat("fa-IR", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date());
}

function makeAlert(
  title: string,
  message: string,
  severity: AlertSeverity,
  type: Alert["type"],
  href?: string,
): Alert {
  return {
    id: `alert-${Date.now()}-${Math.random().toString(16).slice(2)}`,
    title,
    message,
    severity,
    type,
    createdAt: "همین حالا",
    read: false,
    href,
  };
}

export function AppProvider({ children }: { children: React.ReactNode }) {
  const seed = useMemo(() => cloneSeedSnapshot(), []);
  const [tickets, setTickets] = useState(seed.tickets);
  const [escalations, setEscalations] = useState(seed.escalations);
  const [incidents, setIncidents] = useState(seed.incidents);
  const [articles, setArticles] = useState(seed.articles);
  const [alerts, setAlerts] = useState(seed.alerts);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      const snapshot = apiClient.getSnapshot();
      setTickets(snapshot.tickets);
      setEscalations(snapshot.escalations);
      setIncidents(snapshot.incidents);
      setArticles(snapshot.articles);
      setAlerts(snapshot.alerts);
      setIsReady(true);
    }, 0);
    return () => window.clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (!isReady) return;
    apiClient.saveSnapshot({
      tickets,
      escalations,
      incidents,
      articles,
      alerts,
    });
  }, [alerts, articles, escalations, incidents, isReady, tickets]);

  const finishAnalysis = useCallback((ticketId: number) => {
    setTickets((current) =>
      current.map((ticket) => {
        if (ticket.id !== ticketId) return ticket;
        const analysis = buildMockAnalysis(ticket.title, ticket.description);
        return {
          ...ticket,
          category: analysis.category,
          categoryLabelFa: analysis.categoryLabelFa,
          urgency: analysis.urgency,
          confidence: analysis.confidence,
          analysis,
          analysisStatus: "complete",
          updatedAt: nowFa(),
        };
      }),
    );

  }, []);

  const analyzeTicket = useCallback(
    (ticketId: number) => {
      setTickets((current) =>
        current.map((ticket) =>
          ticket.id === ticketId
            ? { ...ticket, analysisStatus: "pending", updatedAt: nowFa() }
            : ticket,
        ),
      );
      window.setTimeout(() => finishAnalysis(ticketId), 700);
    },
    [finishAnalysis],
  );

  const createTicket = useCallback(
    (input: TicketCreateInput) => {
      const id =
        tickets.reduce((largest, ticket) => Math.max(largest, ticket.id), 100) +
        1;
      const createdAt = nowFa();
      const newTicket: Ticket = {
        id,
        ...input,
        category: "account",
        categoryLabelFa: "در حال تشخیص",
        urgency: "low",
        status: "open",
        analysisStatus: "pending",
        confidence: 0,
        createdAt,
        updatedAt: createdAt,
        analysis: null,
      };
      setTickets((current) => [newTicket, ...current]);
      window.setTimeout(() => finishAnalysis(id), 900);
      return id;
    },
    [finishAnalysis, tickets],
  );

  const importTickets = useCallback(
    (rows: ImportedTicket[], actor: User) => {
      const firstId =
        tickets.reduce((largest, ticket) => Math.max(largest, ticket.id), 100) +
        1;
      const imported = rows.map<Ticket>((row, index) => {
        const analysis = buildMockAnalysis(row.title, row.description);
        return {
          id: firstId + index,
          title: row.title,
          description: row.description,
          department: row.department,
          requesterId: actor.id,
          requesterName: actor.name,
          category: analysis.category,
          categoryLabelFa: categoryLabels[analysis.category],
          urgency: analysis.urgency,
          status: "open",
          analysisStatus: "complete",
          confidence: analysis.confidence,
          createdAt: row.createdAt || nowFa(),
          updatedAt: nowFa(),
          analysis,
        };
      });
      setTickets((current) => [...imported, ...current]);
      return imported.length;
    },
    [tickets],
  );

  const updateTicketStatus = useCallback(
    (ticketId: number, status: TicketStatus) => {
      setTickets((current) =>
        current.map((ticket) =>
          ticket.id === ticketId
            ? { ...ticket, status, updatedAt: nowFa() }
            : ticket,
        ),
      );
    },
    [],
  );

  const escalateTicket = useCallback(
    (ticketId: number, reason: string, actor: User) => {
      const existing = escalations.find(
        (item) => item.ticketId === ticketId && item.status !== "resolved",
      );
      if (existing) return existing.id;

      const escalationId = `esc-${ticketId}-${Date.now()}`;
      const createdAt = nowFa();
      const escalation: Escalation = {
        id: escalationId,
        ticketId,
        requesterId: actor.id,
        requesterName: actor.name,
        reason,
        status: "waiting",
        createdAt,
        updatedAt: createdAt,
        messages: [
          {
            id: `msg-${Date.now()}`,
            senderId: actor.id,
            senderName: actor.name,
            senderRole: actor.role,
            text: reason,
            createdAt: shortTimeFa(),
          },
        ],
      };

      setEscalations((current) => [escalation, ...current]);
      setTickets((current) =>
        current.map((ticket) =>
          ticket.id === ticketId
            ? { ...ticket, status: "escalated", updatedAt: createdAt }
            : ticket,
        ),
      );
      setAlerts((current) => [
        makeAlert(
          "ارجاع جدید به کارشناس",
          `${actor.name} تیکت #${ticketId} را برای بررسی انسانی ارجاع داد.`,
          "high",
          "escalation",
          `/admin/escalated/${escalationId}`,
        ),
        ...current,
      ]);
      return escalationId;
    },
    [escalations],
  );

  const sendEscalationMessage = useCallback(
    (escalationId: string, text: string, actor: User) => {
      const cleaned = text.trim();
      if (!cleaned) return;
      setEscalations((current) =>
        current.map((escalation) =>
          escalation.id === escalationId
            ? {
                ...escalation,
                status:
                  escalation.status === "waiting" && actor.role === "admin"
                    ? "active"
                    : escalation.status,
                assignedAdminId:
                  actor.role === "admin"
                    ? actor.id
                    : escalation.assignedAdminId,
                assignedAdminName:
                  actor.role === "admin"
                    ? actor.name
                    : escalation.assignedAdminName,
                updatedAt: nowFa(),
                messages: [
                  ...escalation.messages,
                  {
                    id: `msg-${Date.now()}-${Math.random()
                      .toString(16)
                      .slice(2)}`,
                    senderId: actor.id,
                    senderName: actor.name,
                    senderRole: actor.role as Role,
                    text: cleaned,
                    createdAt: shortTimeFa(),
                  },
                ],
              }
            : escalation,
        ),
      );
    },
    [],
  );

  const updateEscalationStatus = useCallback(
    (
      escalationId: string,
      status: Escalation["status"],
      admin?: User,
    ) => {
      const ticketId = escalations.find(
        (escalation) => escalation.id === escalationId,
      )?.ticketId;
      setEscalations((current) =>
        current.map((escalation) => {
          if (escalation.id !== escalationId) return escalation;
          return {
            ...escalation,
            status,
            assignedAdminId: admin?.id ?? escalation.assignedAdminId,
            assignedAdminName: admin?.name ?? escalation.assignedAdminName,
            updatedAt: nowFa(),
          };
        }),
      );
      if (status === "resolved" && ticketId) {
        updateTicketStatus(ticketId, "resolved");
      }
    },
    [escalations, updateTicketStatus],
  );

  const updateIncidentStatus = useCallback(
    (incidentId: number, status: IncidentStatus) => {
      setIncidents((current) =>
        current.map((incident) =>
          incident.id === incidentId
            ? {
                ...incident,
                status,
                resolvedAt:
                  status === "resolved" ? nowFa() : incident.resolvedAt,
              }
            : incident,
        ),
      );
    },
    [],
  );

  const createArticle = useCallback(
    (article: Omit<KnowledgeArticle, "id" | "updatedAt">) => {
      const id =
        articles.reduce(
          (largest, current) => Math.max(largest, current.id),
          10,
        ) + 1;
      setArticles((current) => [
        { ...article, id, updatedAt: nowFa() },
        ...current,
      ]);
      return id;
    },
    [articles],
  );

  const markAlertRead = useCallback((alertId: string, admin: User) => {
    if (admin.role !== "admin") return;
    setAlerts((current) =>
      current.map((alert) =>
        alert.id === alertId
          ? {
              ...alert,
              read: true,
              assignedAdminId: alert.assignedAdminId ?? admin.id,
              assignedAdminName: alert.assignedAdminName ?? admin.name,
            }
          : alert,
      ),
    );
  }, []);

  const ingestAlert = useCallback((alert: Alert) => {
    setAlerts((current) => {
      const exists = current.some((item) => item.id === alert.id);
      if (!exists) return [alert, ...current];
      return current.map((item) => (item.id === alert.id ? alert : item));
    });
  }, []);

  const emitDemoAlert = useCallback(() => {
    setAlerts((current) => [
      makeAlert(
        "هشدار زنده آزمایشی",
        "یک تیکت با فوریت بالا هم‌اکنون توسط Radar شناسایی شد.",
        "high",
        "ticket",
        "/tickets",
      ),
      ...current,
    ]);
  }, []);

  const resetDemoData = useCallback(() => {
    const snapshot = apiClient.resetSnapshot();
    setTickets(snapshot.tickets);
    setEscalations(snapshot.escalations);
    setIncidents(snapshot.incidents);
    setArticles(snapshot.articles);
    setAlerts(snapshot.alerts);
  }, []);

  const value = useMemo<AppContextValue>(
    () => ({
      tickets,
      escalations,
      incidents,
      articles,
      alerts,
      isReady,
      createTicket,
      importTickets,
      analyzeTicket,
      updateTicketStatus,
      escalateTicket,
      sendEscalationMessage,
      updateEscalationStatus,
      updateIncidentStatus,
      createArticle,
      markAlertRead,
      ingestAlert,
      emitDemoAlert,
      resetDemoData,
    }),
    [
      alerts,
      analyzeTicket,
      articles,
      createArticle,
      createTicket,
      emitDemoAlert,
      escalateTicket,
      escalations,
      importTickets,
      ingestAlert,
      incidents,
      isReady,
      markAlertRead,
      resetDemoData,
      sendEscalationMessage,
      tickets,
      updateEscalationStatus,
      updateIncidentStatus,
      updateTicketStatus,
    ],
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useAppData() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error("useAppData باید داخل AppProvider استفاده شود");
  }
  return context;
}
