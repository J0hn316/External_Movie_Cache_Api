from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.cache_schema import CacheCleanupOut, CacheStatsOut
from app.services.cache_service import delete_expired_cache, get_cache_stats

router = APIRouter(prefix="/cache", tags=["cache"])


@router.get("/stats", response_model=CacheStatsOut)
def get_cache_stats_route(db: Session = Depends(get_db)) -> CacheStatsOut:
    return get_cache_stats(db)


@router.delete("/expired", response_model=CacheCleanupOut)
def delete_expired_cache_route(db: Session = Depends(get_db)) -> CacheCleanupOut:
    return delete_expired_cache(db)
