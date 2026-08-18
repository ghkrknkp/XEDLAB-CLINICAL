import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import get_settings
from app.core.logging import logger, log_event
from app.database.database import init_db
from app.api import auth, upload, reports, jobs, qa, health

settings = get_settings()

app = FastAPI(
    title="AI Medical Report Analyzer API",
    description=(
        "Production-style, non-diagnostic AI document intelligence web application. "
        "Extracts structured laboratory findings from medical reports, deterministically "
        "validates values against printed reference ranges, generates grounded patient-friendly "
        "explanations, and provides isolated RAG-based report Q&A."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration — allow all origins for easy frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def root():
    return {
        "status": "healthy",
        "app": "XEDLAB Clinical AI Medical Report Analyzer API",
        "version": "1.0.0",
        "docs": "/docs",
        "health_check": "/api/health",
    }


@app.get("/api", include_in_schema=False)
def api_root():
    return {
        "status": "healthy",
        "message": "AI Medical Report Analyzer API endpoints active.",
        "health": "/api/health",
    }


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled internal error on %s: %s", request.url.path, str(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {type(exc).__name__}: {str(exc)}"},
    )


@app.on_event("startup")
def on_startup():
    try:
        init_db()
        log_event("application_started", status="healthy")
        print("✅ Database tables initialized successfully.")
    except Exception as e:
        print(f"❌ Database init failed: {e}")
        raise


# Register Routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(jobs.router)
app.include_router(reports.router)
app.include_router(qa.router)
