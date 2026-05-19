from contextlib import asynccontextmanager
from app.api.routes_abuseipdb import router as abuseipdb_router  

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_admin import router as admin_router
from app.api.routes_analyze import router as analyze_router
from app.api.routes_auth import router as auth_router
from app.api.routes_dashboard import router as dashboard_router
from app.api.routes_hibp import router as hibp_router
from app.api.routes_news import router as news_router
from app.core.config import get_settings
from app.db.session import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title='SecRadar API',
    version='0.4.0',
    docs_url='/docs',
    redoc_url='/redoc',
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok'}


app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(news_router)
app.include_router(hibp_router)
app.include_router(analyze_router)
app.include_router(admin_router)
app.include_router(abuseipdb_router)