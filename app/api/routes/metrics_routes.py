import asyncio
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.services import metrics_service
from app.models.metrics import (
    MetricResponse, DailyQueryVolume, AverageLatency, 
    SuccessRate, TopQueries, TopDocuments, MetricsSummary
)

router = APIRouter()


@router.get("/metrics/summary", response_model=MetricsSummary, tags=["metrics"])
async def get_metrics_summary(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Get a summary of all metrics for dashboard display.
    """
    try:
        summary = await metrics_service.get_metrics_summary(days, limit)
        return summary
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/query-volume", response_model=List[DailyQueryVolume], tags=["metrics"])
async def get_query_volume(
    days: int = Query(7, ge=1, le=30)
):
    """
    Get query volume per day for the last N days.
    """
    try:
        query_volume = await metrics_service.get_daily_query_volume(days)
        return query_volume
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/latency", response_model=List[AverageLatency], tags=["metrics"])
async def get_latency(
    days: int = Query(7, ge=1, le=30)
):
    """
    Get average latency per day for the last N days.
    """
    try:
        latency = await metrics_service.get_average_latency(days)
        return latency
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/success-rate", response_model=List[SuccessRate], tags=["metrics"])
async def get_success_rate(
    days: int = Query(7, ge=1, le=30)
):
    """
    Get success rate per day for the last N days.
    """
    try:
        success_rate = await metrics_service.get_success_rate(days)
        return success_rate
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/top-queries", response_model=List[TopQueries], tags=["metrics"])
async def get_top_queries(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Get top queried questions.
    """
    try:
        top_queries = await metrics_service.get_top_queries(days, limit)
        return top_queries
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/top-documents", response_model=List[TopDocuments], tags=["metrics"])
async def get_top_documents(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Get top queried documents.
    """
    try:
        top_documents = await metrics_service.get_top_documents(days, limit)
        return top_documents
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 