import copy
import json
from datetime import datetime, timezone
from pathlib import Path

from app.schemas.knowledge_base import (
    KnowledgeArticleCreate,
    KnowledgeArticleUpdate,
    get_category_label_fa,
)

FAKE_KB_DB: list[dict] = []
_kb_id_counter = 100


def _load_initial_seed_articles() -> None:
    global _kb_id_counter
    if FAKE_KB_DB:
        return

    seed_path = Path(__file__).resolve().parent.parent.parent.parent / "ai-core" / "data" / "knowledge_articles.json"
    if seed_path.exists():
        try:
            with open(seed_path, "r", encoding="utf-8") as f:
                articles = json.load(f)
                now = datetime.now(timezone.utc)
                for item in articles:
                    art_id = item.get("article_id") or item.get("id") or _kb_id_counter
                    if isinstance(art_id, int) and art_id >= _kb_id_counter:
                        _kb_id_counter = art_id + 1

                    content = item.get("content", "")
                    summary = item.get("summary") or (content[:150] + "..." if len(content) > 150 else content)
                    category = item.get("category", "general")
                    FAKE_KB_DB.append({
                        "id": art_id,
                        "title": item.get("title", ""),
                        "content": content,
                        "summary": summary,
                        "category": category,
                        "category_label_fa": get_category_label_fa(category),
                        "tags": item.get("tags", []),
                        "created_at": now,
                        "updated_at": now,
                        "author": "ادمین پشتیبانی IT",
                    })
                return
        except Exception:
            pass

    # فال‌بک اولیه در صورتی که فایل seed لود نشود
    now = datetime.now(timezone.utc)
    fallback_seed = [
        {
            "id": 1,
            "title": "راهنمای رفع خطای احراز هویت VPN",
            "content": "اگر هنگام اتصال به VPN خطای احراز هویت دریافت می‌کنید، ابتدا نام کاربری و رمز عبور و کد یک‌بارمصرف MFA را بررسی نمایید.",
            "summary": "نحوه بررسی خطاهای احراز هویت، رمز عبور و کدهای MFA برای اتصال امن VPN.",
            "category": "vpn",
            "category_label_fa": "مشکل VPN",
            "tags": ["vpn", "mfa", "احراز هویت"],
            "created_at": now,
            "updated_at": now,
            "author": "ادمین پشتیبانی IT",
        }
    ]
    FAKE_KB_DB.extend(fallback_seed)


# بارگذاری اولیه داده‌های نمونه
_load_initial_seed_articles()


class KnowledgeBaseRepository:
    """
    ریپازیتوری پایگاه دانش:
    مسئول کلیه عملیات خواندن، نوشتن و جستجوی مقالات راهنما.
    در حال حاضر با ساختار ایزوله در حافظه پیاده‌سازی شده و پس از تکمیل
    لایه دیتابیس توسط تیم مربوطه، بدون دستکاری لایه سرویس به AsyncSession متصل خواهد شد.
    """

    async def create(self, article_in: KnowledgeArticleCreate) -> dict:
        global _kb_id_counter
        now = datetime.now(timezone.utc)

        content = article_in.content.strip()
        summary = article_in.summary or (content[:150] + "..." if len(content) > 150 else content)
        category = article_in.category or "general"

        new_article = {
            "id": _kb_id_counter,
            "title": article_in.title.strip(),
            "content": content,
            "summary": summary,
            "category": category,
            "category_label_fa": get_category_label_fa(category),
            "tags": [t.strip() for t in article_in.tags if t.strip()],
            "created_at": now,
            "updated_at": now,
            "author": "ادمین پشتیبانی IT",
        }

        _kb_id_counter += 1
        FAKE_KB_DB.insert(0, new_article)
        return copy.deepcopy(new_article)

    async def get_by_id(self, article_id: int) -> dict | None:
        for item in FAKE_KB_DB:
            if item.get("id") == article_id:
                return copy.deepcopy(item)
        return None

    async def get_all(
        self,
        category: str | None = None,
        q: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[dict], int]:
        filtered = []

        q_clean = q.lower().strip() if q else None
        cat_clean = category.lower().strip() if category else None

        for item in FAKE_KB_DB:
            # فیلتر دسته‌بندی
            if cat_clean:
                item_cat = (item.get("category") or "").lower()
                if item_cat != cat_clean:
                    continue

            # فیلتر جستجوی متنی روی عنوان، محتوا و تگ‌ها
            if q_clean:
                title_match = q_clean in item.get("title", "").lower()
                content_match = q_clean in item.get("content", "").lower()
                tag_match = any(q_clean in str(t).lower() for t in item.get("tags", []))
                if not (title_match or content_match or tag_match):
                    continue

            filtered.append(item)

        total = len(filtered)
        paginated = filtered[offset : offset + limit]
        return copy.deepcopy(paginated), total

    async def update(self, article_id: int, update_data: KnowledgeArticleUpdate) -> dict | None:
        article = None
        for item in FAKE_KB_DB:
            if item.get("id") == article_id:
                article = item
                break

        if not article:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)

        if "title" in update_dict and update_dict["title"] is not None:
            article["title"] = update_dict["title"].strip()

        if "content" in update_dict and update_dict["content"] is not None:
            article["content"] = update_dict["content"].strip()
            if "summary" not in update_dict:
                article["summary"] = article["content"][:150] + "..." if len(article["content"]) > 150 else article["content"]

        if "summary" in update_dict and update_dict["summary"] is not None:
            article["summary"] = update_dict["summary"].strip()

        if "category" in update_dict and update_dict["category"] is not None:
            cat = update_dict["category"].strip()
            article["category"] = cat
            article["category_label_fa"] = get_category_label_fa(cat)

        if "tags" in update_dict and update_dict["tags"] is not None:
            article["tags"] = [t.strip() for t in update_dict["tags"] if t.strip()]

        article["updated_at"] = datetime.now(timezone.utc)
        return copy.deepcopy(article)

    async def delete(self, article_id: int) -> bool:
        global FAKE_KB_DB
        initial_len = len(FAKE_KB_DB)
        FAKE_KB_DB = [item for item in FAKE_KB_DB if item.get("id") != article_id]
        return len(FAKE_KB_DB) < initial_len
