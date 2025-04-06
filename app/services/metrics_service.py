import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from app.core.config import settings
from app.db import mongodb
from app.models.metrics import (
    DailyQueryVolume, AverageLatency, SuccessRate,
    TopQueries, TopDocuments, MetricsSummary
)


async def log_metric(metric_type: str, value: float, metadata: Optional[Dict[str, Any]] = None) -> str:
    """Log a metric to the database"""
    metric_data = {
        "metric_type": metric_type,
        "value": value,
        "metadata": metadata or {},
        "timestamp": datetime.utcnow()
    }
    
    return await mongodb.log_metric(metric_data)


async def get_daily_query_volume(days: int = 7) -> List[DailyQueryVolume]:
    """Get query volume per day for the last N days"""
    results = await mongodb.get_daily_query_volume(days)
    
    # Format results
    return [
        DailyQueryVolume(date=item["_id"], count=item["count"])
        for item in results
    ]


async def get_average_latency(days: int = 7) -> List[AverageLatency]:
    """Get average latency per day for the last N days"""
    results = await mongodb.get_average_latency(days)
    
    # Format results
    return [
        AverageLatency(date=item["_id"], avg_latency=item["avg_latency"])
        for item in results
    ]


async def get_success_rate(days: int = 7) -> List[SuccessRate]:
    """Get success rate per day for the last N days"""
    results = await mongodb.get_success_rate(days)
    
    # Format results
    return [
        SuccessRate(date=item["_id"], success_rate=item["success_rate"])
        for item in results
    ]


async def get_top_queries(limit: int = 10) -> List[TopQueries]:
    """Get top queried questions"""
    results = await mongodb.get_top_queries(limit)
    
    # Format results
    return [
        TopQueries(query_text=item["_id"], count=item["count"])
        for item in results
    ]


async def get_top_documents(limit: int = 10) -> List[TopDocuments]:
    """Get top queried documents"""
    results = await mongodb.get_top_documents(limit)
    
    # Format results
    return [
        TopDocuments(
            document_id=item["document_id"],
            file_name=item["file_name"],
            count=item["count"]
        )
        for item in results
    ]


async def get_metrics_summary(days: int = 7, limit: int = 10) -> MetricsSummary:
    """Get summary of all metrics"""
    # Get all metrics in parallel using asyncio.gather
    import asyncio
    
    query_volume, latency, success_rate, top_queries, top_documents = await asyncio.gather(
        get_daily_query_volume(days),
        get_average_latency(days),
        get_success_rate(days),
        get_top_queries(limit),
        get_top_documents(limit)
    )
    
    # Return summary
    return MetricsSummary(
        query_volume=query_volume,
        latency=latency,
        success_rate=success_rate,
        top_queries=top_queries,
        top_documents=top_documents
    )


async def fill_missing_dates(data: List[Dict[str, Any]], days: int = 7) -> List[Dict[str, Any]]:
    """Fill in missing dates with zero values"""
    # Create a map of existing dates
    date_map = {item["date"]: item for item in data}
    
    # Generate all dates in the range
    end_date = datetime.utcnow()
    result = []
    
    for i in range(days):
        date = (end_date - timedelta(days=i)).strftime("%Y-%m-%d")
        if date in date_map:
            result.append(date_map[date])
        else:
            # Create a zero entry for missing date
            result.append({"date": date, "value": 0})
    
    # Sort by date
    result.sort(key=lambda x: x["date"])
    
    return result 