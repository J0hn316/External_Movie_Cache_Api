from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class MovieApiResponse(BaseModel):
    source: str
    data: dict[str, Any]
