"""AI Service FastAPI Application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.api.routes import router
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="AgentTwinOps AI Service",
        description="Multi-agent AI service for Digital Twin operations",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(router)
    
    @app.on_event("startup")
    async def startup_event():
        logger.info("🚀 AI Service starting up...")
        logger.info(f"Environment: {settings.AI_SERVICE_ENV}")
        logger.info(f"Backend API: {settings.BACKEND_API_URL}")
        logger.info(f"Model: {settings.AI_MODEL}")
        logger.info(f"Real ML Models: {settings.ENABLE_REAL_ML_MODELS}")
        
        if not settings.OPENAI_API_KEY and not settings.ANTHROPIC_API_KEY:
            logger.warning("⚠️  No AI provider API key configured - using deterministic fallback")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("🛑 AI Service shutting down...")
    
    @app.get("/")
    async def root():
        return {
            "service": "AgentTwinOps AI Service",
            "status": "running",
            "version": "1.0.0",
            "docs": "/docs",
        }
    
    @app.get("/status")
    async def get_status():
        """Get AI service status including LLM configuration"""
        from app.agents.base import BaseAgent
        
        # Check LLM availability
        test_agent = BaseAgent("test")
        llm_status = "ACTIVE" if test_agent.llm else "NOT_CONFIGURED"
        
        # Determine which provider would be used
        llm_provider = None
        if settings.OPENAI_API_KEY:
            llm_provider = "OpenAI"
        elif settings.ANTHROPIC_API_KEY:
            llm_provider = "Anthropic" 
        
        return {
            "service": "AgentTwinOps AI Service",
            "status": "healthy",
            "mode": settings.AI_SERVICE_MODE,
            "backend": settings.BACKEND_API_URL,
            "llm": {
                "status": llm_status,
                "provider": llm_provider,
                "model": settings.AI_MODEL if llm_provider else None,
                "note": "Add OPENAI_API_KEY or ANTHROPIC_API_KEY to .env to activate LLM" if llm_status == "NOT_CONFIGURED" else None
            },
            "features": {
                "real_ml_models": settings.ENABLE_REAL_ML_MODELS,
                "langsmith_tracing": settings.ENABLE_LANGSMITH_TRACING,
            }
        }
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.AI_SERVICE_HOST,
        port=settings.AI_SERVICE_PORT,
        reload=settings.is_development,
    )
