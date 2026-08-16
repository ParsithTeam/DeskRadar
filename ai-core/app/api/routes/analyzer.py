from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool

from ...analyzer.analyzer_service import analyze_ticket
from ...schemas.analyzer import AnalyzeRequest, AnalyzerResponse

router = APIRouter(prefix="/analyzer", tags=["Analyzer"])


@router.post(
    "/analyze",
    response_model=AnalyzerResponse,
    response_model_exclude_none=True,
)
async def analyze(payload: AnalyzeRequest) -> dict:
    result = await run_in_threadpool(
        analyze_ticket,
        payload.to_analysis_text(),
        payload.ticket_id,
        debug=payload.debug,
    )
    if result.get("analysis_status") != "completed":
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result
