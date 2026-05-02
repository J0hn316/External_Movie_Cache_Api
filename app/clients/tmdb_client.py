from __future__ import annotations

from typing import Any

import httpx

from app.core.config import settings


class TMDbClientError(Exception):
    pass


class TMDbClient:
    def __init__(
        self,
        *,
        base_url: str = settings.tmdb_base_url,
        api_key: str = settings.tmdb_api_key,
        timeout_seconds: int = settings.http_timeout_seconds,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds

    def _params_with_api_key(
        self, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        if not self.api_key:
            raise TMDbClientError("TMDb API key is missing")

        final_params = dict(params or {})
        final_params["api_key"] = self.api_key
        return final_params

    def _get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"

        try:
            response = httpx.get(
                url,
                params=self._params_with_api_key(params),
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            body = exc.response.text
            raise TMDbClientError(f"TMDb returned HTTP {status_code}: {body}") from exc

        except httpx.TimeoutException as exc:
            raise TMDbClientError("TMDb request timed out") from exc

        except httpx.HTTPError as exc:
            raise TMDbClientError("TMDb request failed") from exc

    def search_movies(self, query: str, *, page: int = 1) -> dict[str, Any]:
        return self._get(
            "/search/movie",
            params={
                "query": query,
                "page": page,
                "include_adult": False,
                "language": "en-US",
            },
        )

    def get_movie_details(self, tmdb_id: int) -> dict[str, Any]:
        return self._get(
            f"/movie/{tmdb_id}",
            params={
                "language": "en-US",
            },
        )
