from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.database import engine, Base

from app.core.limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.api.Product import router as ProductRouter
from app.api.chat import router as chatRouter

app = FastAPI(title="Inventory MCP")

app.state.limiter = limiter

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(SlowAPIMiddleware)

app.include_router(ProductRouter)
app.include_router(chatRouter)
