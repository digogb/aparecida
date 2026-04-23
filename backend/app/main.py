import importlib
import pkgutil
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

app = FastAPI(title="Ione Juridico", version="1.0.0")
_scheduler = AsyncIOScheduler(timezone="America/Fortaleza")

_cors_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
if not _cors_origins:
    _cors_origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auto-discovery de routers
routers_path = Path(__file__).parent / "routers"
for info in pkgutil.iter_modules([str(routers_path)]):
    if info.name.startswith("_"):
        continue
    try:
        mod = importlib.import_module(f"app.routers.{info.name}")
        if hasattr(mod, "router"):
            app.include_router(
                mod.router,
                prefix=getattr(mod, "PREFIX", "/api"),
                tags=getattr(mod, "TAGS", [info.name]),
            )
        if hasattr(mod, "ws_router"):
            app.include_router(mod.ws_router)
    except Exception as e:
        print(f"[warn] Router {info.name}: {e}")


@app.on_event("startup")
async def startup() -> None:
    from app.database import async_session
    try:
        from app.seeds import run_seeds
        async with async_session() as db:
            await run_seeds(db)
    except Exception as e:
        print(f"[warn] Seeds: {e}")


@app.on_event("startup")
async def start_gmail_poller() -> None:
    import logging
    from datetime import datetime, timezone
    from app.services.gmail_poller import poll_inbox

    logging.basicConfig(level=logging.INFO)

    _scheduler.add_job(
        poll_inbox,
        "interval",
        minutes=5,
        id="gmail_poller",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
        next_run_time=datetime.now(timezone.utc),
    )
    if not _scheduler.running:
        _scheduler.start()


@app.on_event("shutdown")
async def stop_gmail_poller() -> None:
    if _scheduler.running:
        _scheduler.shutdown(wait=False)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
