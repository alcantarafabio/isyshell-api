from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import init_db, seed_default_data
from app.routes import scripts, execute, logs, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_default_data()
    yield


app = FastAPI(
    title="IsyShell API",
    description="API para executar scripts Bash de forma segura e auditada. Autenticação via header `X-Isy-Token`.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)  # open for hackathon — restrict in production

app.include_router(scripts.router)
app.include_router(execute.router)
app.include_router(logs.router)
app.include_router(admin.router)


@app.get("/", tags=["Health"])
def health_check():
    return {
        "service": "IsyShell API",
        "version": "1.0.0",
        "status": "online",
    }
