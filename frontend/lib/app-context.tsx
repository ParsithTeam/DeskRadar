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
import { useAuth } from "@/lib/auth-context";
import type {
  Alert,
  Escalation,
  Incident,
  IncidentStatus,
  KnowledgeArticle,
  KnowledgeArticleCreateInput,
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

interface AppContextValue {
  tickets: Ticket[];
  escalations: Escalation[];
  incidents: Incident[];
  articles: KnowledgeArticle[];
  alerts: Alert[];
  isReady: boolean;
  dataError: string;
  clearDataError: () => void;
  refreshAll: () => Promise<void>;
  loadTicket: (ticketId: number) => Promise<void>;
  loadIncident: (incidentId: number) => Promise<void>;
  loadArticle: (articleId: number) => Promise<void>;
  createTicket: (input: TicketCreateInput) => Promise<number>;
  importTickets: (rows: ImportedTicket[], actor: User) => Promise<number>;
  analyzeTicket: (ticketId: number) => Promise<void>;
  updateTicketStatus: (ticketId: number, status: TicketStatus) => Promise<void>;
  escalateTicket: (
    ticketId: number,
    reason: string,
    actor: User,
  ) => Promise<string | null>;
  sendEscalationMessage: (
    escalationId: string,
    text: string,
    actor: User,
  ) => Promise<void>;
  updateEscalationStatus: (
    escalationId: string,
    status: Escalation["status"],
    admin?: User,
  ) => Promise<void>;
  updateIncidentStatus: (
    incidentId: number,
    status: IncidentStatus,
  ) => Promise<void>;
  createArticle: (article: KnowledgeArticleCreateInput) => Promise<number>;
  markAlertRead: (alertId: string, admin: User) => Promise<void>;
  ingestAlert: (alert: Alert) => void;
}

const AppContext = createContext<AppContextValue | undefined>(undefined);

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "خطای نامشخصی رخ داد.";
}

function upsertById<T extends { id: number }>(items: T[], item: T): T[] {
  const exists = items.some((current) => current.id === item.id);
  return exists
    ? items.map((current) => (current.id === item.id ? item : current))
    : [item, ...items];
}

function wait(milliseconds: number) {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds));
}

