"""
Pytest configuration for Document Search & Q&A Platform tests.
"""

import os
import pytest
import tempfile
from datetime import datetime
from unittest.mock import patch, AsyncMock

from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

# Constants for tests
TEST_DOCUMENT_ID = "test-doc-123"
TEST_QUERY_ID = "test-query-456"
TEST_PDF_CONTENT = b"%PDF-1.7\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length"


@pytest.fixture
def mock_db():
    """Mock MongoDB connection for tests."""
    if os.environ.get("USE_MOCK_DB", "false").lower() == "true":
        with patch("app.db.mongodb.documents_collection"):
            with patch("app.db.mongodb.queries_collection"):
                with patch("app.db.mongodb.metrics_collection"):
                    yield
    else:
        yield


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_document():
    """Create a test document record."""
    return {
        "document_id": TEST_DOCUMENT_ID,
        "file_name": "test_document.pdf",
        "file_type": "pdf",
        "file_size": 1024,
        "upload_date": datetime.utcnow(),
        "embedding_status": "completed",
        "chunk_count": 5
    }


@pytest.fixture
def test_query():
    """Create a test query record."""
    return {
        "query_id": TEST_QUERY_ID,
        "query_text": "How do I reset a user's password?",
        "answer": "To reset a user's password, go to the admin panel and select 'Reset Password'.",
        "sources": [
            {
                "document_id": TEST_DOCUMENT_ID,
                "file_name": "test_document.pdf", 
                "text": "To reset a user's password, go to the admin panel...",
                "page": 1,
                "similarity": 0.92
            }
        ],
        "latency": 0.543,
        "timestamp": datetime.utcnow()
    }


@pytest.fixture
def mock_document_service():
    """Mock document service functions."""
    with patch("app.services.document_service.save_uploaded_file", new_callable=AsyncMock) as mock_save:
        with patch("app.services.document_service.create_document_record", new_callable=AsyncMock) as mock_create:
            with patch("app.services.document_service.process_document", new_callable=AsyncMock) as mock_process:
                with patch("app.services.document_service.get_document", new_callable=AsyncMock) as mock_get:
                    with patch("app.services.document_service.get_all_documents", new_callable=AsyncMock) as mock_get_all:
                        with patch("app.services.document_service.delete_document", new_callable=AsyncMock) as mock_delete:
                        
                            # Set up default return values
                            mock_save.return_value = os.path.join(tempfile.gettempdir(), "test_doc.pdf")
                            
                            class MockDoc:
                                document_id = TEST_DOCUMENT_ID
                                file_name = "test_doc.pdf"
                                file_type = "pdf"
                                file_size = 1024
                                upload_date = datetime.utcnow()
                                embedding_status = "pending"
                                
                            mock_create.return_value = MockDoc()
                            mock_process.return_value = None
                            
                            yield {
                                "save_uploaded_file": mock_save,
                                "create_document_record": mock_create,
                                "process_document": mock_process,
                                "get_document": mock_get,
                                "get_all_documents": mock_get_all,
                                "delete_document": mock_delete
                            } 