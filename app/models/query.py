from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class QueryBase(BaseModel):
    """Base query schema"""
    query_text: str


class QueryRequest(QueryBase):
    """Schema for query request"""
    top_k: int = 4
    similarity_threshold: float = 0.7
    document_ids: Optional[List[str]] = None  # If provided, search only in these documents


class QueryResponse(BaseModel):
    """Schema for query response"""
    query_id: str
    query_text: str
    document_ids: List[str]
    answer: str
    sources: List[Dict[str, Any]]  # Citations with source document information
    latency: float  # Response time in seconds
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class QueryLog(BaseModel):
    """Schema for query log entry"""
    query_id: str
    query_text: str
    document_ids: List[str]
    answer: str
    sources: List[Dict[str, Any]]  # Citations with source document information
    latency: float
    status: str  # success, error
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class QueryHistory(BaseModel):
    """Schema for query history"""
    queries: List[QueryLog]
    total: int 