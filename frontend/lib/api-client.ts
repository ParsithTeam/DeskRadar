import type {
  Alert,
  AnalysisStatus,
  Incident,
  IncidentStatus,
  Ticket,
  TicketAnalysis,
  TicketCategory,
  TicketCreateInput,
  TicketStatus,
  Urgency,
} from "@/types";

const API_PREFIX = "/backend-api";

type JsonRecord = Record<string, unknown>;

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status?: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

function isRecord(value: unknown): value is JsonRecord {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function asString(value: unknown, fallback = ""): string {
  return typeof value === "string" ? value : fallback;
}

function asNumber(value: unknown, fallback = 0): number {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

function formatDate(value: unknown): string {
  const raw = asString(value);
  if (!raw) return "نامشخص";
  const date = new Date(raw);
  if (Number.isNaN(date.getTime())) return raw;
  return new Intl.DateTimeFormat("fa-IR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(date);
}

function normalizeCategory(value: unknown): TicketCategory {
  const category = asString(value, "unknown");
  const known: TicketCategory[] = [
    "vpn",
    "email",
    "network",
    "printer",
    "account",
    "permission",
    "software",
    "hardware",
    "unknown",
  ];
  return known.includes(category as TicketCategory)
    ? (category as TicketCategory)
    : "unknown";
}

function normalizeUrgency(value: unknown): Urgency {
  const urgency = asString(value).toLowerCase();
  return urgency === "medium" || urgency === "high" || urgency === "critical"
    ? urgency
    : urgency === "low"
      ? "low"
      : "unknown";
}

function normalizeTicketStatus(value: unknown): TicketStatus {
  const status = asString(value).toLowerCase();
  return status === "in_progress" ||
    status === "resolved" ||
    status === "closed" ||
    status === "escalated"
    ? status
    : "open";
}

function normalizeAnalysisStatus(value: unknown): AnalysisStatus {
  const status = asString(value).toLowerCase();
  if (status === "waiting" || status === "pending" || status === "failed") {
    return status;
  }
  return status === "completed" || status === "complete" ? "complete" : "waiting";
}

function categoryLabel(category: TicketCategory): string {
  const labels: Record<TicketCategory, string> = {
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
  return labels[category];
}

function mapAnalysis(value: unknown): TicketAnalysis | null {
  if (!isRecord(value)) return null;
  const category = normalizeCategory(value.category);
  const related = Array.isArray(value.related_article)
    ? value.related_article[0]
    : value.related_article;
  const relatedRecord = isRecord(related) ? related : null;

  return {
    category,
    categoryLabelFa:
      asString(value.category_label_fa) || categoryLabel(category),
    intentLabelFa: asString(value.intent_label_fa, "نامشخص"),
    urgency: normalizeUrgency(value.urgency),
    confidence: Math.min(Math.max(asNumber(value.confidence), 0), 1),
    summaryFa: asString(value.summary_fa, "خلاصه‌ای ثبت نشده است."),
    suggestedReplyFa: asString(
      value.suggested_reply_fa,
      "پاسخ پیشنهادی ثبت نشده است.",
    ),
    reasonsFa: Array.isArray(value.reasons_fa)
      ? value.reasons_fa.filter((item): item is string => typeof item === "string")
      : [],
    similarTickets: [],
    relatedArticle: relatedRecord
      ? {
          id: asNumber(relatedRecord.article_id ?? relatedRecord.id),
          title: asString(relatedRecord.title, "مقاله مرتبط"),
          score: asNumber(relatedRecord.score),
        }
      : null,
    possibleIncident: false,
  };
}

function mapTicket(value: unknown, currentUser?: { id: string; name: string }): Ticket {
  if (!isRecord(value)) throw new ApiError("پاسخ تیکت از بک‌اند معتبر نیست.");
  const analysis = mapAnalysis(value.ai_analysis);
  const requesterName = asString(value.requester, "نامشخص");
  const category = analysis?.category ?? "unknown";

  return {
    id: asNumber(value.ticket_id ?? value.id),
    title: asString(value.title, "بدون عنوان"),
    description: asString(value.description),
    department: asString(value.department, "نامشخص"),
    requesterId:
      currentUser && requesterName === currentUser.name
        ? currentUser.id
        : requesterName,
    requesterName,
    category,
    categoryLabelFa: analysis?.categoryLabelFa ?? categoryLabel(category),
    urgency: analysis?.urgency ?? normalizeUrgency(value.urgency),
    status: normalizeTicketStatus(value.ticket_status ?? value.status),
    analysisStatus: normalizeAnalysisStatus(value.analysis_status),
    confidence: analysis?.confidence ?? 0,
    createdAt: formatDate(value.created_at),
    updatedAt: formatDate(value.updated_at ?? value.created_at),
    analysis,
  };
}

function normalizeIncidentStatus(value: unknown): IncidentStatus {
  const status = asString(value).toLowerCase();
  return status === "confirmed" || status === "resolved" || status === "dismissed"
    ? status
    : "candidate";
}

function mapIncident(value: unknown): Incident {
  if (!isRecord(value)) throw new ApiError("پاسخ رخداد از بک‌اند معتبر نیست.");
  const matchedIds = Array.isArray(value.matched_ticket_ids)
    ? value.matched_ticket_ids.filter((id): id is number => typeof id === "number")
    : [];
  const normalizedSeverity = normalizeUrgency(value.severity);

  return {
    id: asNumber(value.id),
    title: asString(value.title_fa, "رخداد بدون عنوان"),
    description: asString(value.reason_fa),
    category: "unknown",
    categoryLabelFa: "ثبت نشده",
    severity: normalizedSeverity === "unknown" ? "medium" : normalizedSeverity,
    status: normalizeIncidentStatus(value.status),
    detectedReason: asString(value.reason_fa, "دلیلی ثبت نشده است."),
    createdAt: formatDate(value.created_at),
    resolvedAt: value.resolved_at ? formatDate(value.resolved_at) : undefined,
    tickets: matchedIds.map((ticketId) => ({
      ticketId,
      title: `تیکت #${ticketId.toLocaleString("fa-IR")}`,
    })),
  };
}

export function mapAlertFromApi(value: unknown): Alert {
  if (!isRecord(value)) throw new ApiError("پاسخ هشدار از بک‌اند معتبر نیست.");
  const rawType = asString(value.type);
  const incidentId = asNumber(value.incident_id);
  const ticketId = asNumber(value.ticket_id);
  const rawSeverity = asString(value.severity);
  const severity =
    rawSeverity === "critical"
      ? "critical"
      : rawSeverity === "warning"
        ? "high"
        : "low";
  const type = rawType === "incident_candidate" ? "incident" : "ticket";

  return {
    id: String(value.alert_id ?? value.id ?? ""),
    title:
      type === "incident"
        ? "هشدار رخداد"
        : rawType === "urgent_ticket"
          ? "تیکت فوری"
          : "هشدار جدید",
    message: asString(value.message, "هشدار جدیدی ثبت شده است."),
    severity,
    type,
    createdAt: formatDate(value.created_at),
    read: Boolean(value.is_read),
    href: incidentId
      ? `/incidents/${incidentId}`
      : ticketId
        ? `/tickets/${ticketId}`
        : undefined,
  };
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_PREFIX}${path}`, {
      ...init,
      cache: "no-store",
      headers: {
        Accept: "application/json",
        ...(init?.body ? { "Content-Type": "application/json" } : {}),
        ...init?.headers,
      },
    });
  } catch {
    throw new ApiError(
      "ارتباط با بک‌اند برقرار نشد. از اجرا بودن سرویس روی پورت تنظیم‌شده مطمئن شوید.",
    );
  }

  if (!response.ok) {
    let message = `درخواست با خطای ${response.status} روبه‌رو شد.`;
    try {
      const payload: unknown = await response.json();
      if (isRecord(payload)) {
        message = asString(payload.detail) || asString(payload.message) || message;
      }
    } catch {
      // Keep the status-based message for non-JSON errors.
    }
    throw new ApiError(message, response.status);
  }

  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export const apiClient = {
  async health() {
    return request<{ status: string }>("/health");
  },

  async listAdminTickets(currentUser: { id: string; name: string }) {
    const data = await request<unknown[]>("/api/tickets/admin?limit=100&offset=0");
    return data.map((item) => mapTicket(item, currentUser));
  },

  async listUserTickets(currentUser: { id: string; name: string }) {
    const params = new URLSearchParams({
      current_user: currentUser.name,
      limit: "100",
      offset: "0",
    });
    const data = await request<unknown[]>(`/api/tickets?${params}`);
    return data.map((item) =>
      mapTicket(
        isRecord(item) ? { ...item, requester: currentUser.name } : item,
        currentUser,
      ),
    );
  },

  async getTicket(ticketId: number, currentUser: { id: string; name: string }) {
    const data = await request<unknown>(`/api/tickets/${ticketId}`);
    return mapTicket(data, currentUser);
  },

  async createTicket(input: TicketCreateInput) {
    const data = await request<unknown>("/api/tickets?auto_analyze=true", {
      method: "POST",
      body: JSON.stringify({
        title: input.title,
        description: input.description,
        requester: input.requesterName,
        department: input.department,
      }),
    });
    return mapTicket(data, { id: input.requesterId, name: input.requesterName });
  },

  async analyzeTicket(ticketId: number) {
    await request<unknown>(`/api/tickets/${ticketId}/analyze`, { method: "POST" });
  },

  async listIncidents(status?: IncidentStatus) {
    const query = status ? `?status=${encodeURIComponent(status)}` : "";
    const data = await request<unknown[]>(`/incidents${query}`);
    return data.map(mapIncident);
  },

  async getIncident(incidentId: number) {
    return mapIncident(await request<unknown>(`/incidents/${incidentId}`));
  },

  async updateIncidentStatus(incidentId: number, status: IncidentStatus) {
    const options: RequestInit = {
      method: "PATCH",
      body: JSON.stringify({ status }),
    };
    let data: unknown;
    try {
      data = await request<unknown>(`/incidents/${incidentId}/status`, options);
    } catch (error) {
      if (!(error instanceof ApiError) || error.status !== 404) throw error;
      data = await request<unknown>(`/incidents/${incidentId}/satus`, options);
    }
    return mapIncident(data);
  },

  async listAlerts() {
    const data = await request<unknown[]>("/alerts");
    return data.map(mapAlertFromApi);
  },

  async markAlertRead(alertId: string) {
    return mapAlertFromApi(
      await request<unknown>(`/alerts/${encodeURIComponent(alertId)}/mark-read`, {
        method: "POST",
      }),
    );
  },
};
