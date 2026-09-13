import logging
from fastapi import BackgroundTasks, HTTPException, status
import httpx

from app.core.config import settings
from app.repositories.knowledge_base_repository import KnowledgeBaseRepository
from app.schemas.knowledge_base import (
    KnowledgeArticleCreate,
    KnowledgeArticleUpdate,
)

logger = logging.getLogger(__name__)


class KnowledgeBaseService:
    """
    سرویس پایگاه دانش:
    مدیریت منطق تجاری مقالات، جستجو، صفحه‌بندی و ارتباط با AI Core جهت reindex.
    """

    def __init__(self, kb_repo: KnowledgeBaseRepository | None = None) -> None:
        self.kb_repo = kb_repo or KnowledgeBaseRepository()

    async def create_article(
        self,
        article_in: KnowledgeArticleCreate,
        background_tasks: BackgroundTasks | None = None,
    ) -> dict:
        created = await self.kb_repo.create(article_in)

        # اگر تسک پس‌زمینه پاس داده شده باشد، می‌توان reindex خودکار در AI Core را تریگر کرد
        if background_tasks:
            background_tasks.add_task(self.trigger_ai_reindex)

        return created

    async def get_article(self, article_id: int) -> dict:
        article = await self.kb_repo.get_by_id(article_id)
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"مقاله با شناسه {article_id} یافت نشد.",
            )
        return article

    async def list_articles(
        self,
        category: str | None = None,
        q: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        offset = max(0, (page - 1) * page_size)
        items, total = await self.kb_repo.get_all(
            category=category,
            q=q,
            limit=page_size,
            offset=offset,
        )
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def update_article(
        self,
        article_id: int,
        update_data: KnowledgeArticleUpdate,
    ) -> dict:
        updated = await self.kb_repo.update(article_id, update_data)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"مقاله با شناسه {article_id} یافت نشد.",
            )
        return updated

    async def delete_article(self, article_id: int) -> None:
        success = await self.kb_repo.delete(article_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"مقاله با شناسه {article_id} یافت نشد.",
            )

    async def trigger_ai_reindex(self) -> dict:
        """
        ارسال درخواست اختیاری به AI Core برای بازسازی بردارهای امبدینگ مقالات
        """
        try:
            ai_url = f"{settings.AI_CORE_URL}/kb/reindex"
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(ai_url)
                if resp.is_success:
                    return {"status": "success", "detail": "AI Core reindexed"}
        except Exception as exc:
            logger.warning("AI Core reindex notification skipped or failed: %s", exc)

        return {"status": "ok", "message": "Reindex requested locally"}
