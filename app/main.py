import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from app.api.routes import document_routes, query_routes, metrics_routes, system_routes
from app.core.config import settings

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Document Search & Q&A Platform",
    description="LLM-powered document search with metrics dashboard",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(document_routes.router, prefix="/api", tags=["documents"])
app.include_router(query_routes.router, prefix="/api", tags=["queries"])
app.include_router(metrics_routes.router, prefix="/api", tags=["metrics"])
app.include_router(system_routes.router, prefix="/api", tags=["system"])

# Mount static files
# app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", tags=["health"], response_model=dict)
async def health_check() -> JSONResponse:
    """Health check endpoint"""
    return JSONResponse(content={"status": "healthy", "version": "1.0.0"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG) 