export function AppProvider({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [escalations] = useState<Escalation[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [articles, setArticles] = useState<KnowledgeArticle[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isReady, setIsReady] = useState(false);
  const [dataError, setDataError] = useState("");

  const clearDataError = useCallback(() => setDataError(""), []);

  const refreshAll = useCallback(async () => {
    if (!user) {
      setTickets([]);
      setIncidents([]);
      setArticles([]);
      setAlerts([]);
      setDataError("");
      setIsReady(true);
      return;
    }

    setIsReady(false);
    setDataError("");

    const ticketRequest =
      user.role === "admin"
        ? apiClient.listAdminTickets(user)
        : apiClient.listUserTickets(user);
    const [ticketResult, articleResult, incidentResult, alertResult] =
      await Promise.allSettled([
        ticketRequest,
        apiClient.listArticles(),
        user.role === "admin" ? apiClient.listIncidents() : Promise.resolve([]),
        user.role === "admin" ? apiClient.listAlerts() : Promise.resolve([]),
      ]);
    const errors: string[] = [];

    if (ticketResult.status === "fulfilled") {
      setTickets(ticketResult.value);
    } else {
      setTickets([]);
      errors.push(`تیکت‌ها: ${errorMessage(ticketResult.reason)}`);
    }

    if (articleResult.status === "fulfilled") {
      setArticles(articleResult.value);
    } else {
      setArticles([]);
      errors.push(`پایگاه دانش: ${errorMessage(articleResult.reason)}`);
    }

    if (user.role === "admin") {
      if (incidentResult.status === "fulfilled") {
        setIncidents(incidentResult.value);
      } else {
        setIncidents([]);
        errors.push(`رخدادها: ${errorMessage(incidentResult.reason)}`);
      }

      if (alertResult.status === "fulfilled") {
        setAlerts(alertResult.value);
      } else {
        setAlerts([]);
        errors.push(`هشدارها: ${errorMessage(alertResult.reason)}`);
      }
    } else {
      setIncidents([]);
      setAlerts([]);
    }

    setDataError(errors.join(" | "));
    setIsReady(true);
  }, [user]);

  useEffect(() => {
    const timer = window.setTimeout(() => void refreshAll(), 0);
    return () => window.clearTimeout(timer);
  }, [refreshAll]);

  const loadTicket = useCallback(
    async (ticketId: number) => {
      if (!user) return;
      try {
        const ticket = await apiClient.getTicket(ticketId, user);
        setTickets((current) => upsertById(current, ticket));
      } catch (error) {
        setDataError(errorMessage(error));
        throw error;
      }
    },
    [user],
  );

  const loadIncident = useCallback(async (incidentId: number) => {
    try {
      const incident = await apiClient.getIncident(incidentId);
      setIncidents((current) => upsertById(current, incident));
    } catch (error) {
      setDataError(errorMessage(error));
      throw error;
    }
  }, []);

  const loadArticle = useCallback(async (articleId: number) => {
    try {
      const article = await apiClient.getArticle(articleId);
      setArticles((current) => upsertById(current, article));
    } catch (error) {
      setDataError(errorMessage(error));
      throw error;
    }
  }, []);

  const pollTicketAnalysis = useCallback(
    async (ticketId: number) => {
      if (!user) return;
      for (let attempt = 0; attempt < 20; attempt += 1) {
        await wait(1500);
        try {
          const ticket = await apiClient.getTicket(ticketId, user);
          setTickets((current) => upsertById(current, ticket));
          if (ticket.analysisStatus !== "pending") return;
        } catch (error) {
          if (attempt === 19) setDataError(errorMessage(error));
        }
      }
    },
    [user],
  );

  const createTicket = useCallback(
    async (input: TicketCreateInput) => {
      try {
        const ticket = await apiClient.createTicket(input);
        setTickets((current) => upsertById(current, ticket));
        if (ticket.analysisStatus === "pending") {
          void pollTicketAnalysis(ticket.id);
        }
        return ticket.id;
      } catch (error) {
        setDataError(errorMessage(error));
        throw error;
      }
    },
    [pollTicketAnalysis],
  );

  const analyzeTicket = useCallback(
    async (ticketId: number) => {
      const previous = tickets.find((ticket) => ticket.id === ticketId);
      setTickets((current) =>
        current.map((ticket) =>
          ticket.id === ticketId
            ? { ...ticket, analysisStatus: "pending" }
            : ticket,
        ),
      );

      try {
        await apiClient.analyzeTicket(ticketId);
        void pollTicketAnalysis(ticketId);
      } catch (error) {
        if (previous) {
          setTickets((current) => upsertById(current, previous));
        }
        setDataError(errorMessage(error));
        throw error;
      }
    },
    [pollTicketAnalysis, tickets],
  );

  const updateTicketStatus = useCallback(
    async (ticketId: number, status: TicketStatus) => {
      try {
        const ticket = await apiClient.updateTicketStatus(ticketId, status);
        setTickets((current) => upsertById(current, ticket));
      } catch (error) {
        setDataError(errorMessage(error));
        throw error;
      }
    },
    [],
  );

  const updateIncidentStatus = useCallback(
    async (incidentId: number, status: IncidentStatus) => {
      try {
        const incident = await apiClient.updateIncidentStatus(incidentId, status);
        setIncidents((current) => upsertById(current, incident));
      } catch (error) {
        setDataError(errorMessage(error));
        throw error;
      }
    },
    [],
  );

  const markAlertRead = useCallback(async (alertId: string, admin: User) => {
    if (admin.role !== "admin") return;
    try {
      const alert = await apiClient.markAlertRead(alertId, admin);
      setAlerts((current) =>
        current.map((item) => (item.id === alert.id ? alert : item)),
      );
    } catch (error) {
      setDataError(errorMessage(error));
      throw error;
    }
  }, []);

  const createArticle = useCallback(
    async (input: KnowledgeArticleCreateInput) => {
      try {
        const article = await apiClient.createArticle(input);
        setArticles((current) => upsertById(current, article));
        return article.id;
      } catch (error) {
        setDataError(errorMessage(error));
        throw error;
      }
    },
    [],
  );

  const ingestAlert = useCallback((alert: Alert) => {
    setAlerts((current) => {
      const exists = current.some((item) => item.id === alert.id);
      return exists
        ? current.map((item) => (item.id === alert.id ? alert : item))
        : [alert, ...current];
    });
  }, []);

  const unsupported = useCallback(async (feature: string): Promise<never> => {
    const message = `API بخش «${feature}» هنوز در بک‌اند پیاده‌سازی نشده است.`;
    setDataError(message);
    throw new Error(message);
  }, []);

  const value = useMemo<AppContextValue>(
    () => ({
      tickets,
      escalations,
      incidents,
      articles,
      alerts,
      isReady,
      dataError,
      clearDataError,
      refreshAll,
      loadTicket,
      loadIncident,
      loadArticle,
      createTicket,
      importTickets: () => unsupported("ورود گروهی CSV"),
      analyzeTicket,
      updateTicketStatus,
      escalateTicket: () => unsupported("ارجاع تیکت و گفتگو"),
      sendEscalationMessage: () => unsupported("گفتگوی ارجاع"),
      updateEscalationStatus: () => unsupported("مدیریت ارجاع"),
      updateIncidentStatus,
      createArticle,
      markAlertRead,
      ingestAlert,
    }),
    [
      alerts,
      analyzeTicket,
      articles,
      clearDataError,
      createArticle,
      createTicket,
      dataError,
      escalations,
      incidents,
      ingestAlert,
      isReady,
      loadIncident,
      loadArticle,
      loadTicket,
      markAlertRead,
      refreshAll,
      tickets,
      unsupported,
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
