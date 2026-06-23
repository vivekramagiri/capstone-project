"""
FastAPI microservice for loan application processing
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from src.config import settings
from src.api.routes import router
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Loan Approval AI System",
    description="Multi-Agent Agentic AI System for Intelligent Loan Approval",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Starting Loan Approval API")
    try:
        settings.validate()
        logger.info("Configuration validated")
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Loan Approval API")


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "loan-approval-ai",
        "version": "1.0.0",
    }


# Include routes
app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level=settings.API_LOG_LEVEL.lower(),
    )
