from fastapi import APIRouter, BackgroundTasks, Query, status

from app.repositories.knowledge_base_repository import KnowledgeBaseRepository
from app.schemas.knowledge_base import (
    KnowledgeArticleCreate,
    KnowledgeArticleListResponse,
    KnowledgeArticleResponse,
    KnowledgeArticleUpdate,
)
from app.services.knowledge_base_service import KnowledgeBaseService

router = APIRouter(prefix="/knowledge-articles", tags=["Knowledge Base"])

kb_repo = KnowledgeBaseRepository()
kb_service = KnowledgeBaseService(kb_repo=kb_repo)


# ==============================================================================
# اندپوینت‌های رسمی و منطبق با فرانت‌اند DeskRadar (/knowledge-articles)
# ==============================================================================

@router.get(
    "",
    response_model=KnowledgeArticleListResponse,
    status_code=status.HTTP_200_OK,
    summary="دریافت لیست مقالات راهنما (پشتیبانی از جستجو و فیلتر دسته‌بندی)",
)
@router.get(
    "/",
    response_model=KnowledgeArticleListResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def list_articles(
    category: str | None = Query(default=None, description="فیلتر بر اساس دسته‌بندی (مانند vpn, email, network)"),
    q: str | None = Query(default=None, description="عبارت جستجو در عنوان، متن یا تگ‌ها"),
    page: int = Query(default=1, ge=1, description="شماره صفحه"),
    page_size: int = Query(default=20, ge=1, le=100, alias="pageSize", description="تعداد در هر صفحه"),
):
    return await kb_service.list_articles(
        category=category,
        q=q,
        page=page,
        page_size=page_size,
    )


@router.post(
    "",
    response_model=KnowledgeArticleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="ایجاد و ثبت مقاله جدید در پایگاه دانش",
)
@router.post(
    "/",
    response_model=KnowledgeArticleResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def create_article(
    article_in: KnowledgeArticleCreate,
    background_tasks: BackgroundTasks,
):
    return await kb_service.create_article(
        article_in=article_in,
        background_tasks=background_tasks,
    )


@router.get(
    "/{article_id}",
    response_model=KnowledgeArticleResponse,
    status_code=status.HTTP_200_OK,
    summary="دریافت جزئیات کامل مقاله راهنما",
)
async def get_article(article_id: int):
    return await kb_service.get_article(article_id=article_id)


@router.patch(
    "/{article_id}",
    response_model=KnowledgeArticleResponse,
    status_code=status.HTTP_200_OK,
    summary="ویرایش و به‌روزرسانی مقاله راهنما",
)
async def update_article(article_id: int, update_in: KnowledgeArticleUpdate):
    return await kb_service.update_article(article_id=article_id, update_data=update_in)


@router.delete(
    "/{article_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="حذف مقاله از پایگاه دانش",
)
async def delete_article(article_id: int):
    await kb_service.delete_article(article_id=article_id)
    return None


@router.post(
    "/reindex",
    status_code=status.HTTP_200_OK,
    summary="درخواست بازسازی بردارها در هوش مصنوعی",
)
async def reindex_knowledge_base():
    return await kb_service.trigger_ai_reindex()
