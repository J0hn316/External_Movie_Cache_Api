from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.db.models import MovieDetailsCache, MovieSearchCache


def utc_now() -> datetime:
    return datetime.now(UTC)


def _count_all(db: Session, model: type) -> int:
    stmt = select(func.count()).select_from(model)
    return int(db.execute(stmt).scalar_one())


def _count_expired(db: Session, model: type) -> int:
    stmt = select(func.count()).select_from(model).where(model.expires_at <= utc_now())
    return int(db.execute(stmt).scalar_one())


def get_cache_stats(db: Session) -> dict[str, int]:
    return {
        "search_cache_count": _count_all(db, MovieSearchCache),
        "details_cache_count": _count_all(db, MovieDetailsCache),
        "expired_search_cache_count": _count_expired(db, MovieSearchCache),
        "expired_details_cache_count": _count_expired(db, MovieDetailsCache),
    }


def delete_expired_cache(db: Session) -> dict[str, int]:
    now = utc_now()

    search_result = db.execute(
        delete(MovieSearchCache).where(MovieSearchCache.expires_at <= now)
    )

    details_result = db.execute(
        delete(MovieDetailsCache).where(MovieDetailsCache.expires_at <= now)
    )

    db.commit()

    return {
        "deleted_search_cache": int(search_result.rowcount or 0),
        "deleted_details_cache": int(details_result.rowcount or 0),
    }
