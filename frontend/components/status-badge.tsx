"use client";

import type {
  AnalysisStatus,
  EscalationStatus,
  IncidentStatus,
  TicketStatus,
  Urgency,
} from "@/types";

export default function UrgencyBadge({ level }: { level: Urgency }) {
  const styles: Record<Urgency, string> = {
    low: "bg-green-50 text-green-700 border-green-200",
    medium: "bg-blue-50 text-blue-700 border-blue-200",
    high: "bg-orange-50 text-orange-700 border-orange-200",
    critical: "bg-red-50 text-red-700 border-red-200",
  };

  const labels: Record<Urgency, string> = {
    low: "کم اهمیت",
    medium: "متوسط",
    high: "فوری / بالا",
    critical: "بحرانی",
  };

  return (
    <span
      className={`inline-flex px-2.5 py-1 text-[10px] font-bold border rounded-full ${styles[level]}`}
    >
      {labels[level]}
    </span>
  );
}

const ticketStatusMap: Record<
  TicketStatus,
  { label: string; className: string }
> = {
  open: { label: "باز", className: "bg-blue-50 text-blue-700" },
  in_progress: {
    label: "در حال پیگیری",
    className: "bg-amber-50 text-amber-700",
  },
  escalated: {
    label: "ارجاع به کارشناس",
    className: "bg-violet-50 text-violet-700",
  },
  resolved: {
    label: "حل شده",
    className: "bg-emerald-50 text-emerald-700",
  },
  closed: { label: "بسته", className: "bg-slate-100 text-slate-600" },
};

export function TicketStatusBadge({ status }: { status: TicketStatus }) {
  const item = ticketStatusMap[status];
  return (
    <span
      className={`inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-bold ${item.className}`}
    >
      {item.label}
    </span>
  );
}

const analysisStatusMap: Record<
  AnalysisStatus,
  { label: string; className: string }
> = {
  pending: {
    label: "در انتظار تحلیل",
    className: "bg-amber-50 text-amber-700 border-amber-100",
  },
  complete: {
    label: "تحلیل شده",
    className: "bg-blue-50 text-blue-700 border-blue-100",
  },
  failed: {
    label: "خطا در تحلیل",
    className: "bg-rose-50 text-rose-700 border-rose-100",
  },
};

export function AnalysisStatusBadge({
  status,
}: {
  status: AnalysisStatus;
}) {
  const item = analysisStatusMap[status];
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-[10px] font-bold ${item.className}`}
    >
      <span className="w-1 h-1 rounded-full bg-current" />
      {item.label}
    </span>
  );
}

const incidentStatusMap: Record<
  IncidentStatus,
  { label: string; className: string }
> = {
  candidate: {
    label: "نیازمند تأیید",
    className: "bg-amber-50 text-amber-700",
  },
  confirmed: {
    label: "تأیید شده",
    className: "bg-rose-50 text-rose-700",
  },
  resolved: {
    label: "رفع شده",
    className: "bg-emerald-50 text-emerald-700",
  },
};

export function IncidentStatusBadge({
  status,
}: {
  status: IncidentStatus;
}) {
  const item = incidentStatusMap[status];
  return (
    <span
      className={`inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-bold ${item.className}`}
    >
      {item.label}
    </span>
  );
}

const escalationStatusMap: Record<
  EscalationStatus,
  { label: string; className: string }
> = {
  waiting: {
    label: "در انتظار پاسخ",
    className: "bg-rose-50 text-rose-700",
  },
  active: {
    label: "در حال گفتگو",
    className: "bg-blue-50 text-blue-700",
  },
  resolved: {
    label: "حل شده",
    className: "bg-emerald-50 text-emerald-700",
  },
};

export function EscalationStatusBadge({
  status,
}: {
  status: EscalationStatus;
}) {
  const item = escalationStatusMap[status];
  return (
    <span
      className={`inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-bold ${item.className}`}
    >
      {item.label}
    </span>
  );
}
