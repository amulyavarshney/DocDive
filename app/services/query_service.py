import os
import uuid
import time
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from functools import lru_cache

from langchain.schema import Document
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings, AzureChatOpenAI, ChatOpenAI
from langchain_anthropic import ChatAnthropic

from app.db import mongodb
from app.models.query import QueryRequest, QueryResponse, QueryLog
from app.services.system_service import get_chroma_client, get_embedding_model, get_llm_model


# Define the QA prompt template
QA_PROMPT_TEMPLATE = """
You are a knowledgeable assistant that helps users find information from documents. Use only the information from the provided context to answer the question. If you don't know the answer or the information is not in the context, say "I don't have enough information to answer this question." and suggest what information might help.

Context information from documents:
{context}

Question: {question}

Provide a comprehensive and accurate answer based solely on the context provided. Include specific details from the context that support your answer. If referencing a specific part of the document, mention the source.

Answer:
"""

QA_PROMPT = PromptTemplate(
    template=QA_PROMPT_TEMPLATE,
    input_variables=["context", "question"]
)


async def get_document_collections(document_ids: Optional[List[str]] = None) -> List[str]:
    """Get list of collections to search"""
    if not document_ids:
        # Get all documents with completed embeddings
        documents = mongodb.documents_collection.find(
            {"embedding_status": "processed"}
        ).to_list(length=None)
        document_ids = [doc["document_id"] for doc in documents]
    
    # Convert document IDs to collection names
    return [f"doc_{doc_id}" for doc_id in document_ids]


async def create_vector_store(collection_name: str, embedding_model):
    """Create and validate a vector store for a collection"""
    chroma_client = get_chroma_client()
    
    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embedding_model,
        client=chroma_client
    )
    
    # Test the vector store with a simple query
    test_results = vector_store.similarity_search("test", k=1)
    if not test_results:
        raise ValueError(f"Vector store for {collection_name} returned no results")
    
    return vector_store


async def log_query_result(query_id: str, query_text: str, document_ids: List[str], 
                            answer: str, sources: List[Dict[str, Any]], 
                           latency: float, status: str, error_message: str = None):
    """Log query results to database"""
    query_log = QueryLog(
        query_id=query_id,
        query_text=query_text,
        document_ids=document_ids,
        answer=answer,
        sources=sources,
        latency=latency,
        status=status,
        error_message=error_message
    )
    await mongodb.log_query(query_log.model_dump())


