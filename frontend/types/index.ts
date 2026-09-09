export type Role = "admin" | "user";

export type TicketCategory =
  | "vpn"
  | "email"
  | "network"
  | "printer"
  | "account"
  | "permission"
  | "software"
  | "hardware"
  | "unknown";

export type Urgency = "unknown" | "low" | "medium" | "high" | "critical";
export type TicketStatus =
  | "open"
  | "in_progress"
  | "escalated"
  | "resolved"
  | "closed";
export type AnalysisStatus = "waiting" | "pending" | "complete" | "failed";
export type IncidentStatus =
  | "candidate"
  | "confirmed"
  | "resolved"
  | "dismissed";
export type EscalationStatus = "waiting" | "active" | "resolved";
export type AlertSeverity = "low" | "medium" | "high" | "critical";

export interface User {
  id: string;
  name: string;
  email: string;
  role: Role;
}

export interface SimilarTicket {
  id: number;
  title: string;
  score: number;
}

export interface TicketAnalysis {
  category: TicketCategory;
  categoryLabelFa: string;
  intentLabelFa: string;
  urgency: Urgency;
  confidence: number;
  summaryFa: string;
  suggestedReplyFa: string;
  reasonsFa: string[];
  similarTickets: SimilarTicket[];
  relatedArticle: {
    id: number;
    title: string;
    score: number;
  } | null;
  possibleIncident: boolean;
}

export interface Ticket {
  id: number;
  title: string;
  description: string;
  department: string;
  requesterId: string;
  requesterName: string;
  category: TicketCategory;
  categoryLabelFa: string;
  urgency: Urgency;
  status: TicketStatus;
  analysisStatus: AnalysisStatus;
  confidence: number;
  createdAt: string;
  updatedAt: string;
  analysis: TicketAnalysis | null;
}

export interface TicketCreateInput {
  title: string;
  description: string;
  department: string;
  requesterId: string;
  requesterName: string;
}

export interface EscalationMessage {
  id: string;
  senderId: string;
  senderName: string;
  senderRole: Role;
  text: string;
  createdAt: string;
}

export interface Escalation {
  id: string;
  ticketId: number;
  requesterId: string;
  requesterName: string;
  reason: string;
  status: EscalationStatus;
  assignedAdminId?: string;
  assignedAdminName?: string;
  createdAt: string;
  updatedAt: string;
  messages: EscalationMessage[];
}

export interface IncidentTicket {
  ticketId: number;
  title: string;
  similarity?: number;
}

export interface Incident {
  id: number;
  title: string;
  description: string;
  category: TicketCategory;
  categoryLabelFa: string;
  severity: AlertSeverity;
  status: IncidentStatus;
  detectedReason: string;
  createdAt: string;
  resolvedAt?: string;
  tickets: IncidentTicket[];
}

export interface KnowledgeArticle {
  id: number;
  title: string;
  summary: string;
  category: TicketCategory;
  categoryLabelFa: string;
  tags: string[];
  content: string;
  updatedAt: string;
  author: string;
}

export interface Alert {
  id: string;
  title: string;
  message: string;
  severity: AlertSeverity;
  type: "incident" | "ticket" | "escalation";
  createdAt: string;
  read: boolean;
  assignedAdminId?: string;
  assignedAdminName?: string;
  href?: string;
}
