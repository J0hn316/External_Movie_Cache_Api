import json
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.clients.tmdb_client import TMDbClient, TMDbClientError
from app.core.config import settings
from app.db.models import MovieDetailsCache, MovieSearchCache


def utc_now() -> datetime:
    return datetime.now(UTC)


def get_expires_at() -> datetime:
    return utc_now() + timedelta(seconds=settings.cache_ttl_seconds)


def is_fresh(expires_at: datetime) -> bool:
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)

    return expires_at > utc_now()


def normalize_query(query: str) -> str:
    return query.strip().lower()


def search_movies_with_cache(
    db: Session, *, query: str, page: int = 1, client: TMDbClient | None = None
) -> tuple[str, dict[str, Any]]:
    normalized_query = normalize_query(query)

    cache_key = f"{normalized_query}:page:{page}"

    stmt = select(MovieSearchCache).where(MovieSearchCache.query == cache_key)
    cached = db.execute(stmt).scalar_one_or_none()

    if cached is not None and is_fresh(cached.expires_at):
        return "cached", json.loads(cached.response_json)

    tmdb = client or TMDbClient()

    try:
        data = tmdb.search_movies(normalized_query, page=page)
    except TMDbClientError:
        raise

    response_json = json.dumps(data, ensure_ascii=False)

    if cached is None:
        cached = MovieSearchCache(
            query=cache_key, response_json=response_json, expires_at=get_expires_at()
        )
        db.add(cached)
    else:
        cached.response_json = response_json
        cached.cached_at = utc_now()
        cached.expires_at = get_expires_at()

    db.commit()
    db.refresh(cached)

    return "tmdb", data


def get_movie_details_with_cache(
    db: Session,
    *,
    tmdb_id: int,
    client: TMDbClient | None = None,
) -> tuple[str, dict[str, Any]]:
    stmt = select(MovieDetailsCache).where(MovieDetailsCache.tmdb_id == tmdb_id)
    cached = db.execute(stmt).scalar_one_or_none()

    if cached is not None and is_fresh(cached.expires_at):
        return "cache", json.loads(cached.response_json)

    tmdb = client or TMDbClient()

    try:
        data = tmdb.get_movie_details(tmdb_id)
    except TMDbClientError:
        raise

    response_json = json.dumps(data, ensure_ascii=False)

    if cached is None:
        cached = MovieDetailsCache(
            tmdb_id=tmdb_id,
            response_json=response_json,
            expires_at=get_expires_at(),
        )
        db.add(cached)
    else:
        cached.response_json = response_json
        cached.cached_at = utc_now()
        cached.expires_at = get_expires_at()

    db.commit()
    db.refresh(cached)

    return "tmdb", data
