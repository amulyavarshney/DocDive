import asyncio
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Depends, status
from fastapi.responses import JSONResponse
from datetime import datetime

from app.core.config import settings
from app.services import query_service
from app.models.query import QueryRequest, QueryResponse, QueryHistory

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/query", 
    response_model=QueryResponse, 
    status_code=status.HTTP_200_OK,
    tags=["queries"],
    responses={
        400: {"description": "Bad request - Invalid parameters"},
        500: {"description": "Internal server error"}
    }
)
async def query_documents(query: QueryRequest) -> QueryResponse:
    """
    Query documents using LLM-powered retrieval.
    
    This endpoint performs a semantic search on the indexed documents and returns
    an answer along with relevant sources.
    """
    try:
        logger.info(f"Processing query: {query.query_text[:50]}...")
        response = await query_service.perform_query(query)
        return response
    
    except ValueError as e:
        logger.warning(f"Invalid query parameters: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(e)
        )
    
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to process query: {str(e)}"
        )


@router.get(
    "/queries", 
    response_model=QueryHistory, 
    status_code=status.HTTP_200_OK,
    tags=["queries"],
    response_description="List of previous queries with pagination",
    responses={
        500: {"description": "Internal server error"}
    }
)
async def get_query_history(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of queries to return"),
    skip: int = Query(0, ge=0, description="Number of queries to skip")
) -> QueryHistory:
    """
    Get query history with pagination.
    """
    try:
        result = await query_service.get_query_history(limit, skip)
        return QueryHistory(queries=result["queries"], total=result["total"])
    
    except Exception as e:
        logger.error(f"Error retrieving query history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to retrieve query history: {str(e)}"
        )


@router.get(
    "/queries/{query_id}", 
    response_model=QueryResponse, 
    status_code=status.HTTP_200_OK,
    tags=["queries"],
    response_description="Details of a specific query",
    responses={
        404: {"description": "Query not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_query(query_id: str) -> QueryResponse:
    """
    Get a specific query by ID.
    """
    try:
        query_data = await query_service.get_query(query_id)
        
        if not query_data:
            logger.warning(f"Query not found: {query_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Query not found: {query_id}"
            )
        
        return QueryResponse(**query_data)
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error retrieving query {query_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to retrieve query: {str(e)}"
        )