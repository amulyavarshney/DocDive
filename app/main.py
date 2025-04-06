import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(document_routes.router, prefix="/api", tags=["documents"])
app.include_router(query_routes.router, prefix="/api", tags=["queries"])
app.include_router(metrics_routes.router, prefix="/api", tags=["metrics"])
app.include_router(system_routes.router, prefix="/api", tags=["system"])
# Mount static files if needed
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 