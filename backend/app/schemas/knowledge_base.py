from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

CATEGORY_FA_MAP = {
    "vpn": "مشکل VPN",
    "network": "شبکه و اینترنت",
    "email": "ایمیل",
    "printer": "پرینتر",
    "account": "حساب کاربری",
    "server": "سرور",
    "hardware": "سخت‌افزار",
    "software": "نرم‌افزار",
    "general": "عمومی",
}


def get_category_label_fa(category: str | None) -> str:
    if not category:
        return "عمومی"
    cat_lower = category.lower().strip()
    return CATEGORY_FA_MAP.get(cat_lower, category)


class KnowledgeArticleBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=200, description="عنوان مقاله راهنما")
    content: str = Field(..., min_length=5, description="متن و محتوای راهنما")
    category: str | None = Field(default=None, max_length=100, description="دسته‌بندی موضوعی")
    tags: list[str] = Field(default_factory=list, description="برچسب‌ها و کلمات کلیدی")
    summary: str | None = Field(default=None, description="خلاصه کوتاه مقاله")


class KnowledgeArticleCreate(KnowledgeArticleBase):
    pass


class KnowledgeArticleUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    content: str | None = Field(default=None, min_length=5)
    category: str | None = None
    tags: list[str] | None = None
    summary: str | None = None


class KnowledgeArticleSummary(BaseModel):
    id: int
    title: str
    summary: str
    category: str | None = None
    category_label_fa: str | None = None
    tags: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    author: str = "ادمین سیستم"

    model_config = ConfigDict(from_attributes=True)


class KnowledgeArticleResponse(KnowledgeArticleSummary):
    content: str


class KnowledgeArticleListResponse(BaseModel):
    items: list[KnowledgeArticleSummary]
    total: int
    page: int = 1
    page_size: int = 20
