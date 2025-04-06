from fastapi import APIRouter, HTTPException, Query, Depends
from app.services import system_service

router = APIRouter()

@router.get("/diagnostics", tags=["system"])
async def run_diagnostics():
    """
    Test all service connections and return diagnostic information.
    
    This endpoint performs connection tests to MongoDB, Azure OpenAI, and ChromaDB
    to help diagnose connection issues.
    """
    try:
        results = await system_service.test_connections()
        return {"status": "success", "diagnostics": results}
    
    except Exception as e:
        return {
            "status": "error", 
            "message": str(e),
            "diagnostics": {"error": str(e)}
        }


@router.post("/reset-chromadb", tags=["system"])
async def reset_chroma_database():
    """
    Reset the ChromaDB storage directory.
    
    This endpoint creates a backup of the existing ChromaDB directory and creates
    a new empty one to fix corruption issues. Note that this will require re-embedding
    all documents.
    """
    try:
        result = await system_service.reset_chroma_db()
        return result
    
    except Exception as e:
        return {
            "status": "error", 
            "message": str(e)
        }


@router.post("/reset-mongodb", tags=["system"])
async def reset_mongo_database():
    """
    Reset the MongoDB database.
    
    This endpoint drops all collections in the MongoDB database and recreates them
    with proper indexes. Note that this will delete all stored documents and queries.
    """
    try:
        result = await system_service.reset_mongo_db()
        return result
    
    except Exception as e:
        return {
            "status": "error", 
            "message": str(e)
        } 