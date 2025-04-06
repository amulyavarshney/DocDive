from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    """Base document schema"""
    file_name: str
    file_type: str
    file_size: int
    document_id: str


class DocumentCreate(DocumentBase):
    """Schema for creating a document"""
    content_type: str
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    file_path: str
    embedding_status: str = "pending"


class DocumentResponse(DocumentBase):
    """Schema for document response"""
    upload_date: datetime
    embedding_status: str
    chunk_count: Optional[int] = None
    
    class Config:
        from_attributes = True


class DocumentList(BaseModel):
    """Schema for list of documents"""
    documents: List[DocumentResponse]
    total: int


class DocumentsSearch(BaseModel):
    """Schema for searching documents"""
    query: str
    limit: int = 10
    skip: int = 0 