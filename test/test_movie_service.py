from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.services.movies_service import (
    get_movie_details_with_cache,
    search_movies_with_cache,
)


class FakeTMDbClient:
    def __init__(self) -> None:
        self.search_calls = 0
        self.details_calls = 0

    def search_movies(self, query: str, *, page: int = 1) -> dict[str, Any]:
        self.search_calls += 1
        return {
            "page": page,
            "query_used": query,
            "results": [
                {
                    "id": 123,
                    "title": "Fake Batman",
                }
            ],
        }

    def get_movie_details(self, tmdb_id: int) -> dict[str, Any]:
        self.details_calls += 1
        return {
            "id": tmdb_id,
            "title": "Fake Movie Details",
        }


def test_search_movies_cache_miss_then_hit(db_session: Session) -> None:
    fake_client = FakeTMDbClient()

    source_1, data_1 = search_movies_with_cache(
        db_session,
        query="Batman",
        page=1,
        client=fake_client,
    )

    assert source_1 == "tmdb"
    assert data_1["results"][0]["title"] == "Fake Batman"
    assert fake_client.search_calls == 1

    source_2, data_2 = search_movies_with_cache(
        db_session,
        query="  BATMAN  ",
        page=1,
        client=fake_client,
    )

    assert source_2 == "cached"
    assert data_2["results"][0]["title"] == "Fake Batman"

    # Still 1 because second request used cache
    assert fake_client.search_calls == 1


def test_search_cache_separates_pages(db_session: Session) -> None:
    fake_client = FakeTMDbClient()

    source_1, _ = search_movies_with_cache(
        db_session,
        query="spider-man",
        page=1,
        client=fake_client,
    )

    source_2, _ = search_movies_with_cache(
        db_session,
        query="spider-man",
        page=2,
        client=fake_client,
    )

    assert source_1 == "tmdb"
    assert source_2 == "tmdb"

    # page 1 and page 2 should be separate cache entries
    assert fake_client.search_calls == 2


def test_movie_details_cache_miss_then_hit(db_session: Session) -> None:
    fake_client = FakeTMDbClient()

    source_1, data_1 = get_movie_details_with_cache(
        db_session,
        tmdb_id=123,
        client=fake_client,
    )

    assert source_1 == "tmdb"
    assert data_1["title"] == "Fake Movie Details"
    assert fake_client.details_calls == 1

    source_2, data_2 = get_movie_details_with_cache(
        db_session,
        tmdb_id=123,
        client=fake_client,
    )

    assert source_2 == "cache"
    assert data_2["title"] == "Fake Movie Details"

    # Still 1 because second request used cache
    assert fake_client.details_calls == 1
