import os
import uuid
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional, BinaryIO
from PyPDF2 import PdfReader
import pandas as pd
import mistune

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_chroma import Chroma
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.document_loaders import TextLoader, CSVLoader, PyMuPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings, HuggingFaceInstructEmbeddings

from app.core.config import settings
from app.db import mongodb
from app.models.document import DocumentCreate, DocumentResponse
from app.services.system_service import get_chroma_client, get_embedding_model


async def save_uploaded_file(file: BinaryIO, filename: str) -> str:
    """Save an uploaded file to disk and return the file path"""
    file_extension = os.path.splitext(filename)[1].lower()
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_FOLDER, unique_filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    return file_path


async def get_file_content(file_path: str, file_type: str) -> str:
    """Extract content from file based on its type"""
    extractors = {
        "pdf": extract_pdf_text,
        "md": extract_markdown_text,
        "markdown": extract_markdown_text,
        "csv": extract_csv_text,
        "txt": extract_text_file
    }
    
    if file_type not in extractors:
        raise ValueError(f"Unsupported file type: {file_type}")
        
    return await extractors[file_type](file_path)


async def extract_pdf_text(file_path: str) -> str:
    """Extract text from PDF file"""
    text = ""
    reader = PdfReader(file_path)
    for page in reader.pages:
        text += page.extract_text()
    return text


async def extract_markdown_text(file_path: str) -> str:
    """Extract text from Markdown file"""
    with open(file_path, "r", encoding="utf-8") as f:
        md_content = f.read()
    html = mistune.html(md_content)
    return html.replace("<p>", "").replace("</p>", "\n\n").replace("<br>", "\n")


async def extract_csv_text(file_path: str) -> str:
    """Extract text from CSV file"""
    df = pd.read_csv(file_path)
    return df.to_string()


async def extract_text_file(file_path: str) -> str:
    """Extract text from plain text file"""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


async def create_document_chunks(file_path: str, file_type: str) -> List[Document]:
    """Split document content into chunks"""
    if file_type == "pdf":
        loader = PyMuPDFLoader(file_path)
        documents = loader.load()
    elif file_type == "csv":
        loader = CSVLoader(file_path)
        documents = loader.load()
    else:
        # For text and markdown, first get content then load
        content = await get_file_content(file_path, file_type)
        temp_file = f"{file_path}.tmp"
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(content)
            loader = TextLoader(temp_file)
            documents = loader.load()
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)  # Clean up temp file
    
    # Split the documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.DEFAULT_CHUNK_SIZE,
        chunk_overlap=settings.DEFAULT_CHUNK_OVERLAP,
        length_function=len,
    )
    return text_splitter.split_documents(documents)


async def create_document_record(
    filename: str, file_size: int, file_path: str, content_type: str
) -> DocumentCreate:
    """Create document metadata record"""
    file_type = os.path.splitext(filename)[1][1:].lower()
    document_id = str(uuid.uuid4())
    
    return DocumentCreate(
        document_id=document_id,
        file_name=filename,
        file_type=file_type,
        file_size=file_size,
        content_type=content_type,
        file_path=file_path,
        upload_date=datetime.utcnow(),
        embedding_status="pending"
    )

async def store_document_embeddings(document_id: str, chunks: List[Document]) -> str:
    """Store document chunks in vector database with embeddings"""
    # Get the document to update
    document = await mongodb.get_document(document_id)
    if not document:
        raise ValueError(f"Document not found: {document_id}")
    
    # Get embedding model
    embedding_model = await get_embedding_model()
    
    # Use document_id as collection name to isolate different documents
    collection_name = f"doc_{document_id}"
    
    # Add metadata to each chunk to track source document
    for i, chunk in enumerate(chunks):
        if not hasattr(chunk, "metadata"):
            chunk.metadata = {}
        chunk.metadata.update({
            "document_id": document_id,
            "chunk_id": i,
            "file_name": document["file_name"]
        })
    
    # Store in Chroma vectorstore with retry logic
    max_retries = 3
    retry_count = 0
    base_delay = 2  # Base delay in seconds
    max_delay = 20  # Maximum delay in seconds
    
    while retry_count < max_retries:
        try:
            # Get singleton Chroma client
            chroma_client = get_chroma_client()
            
            # Create or get collection
            try:
                collection = chroma_client.get_collection(name=collection_name)
            except:
                collection = chroma_client.create_collection(name=collection_name)
            
            vectorstore = Chroma(
                collection_name=collection_name,
                embedding_function=embedding_model,
                client=chroma_client
            )
            
            # Add documents in batches to avoid memory issues
            batch_size = 50
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i+batch_size]
                vectorstore.add_documents(documents=batch)

            # Verify documents were added
            doc_count = collection.count()
            if doc_count == 0:
                raise ValueError("No documents were added to the collection")
            
            # Update document status in MongoDB
            mongodb.documents_collection.update_one(
                {"document_id": document_id},
                {
                    "$set": {
                        "embedding_status": "completed",
                        "chunk_count": len(chunks),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return document_id
            
        except Exception as e:
            retry_count += 1
            error_msg = f"Error storing embeddings (attempt {retry_count}/{max_retries}): {str(e)}"
            
            if retry_count < max_retries:
                delay = min(max_delay, base_delay * (2 ** (retry_count - 1)))
                await asyncio.sleep(delay)
            else:
                # If we've exhausted our retries, update the document status and raise the error
                error_msg = f"Failed to store embeddings after {max_retries} attempts: {str(e)}"
                await update_document_status(document_id, "error", error_msg)
                raise ValueError(error_msg)


async def update_document_status(document_id: str, status: str, error_message: str = None):
    """Helper to update document status in MongoDB"""
    update = {
        "embedding_status": status,
        "updated_at": datetime.utcnow()
    }
    
    if error_message:
        update["error_message"] = error_message
        
    mongodb.documents_collection.update_one(
        {"document_id": document_id},
        {"$set": update}
    )


async def process_document(document: DocumentCreate) -> None:
    """Process document and create embeddings asynchronously"""
    try:
        # Insert document record into database
        await mongodb.insert_document(document.dict())
        
        # Create document chunks
        chunks = await create_document_chunks(document.file_path, document.file_type)
        
        # Store embeddings
        await store_document_embeddings(document.document_id, chunks)
    except Exception as e:
        await update_document_status(document.document_id, "error", str(e))
        raise


async def get_all_documents(limit: int = 100, skip: int = 0) -> Dict[str, Any]:
    """Get all documents with pagination"""
    documents = await mongodb.get_all_documents(limit, skip)
    total = mongodb.documents_collection.count_documents({})
    
    return {
        "documents": documents,
        "total": total
    }


async def get_document(document_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific document by ID"""
    return await mongodb.get_document(document_id)


async def delete_document(document_id: str) -> bool:
    """Delete document and its embeddings"""
    # Get document to check if it exists
    document = await mongodb.get_document(document_id)
    if not document:
        return False
    
    # Delete document file
    if os.path.exists(document["file_path"]):
        os.remove(document["file_path"])
    
    # Delete from MongoDB
    await mongodb.delete_document(document_id)
    
    # Delete from vector store
    try:
        chroma_client = get_chroma_client()
        collection_name = f"doc_{document_id}"
        if collection_name in chroma_client.list_collections():
            chroma_client.delete_collection(collection_name)
    except Exception:
        # Continue even if vector store deletion fails
        pass
    
    return True 