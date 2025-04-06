import asyncio
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from datetime import datetime

from app.core.config import settings
from app.services import query_service
from app.models.query import QueryRequest, QueryResponse, QueryHistory

router = APIRouter()


@router.post("/query", response_model=QueryResponse, tags=["queries"])
async def query_documents(query: QueryRequest):
    """
    Query documents using LLM-powered retrieval.
    
    This endpoint performs a semantic search on the indexed documents and returns
    an answer along with relevant sources.
    """
    try:
        response = await query_service.perform_query(query)
        return response
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queries", response_model=QueryHistory, tags=["queries"])
async def get_query_history(
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0)
):
    """
    Get query history with pagination.
    """
    try:
        result = await query_service.get_query_history(limit, skip)
        return QueryHistory(queries=result["queries"], total=result["total"])
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queries/{query_id}", response_model=QueryResponse, tags=["queries"])
async def get_query(query_id: str):
    """
    Get a specific query by ID.
    """
    try:
        query_data = await query_service.get_query(query_id)
        
        if not query_data:
            raise HTTPException(status_code=404, detail=f"Query not found: {query_id}")
        
        return QueryResponse(**query_data)
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))