from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.clients.tmdb_client import TMDbClientError
from app.db.session import get_db
from app.schemas.movies_schema import MovieApiResponse
from app.services.movies_service import (
    get_movie_details_with_cache,
    search_movies_with_cache,
)

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("/search", response_model=MovieApiResponse)
def search_movies_route(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db),
) -> MovieApiResponse:
    try:
        source, data = search_movies_with_cache(db, query=q, page=page)
    except TMDbClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return MovieApiResponse(source=source, data=data)


@router.get("/{tmdb_id}", response_model=MovieApiResponse)
def get_movie_details_route(
    tmdb_id: int,
    db: Session = Depends(get_db),
) -> MovieApiResponse:
    try:
        source, data = get_movie_details_with_cache(db, tmdb_id=tmdb_id)
    except TMDbClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return MovieApiResponse(source=source, data=data)
