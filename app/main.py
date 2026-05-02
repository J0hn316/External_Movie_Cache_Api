from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import settings
from app.db.session import engine
from app.api.movies_api import router as movies_router

app = FastAPI(title=settings.app_name)
app.include_router(movies_router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ok"}