async def perform_query(query_request: QueryRequest) -> QueryResponse:
    """Perform document query and return response with sources"""
    start_time = time.time()
    query_id = str(uuid.uuid4())
    
    try:
        # Get document collections to search
        collections = await get_document_collections(query_request.document_ids)

        if not collections:
            raise ValueError("No document collections available for querying")
        
        # Get embedding model
        embedding_model = await get_embedding_model()
        
        # Get LLM model
        llm = await get_llm_model()
        
        # Create vector store for each collection
        vector_stores = []
        for collection in collections:
            try:
                vector_store = await create_vector_store(collection, embedding_model)
                vector_stores.append(vector_store)
            except Exception as e:
                # Log but continue with other collections
                print(f"Warning: Failed to connect to collection {collection}: {str(e)}")
        
        if not vector_stores:
            raise ValueError("No valid vector stores could be created")
        
        # Combine vector stores
        # Create a new combined store with all documents
        combined_store = Chroma(
            collection_name=f"combined_{uuid.uuid4()}",
            embedding_function=embedding_model,
            client=get_chroma_client()
        )
        
        # Add documents from all stores to the combined store
        for store in vector_stores:
            try:
                # Get all documents from the store
                docs = store.get()
                if docs and docs.get('documents'):
                    # Add documents to combined store
                    combined_store.add_texts(
                        texts=docs['documents'],
                        metadatas=docs.get('metadatas', [{}] * len(docs['documents']))
                    )
            except Exception as e:
                raise ValueError(f"Failed to combine vector stores: {str(e)}")
        
        # Create retriever with proper configuration
        retriever = combined_store.as_retriever(
            search_kwargs={
                "k": query_request.top_k
            }
        )
        
        # Create and execute QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": QA_PROMPT}
        )
        
        # Perform the query
        result = await qa_chain.ainvoke({"query": query_request.query_text})
        
        # Extract sources
        sources = []
        for doc in result.get("source_documents", []):
            if not doc.page_content.strip():
                continue
                
            source = {
                "document_id": doc.metadata.get("document_id", ""),
                "file_name": doc.metadata.get("file_name", ""),
                "chunk_id": doc.metadata.get("chunk_id", 0),
                "content": doc.page_content,
                "keywords": doc.metadata.get("keywords", ""),
                "page": doc.metadata.get("page", 0),
            }
            sources.append(source)
        
        # Calculate latency
        latency = time.time() - start_time
        
        # Log successful query
        document_ids = set(doc["document_id"] for doc in sources)
        await log_query_result(
            query_id=query_id,
            query_text=query_request.query_text,
            document_ids=document_ids,
            answer=result.get("result", "No answer found."),
            sources=sources,
            latency=latency,
            status="success"
        )
        
        # Create response
        return QueryResponse(
            query_id=query_id,
            query_text=query_request.query_text,
            document_ids=list(document_ids),
            answer=result.get("result", "No answer found."),
            sources=sources,
            latency=latency
        )
        
    except Exception as e:
        # Calculate latency even for failed queries
        latency = time.time() - start_time
        
        # Log failed query
        await log_query_result(
            query_id=query_id,
            query_text=query_request.query_text,
            document_ids=[],
            answer=f"Error processing query: {str(e)}",
            sources=[],
            latency=latency,
            status="error",
            error_message=str(e)
        )
        
        # Return error response
        return QueryResponse(
            query_id=query_id,
            query_text=query_request.query_text,
            document_ids=[],
            answer=f"Error processing query: {str(e)}",
            sources=[],
            latency=latency
        )


async def get_query_history(limit: int = 100, skip: int = 0, sort: Optional[str] = None) -> Dict[str, Any]:
    """Get query history with pagination"""
    queries = await mongodb.get_queries(limit, skip, sort)
    total = mongodb.queries_collection.count_documents({})
    
    return {
        "queries": queries,
        "total": total
    }


async def format_query_response(query_log: Dict[str, Any]) -> Dict[str, Any]:
    """Format a query log entry into a response"""
    if query_log.get("status") == "success":
        # Use cached answer and sources if available
        if "answer" in query_log and "sources" in query_log:
            return query_log
            
        # Build a response from the log for successful queries without cached data
        return {
            "query_id": query_log["query_id"],
            "query_text": query_log["query_text"],
            "answer": "This query was successful, but the detailed answer is no longer available.",
            "sources": [
                {
                    "document_id": doc_id,
                    "file_name": "Unknown", 
                    "chunk_id": 0,
                    "content": "Content not available..."
                } 
                for doc_id in query_log.get("document_ids", [])
            ],
            "latency": query_log.get("latency", 0.0),
            "timestamp": query_log.get("timestamp", datetime.utcnow())
        }
    
    # For failed queries
    return {
        "query_id": query_log["query_id"],
        "query_text": query_log["query_text"],
        "answer": f"Query failed: {query_log.get('error_message', 'Unknown error')}",
        "sources": [],
        "latency": query_log.get("latency", 0.0),
        "timestamp": query_log.get("timestamp", datetime.utcnow())
    }


async def get_query(query_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific query by ID"""
    query_log = await mongodb.get_query(query_id)
    
    if not query_log:
        return None
    
    try:
        return await format_query_response(query_log)
    except Exception as e:
        print(f"Error formatting query response: {str(e)}")
        return query_log  # Return the raw log if formatting fails