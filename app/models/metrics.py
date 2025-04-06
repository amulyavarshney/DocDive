from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class MetricBase(BaseModel):
    """Base metrics schema"""
    metric_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MetricCreate(MetricBase):
    """Schema for creating a metric"""
    value: float
    metadata: Optional[Dict[str, Any]] = None


class MetricResponse(MetricBase):
    """Schema for metric response"""
    value: float
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class DailyQueryVolume(BaseModel):
    """Schema for daily query volume"""
    date: str
    count: int


class AverageLatency(BaseModel):
    """Schema for average latency"""
    date: str
    avg_latency: float  # in milliseconds


class SuccessRate(BaseModel):
    """Schema for success rate"""
    date: str
    success_rate: float  # 0.0 to 1.0


class TopQueries(BaseModel):
    """Schema for top queries"""
    query_text: str
    count: int


class TopDocuments(BaseModel):
    """Schema for top documents"""
    document_id: str
    file_name: str
    count: int


class MetricsSummary(BaseModel):
    """Schema for metrics summary"""
    query_volume: List[DailyQueryVolume]
    latency: List[AverageLatency]
    success_rate: List[SuccessRate]
    top_queries: List[TopQueries]
    top_documents: List[TopDocuments] 