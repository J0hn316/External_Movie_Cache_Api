from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class MovieSearchCache(Base):
    __tablename__ = "movie_search_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    query: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )

    response_json: Mapped[str] = mapped_column(Text, nullable=False)

    cached_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )


class MovieDetailsCache(Base):
    __tablename__ = "movie_details_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    tmdb_id: Mapped[int] = mapped_column(
        Integer, unique=True, index=True, nullable=False
    )

    response_json: Mapped[str] = mapped_column(Text, nullable=False)

    cached_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
