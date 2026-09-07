# http://127.0.0.1:8000/docs ادرس سواگر 
# uvicorn app.main:app --reload برای اینمکه فست ای پی ای رو اجرا کنه 

from fastapi import FastAPI
from app.api.routes.tickets import router as ticket_router
from  app.api.routes.alerts import router as alert_router
from app.api.routes.incidents import router as incident_router
app = FastAPI(
    title="ServiceDesk Radar API",
    version="1.0.0",
    description="Backend API for ServiceDesk Radar"
)

app.include_router(ticket_router, prefix="/api")
app.include_router(alert_router)
app.include_router(incident_router)

@app.get("/health")
def health_check():
    return {"status": "I'm alive!"}

#ساخت اند پوینت تستی برای بارکردن کانکشن به پستجر اس کی ال
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.core.database import get_db

@app.get("/db-test")
async def db_test(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT 1"))
    return {
        "database": "connected",
        "result": result.scalar(),
    }
