from __future__ import annotations

from pydantic import BaseModel


class CacheStatsOut(BaseModel):
    search_cache_count: int
    details_cache_count: int
    expired_search_cache_count: int
    expired_details_cache_count: int


class CacheCleanupOut(BaseModel):
    deleted_search_cache: int
    deleted_details_cache: int
