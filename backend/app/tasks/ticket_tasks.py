async def analyze_ticket_task(ticket_id: int) -> None:
    from app.core.database import get_session_context
    from app.core.dependencies import buil_ticket_service

    async with get_session_context() as db_session:
        ticket_service = buil_ticket_service(db_session)
        await ticket_service.process_ticket_analyze(ticket_id=ticket_id)
