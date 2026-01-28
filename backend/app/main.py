"""VisuaLearn FastAPI application."""

import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.diagram import router as diagram_router
from app.config import settings


# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.log_level,
)
logger.add(
    f"{settings.temp_dir}/../logs/diagram_{{time}}.log",
    rotation="500 MB",
    retention="7 days",
    level="DEBUG",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("VisuaLearn backend starting")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Log level: {settings.log_level}")
    logger.info(f"Temp directory: {settings.temp_dir}")
    yield
    # Shutdown
    logger.info("VisuaLearn backend shutting down")


# Create FastAPI app
app = FastAPI(
    title="VisuaLearn API",
    description="AI-Powered Educational Diagram Generation",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(diagram_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "visualearn",
        "version": "0.1.0",
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "VisuaLearn API",
        "version": "0.1.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
