"use client";

import { useParams } from "next/navigation";
import TicketDetailView from "@/components/ticket-detail-view";

export default function MyTicketDetailPage() {
  const params = useParams<{ id: string }>();
  return <TicketDetailView ticketId={Number(params.id)} view="user" />;
}
