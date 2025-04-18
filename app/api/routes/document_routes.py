import os
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Query, Depends, status
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.services import document_service
from app.models.document import DocumentResponse, DocumentList

router = APIRouter()


@router.post(
    "/documents/upload", 
    response_model=DocumentResponse, 
    status_code=status.HTTP_201_CREATED,
    tags=["documents"]
)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
) -> DocumentResponse:
    """
    Upload a document for processing and indexing.
    
    The document will be processed asynchronously, and its embeddings will be stored
    for later retrieval.
    """
    # Validate file size
    content = await file.read()
    file_size = len(content)
    
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds the maximum allowed size ({settings.MAX_UPLOAD_SIZE / (1024 * 1024):.1f}MB)"
        )
    
    # Reset file position after reading
    await file.seek(0)
    
    # Validate file type
    filename = file.filename
    file_extension = os.path.splitext(filename)[1][1:].lower()
    
    if file_extension not in settings.SUPPORTED_DOCUMENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: {file_extension}. Supported types: {', '.join(settings.SUPPORTED_DOCUMENT_TYPES)}"
        )
    
    try:
        # Save file to disk
        file_path = await document_service.save_uploaded_file(file, filename)
        
        # Create document record
        document = await document_service.create_document_record(
            filename=filename,
            file_size=file_size,
            file_path=file_path,
            content_type=file.content_type
        )
        
        # Process document in background
        background_tasks.add_task(document_service.process_document, document)
        
        # Convert to response model
        response = DocumentResponse(
            document_id=document.document_id,
            file_name=document.file_name,
            file_type=document.file_type,
            file_size=document.file_size,
            upload_date=document.upload_date,
            embedding_status=document.embedding_status
        )
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/documents", 
    response_model=DocumentList, 
    tags=["documents"],
    response_description="List of documents with pagination"
)
async def get_documents(
    limit: int = Query(100, ge=1, le=1000, description="Number of documents to return"),
    skip: int = Query(0, ge=0, description="Number of documents to skip")
) -> DocumentList:
    """
    Get a list of all uploaded documents with pagination.
    """
    try:
        result = await document_service.get_all_documents(limit, skip)
        return DocumentList(documents=result["documents"], total=result["total"])
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/documents/stats", 
    tags=["documents"],
    status_code=status.HTTP_200_OK,
    response_description="Document count statistics by status"
)
async def get_document_stats() -> Dict[str, int]:
    """
    Get document count statistics by embedding status.
    
    Returns counts for processed, pending, and error documents.
    """
    try:
        stats = await document_service.get_document_status_counts()
        return stats
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get(
    "/documents/types", 
    tags=["documents"],
    status_code=status.HTTP_200_OK,
    response_description="Document distribution by file type"
)
async def get_document_types() -> List[Dict[str, Any]]:
    """
    Get document distribution by file type.
    
    Returns counts for each file type (pdf, txt, csv, etc.)
    """
    try:
        distribution = await document_service.get_document_type_distribution()
        return distribution
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 

@router.get(
    "/documents/{document_id}", 
    response_model=DocumentResponse, 
    tags=["documents"],
    responses={
        404: {"description": "Document not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_document(document_id: str) -> DocumentResponse:
    """
    Get a specific document by ID.
    """
    try:
        document = await document_service.get_document(document_id)
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Document not found: {document_id}"
            )
        
        return DocumentResponse(**document)
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete(
    "/documents/{document_id}", 
    tags=["documents"],
    status_code=status.HTTP_200_OK,
    response_description="Document deletion confirmation",
    responses={
        404: {"description": "Document not found"},
        500: {"description": "Internal server error"}
    }
)
async def delete_document(document_id: str) -> JSONResponse:
    """
    Delete a document and its embeddings.
    """
    try:
        success = await document_service.delete_document(document_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Document not found: {document_id}"
            )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "success", "message": f"Document {document_id} deleted successfully"}
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 