import os
import uuid
import time
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from functools import lru_cache

from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings, AzureChatOpenAI, ChatOpenAI
from langchain_anthropic import ChatAnthropic
from chromadb.config import Settings
import chromadb

from app.core.config import settings
from app.db import mongodb
from app.services.chroma_client import get_chroma_client

@lru_cache(maxsize=1)
def get_chroma_client():
    """Get a singleton instance of Chroma client with consistent settings"""
    # Ensure the persist directory exists
    os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)
    
    # Create consistent settings
    client_settings = Settings(
        persist_directory=settings.VECTOR_DB_PATH,
        anonymized_telemetry=False,
        allow_reset=True,
        is_persistent=True
    )
    
    # Return singleton client instance
    return chromadb.PersistentClient(path=settings.VECTOR_DB_PATH, settings=client_settings)

async def get_embedding_model():
    """Get available embedding model with fallback options"""
    # Try Azure OpenAI embeddings
    if settings.AZURE_OPENAI_API_KEY and settings.AZURE_OPENAI_EMBEDDING_MODEL:
        try:
            embedding_model = AzureOpenAIEmbeddings(
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION,
                azure_deployment=settings.AZURE_OPENAI_EMBEDDING_MODEL,
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
            )
            
            test_embedding = embedding_model.embed_query("test")
            if test_embedding and len(test_embedding) > 0:
                return embedding_model
        except Exception:
            pass  # Fall through to next option
    
    # Try instructor model
    try:
        embedding_model = HuggingFaceInstructEmbeddings(
            model_name="hkunlp/instructor-base", 
            model_kwargs={"device": "cpu"}
        )
        
        test_embedding = embedding_model.embed_query("test")
        if test_embedding and len(test_embedding) > 0:
            return embedding_model
    except Exception:
        pass  # Fall through to next option
    
    # Try simpler model as last resort
    try:
        embedding_model = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"}
        )
        
        test_embedding = embedding_model.embed_query("test")
        if test_embedding and len(test_embedding) > 0:
            return embedding_model
    except Exception as e:
        raise ValueError(f"All embedding models failed: {str(e)}")
    
    raise ValueError("No working embedding model found") 

async def get_llm_model(model_name: Optional[str] = None):
    """Get LLM model based on configuration"""
    try:
        model = model_name or settings.DEFAULT_LLM_MODEL
        
        if model.startswith("azure-gpt"):
            return AzureChatOpenAI(
                api_key=settings.AZURE_OPENAI_API_KEY,
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                azure_deployment=settings.AZURE_OPENAI_MODEL,
                model_name=model,
                temperature=0.2,
                openai_api_version=settings.AZURE_OPENAI_API_VERSION
            )
        elif model.startswith("gpt"):
            return ChatOpenAI(
                api_key=settings.OPENAI_API_KEY,
                model_name=model,
                temperature=0.2
            )
        elif model.startswith("claude"):
            return ChatAnthropic(
                api_key=settings.ANTHROPIC_API_KEY,
                model_name=model,
                temperature=0.2
            )
        else:
            # Default to Azure GPT model
            return AzureChatOpenAI(
                api_key=settings.AZURE_OPENAI_API_KEY,
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                azure_deployment=settings.AZURE_OPENAI_MODEL, 
                temperature=0.2,
                openai_api_version=settings.AZURE_OPENAI_API_VERSION
            )
    except Exception as e:
        print(f"Error initializing LLM: {str(e)}")
        raise ValueError(f"Failed to initialize LLM: {str(e)}")
    
async def reset_chroma_db() -> Dict[str, Any]:
    """Reset the ChromaDB directory to fix corrupted databases"""
    import os
    import shutil
    import time
    
    result = {
        "status": "unknown",
        "message": "",
        "backup_path": ""
    }
    
    try:
        # Create a timestamped backup dir
        timestamp = int(time.time())
        backup_dir = f"{settings.VECTOR_DB_PATH}_backup_{timestamp}"
        original_dir = settings.VECTOR_DB_PATH
        
        # Check if original directory exists
        if os.path.exists(original_dir):
            # Move the existing directory to backup
            print(f"Moving {original_dir} to {backup_dir}")
            shutil.move(original_dir, backup_dir)
            result["backup_path"] = backup_dir
            
            # Create a new empty directory
            os.makedirs(original_dir, exist_ok=True)
            
            result["status"] = "success"
            result["message"] = f"Successfully reset ChromaDB. Original data backed up to {backup_dir}"
        else:
            # Just create the directory if it doesn't exist
            os.makedirs(original_dir, exist_ok=True)
            result["status"] = "success"
            result["message"] = "ChromaDB directory created (it did not exist before)"
    except Exception as e:
        result["status"] = "error"
        result["message"] = f"Failed to reset ChromaDB: {str(e)}"
    
    return result


