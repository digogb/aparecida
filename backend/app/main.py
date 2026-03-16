import importlib
import pkgutil
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Ionde Juridico", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
