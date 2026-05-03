from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.db.models import MovieDetailsCache, MovieSearchCache
from app.services.cache_service import delete_expired_cache, get_cache_stats


def test_cache_stats_counts_rows(db_session: Session) -> None:
    now = datetime.now(UTC)

    search_cache = MovieSearchCache(
        query="stats-test:page:1",
        response_json=json.dumps({"results": []}),
        expires_at=now + timedelta(seconds=3600),
    )

    details_cache = MovieDetailsCache(
        tmdb_id=999001,
        response_json=json.dumps({"id": 999001}),
        expires_at=now + timedelta(seconds=3600),
    )

    db_session.add_all([search_cache, details_cache])
    db_session.commit()

    stats = get_cache_stats(db_session)

    assert stats["search_cache_count"] >= 1
    assert stats["details_cache_count"] >= 1


def test_cache_stats_counts_expired_rows(db_session: Session) -> None:
    now = datetime.now(UTC)

    expired_search = MovieSearchCache(
        query="expired-search:page:1",
        response_json=json.dumps({"results": []}),
        expires_at=now - timedelta(seconds=10),
    )

    expired_details = MovieDetailsCache(
        tmdb_id=999002,
        response_json=json.dumps({"id": 999002}),
        expires_at=now - timedelta(seconds=10),
    )

    db_session.add_all([expired_search, expired_details])
    db_session.commit()

    stats = get_cache_stats(db_session)

    assert stats["expired_search_cache_count"] >= 1
    assert stats["expired_details_cache_count"] >= 1


def test_delete_expired_cache(db_session: Session) -> None:
    now = datetime.now(UTC)

    expired_search = MovieSearchCache(
        query="cleanup-search:page:1",
        response_json=json.dumps({"results": []}),
        expires_at=now - timedelta(seconds=10),
    )

    fresh_search = MovieSearchCache(
        query="fresh-search:page:1",
        response_json=json.dumps({"results": []}),
        expires_at=now + timedelta(seconds=3600),
    )

    expired_details = MovieDetailsCache(
        tmdb_id=999003,
        response_json=json.dumps({"id": 999003}),
        expires_at=now - timedelta(seconds=10),
    )

    fresh_details = MovieDetailsCache(
        tmdb_id=999004,
        response_json=json.dumps({"id": 999004}),
        expires_at=now + timedelta(seconds=3600),
    )

    db_session.add_all([expired_search, fresh_search, expired_details, fresh_details])
    db_session.commit()

    result = delete_expired_cache(db_session)

    assert result["deleted_search_cache"] >= 1
    assert result["deleted_details_cache"] >= 1