async def test_connections() -> Dict[str, Any]:
    """Test all service connections and return diagnostic information"""
    results = {
        "mongodb": {"status": "unknown", "message": ""},
        "azure_openai": {"status": "unknown", "message": ""},
        "chroma_db": {"status": "unknown", "message": ""},
        "environment_variables": {
            "AZURE_OPENAI_API_KEY": bool(settings.AZURE_OPENAI_API_KEY),
            "AZURE_OPENAI_ENDPOINT": bool(settings.AZURE_OPENAI_ENDPOINT),
            "AZURE_OPENAI_API_VERSION": bool(settings.AZURE_OPENAI_API_VERSION),
            "AZURE_OPENAI_EMBEDDING_MODEL": bool(settings.AZURE_OPENAI_EMBEDDING_MODEL),
            "VECTOR_DB_PATH": settings.VECTOR_DB_PATH
        }
    }
    
    # Test MongoDB connection
    try:
        # Use synchronous methods instead of awaiting
        mongodb.client.admin.command("ping")
        doc_count = mongodb.documents_collection.count_documents({})
        results["mongodb"] = {
            "status": "connected",
            "message": f"Successfully connected. Document count: {doc_count}"
        }
    except Exception as e:
        results["mongodb"] = {
            "status": "error",
            "message": f"Connection failed: {str(e)}"
        }
    
    # Test Azure OpenAI connection
    try:
        embedding_model = await get_embedding_model()
        test_embedding = embedding_model.embed_query("test connection")
        results["azure_openai"] = {
            "status": "connected",
            "message": f"Successfully connected. Embedding dimensions: {len(test_embedding)}"
        }
    except Exception as e:
        results["azure_openai"] = {
            "status": "error",
            "message": f"Connection failed: {str(e)}"
        }
    
    # Test ChromaDB connection
    try:
        import chromadb
        import os
        import traceback
        
        # Ensure directory exists
        os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)
        
        # Try to connect with more debug information
        print(f"Connecting to ChromaDB at path: {settings.VECTOR_DB_PATH}")
        try:
            chroma_client = chromadb.PersistentClient(path=settings.VECTOR_DB_PATH)
            print("ChromaDB client created successfully")
            
            # Test getting collection list
            collections = chroma_client.list_collections()
            # In ChromaDB v0.6.0+, list_collections() returns collection names directly
            collection_names = collections
            
            results["chroma_db"] = {
                "status": "connected",
                "message": f"Successfully connected. Available collections: {len(collection_names)}",
                "collections": collection_names
            }
        except Exception as inner_err:
            print(f"ChromaDB detailed error: {str(inner_err)}")
            print(f"Traceback: {traceback.format_exc()}")
            
            # Try alternative approach - create a temporary collection
            try:
                print("Trying alternative approach with temporary collection")
                # Try a new client with explicit settings
                persist_directory = os.path.abspath(settings.VECTOR_DB_PATH)
                chroma_client = chromadb.PersistentClient(path=persist_directory)
                
                # Create a test collection
                test_collection = chroma_client.create_collection(name="test_connection")
                
                # Add a test item
                test_collection.add(
                    documents=["This is a test document"],
                    metadatas=[{"source": "test"}],
                    ids=["test1"]
                )
                
                # Delete the test collection
                chroma_client.delete_collection("test_connection")
                
                results["chroma_db"] = {
                    "status": "connected",
                    "message": "Connected via alternative method. Test collection created and deleted successfully."
                }
            except Exception as alt_err:
                print(f"Alternative ChromaDB approach failed: {str(alt_err)}")
                raise
                
    except Exception as e:
        results["chroma_db"] = {
            "status": "error",
            "message": f"Connection failed: {str(e)}",
            "details": traceback.format_exc()
        }
    
    return results

async def reset_mongo_db() -> Dict[str, Any]:
    """Reset the MongoDB database by dropping and recreating collections"""
    result = {
        "status": "unknown",
        "message": "",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        # Drop existing collections
        collections_to_drop = [
            mongodb.documents_collection,
            mongodb.queries_collection,
            mongodb.metrics_collection
        ]
        
        for collection in collections_to_drop:
            collection.drop()
        
        # Recreate collections with proper indexes
        # Documents collection
        mongodb.documents_collection.create_index("document_id", unique=True)
        mongodb.documents_collection.create_index("embedding_status")
        mongodb.documents_collection.create_index("upload_date")
        
        # Queries collection
        mongodb.queries_collection.create_index("query_id", unique=True)
        mongodb.queries_collection.create_index("timestamp")
        mongodb.queries_collection.create_index("status")

        # Metrics collection
        mongodb.metrics_collection.create_index("timestamp")
        mongodb.metrics_collection.create_index("metric_type")
        
        result["status"] = "success"
        result["message"] = "Successfully reset MongoDB database. All collections have been recreated with proper indexes."
        
    except Exception as e:
        result["status"] = "error"
        result["message"] = f"Failed to reset MongoDB database: {str(e)}"
    
    return result