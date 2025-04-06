import os
import json
import pytest
import tempfile
from datetime import datetime
from typing import Dict, List
from fastapi.testclient import TestClient

from app.main import app
from app.services import document_service, query_service, metrics_service
from app.models.document import DocumentResponse
from app.models.query import QueryRequest, QueryResponse
from app.tests.conftest import TEST_DOCUMENT_ID, TEST_QUERY_ID, TEST_PDF_CONTENT

# Create a test client
client = TestClient(app)

# Test fixtures
@pytest.fixture
def test_document():
    # Create a test document record
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
    # Create a test query record
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

# Health check endpoint test
def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

# Document Routes Tests
class TestDocumentRoutes:
    
    def test_upload_document(self, client, mock_document_service, mock_db):
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
            tmp.write(TEST_PDF_CONTENT)
            tmp.flush()
            tmp.seek(0)
            
            # Test file upload
            with open(tmp.name, "rb") as f:
                file_content = f.read()
                response = client.post(
                    "/api/documents/upload",
                    files={"file": ("test_doc.pdf", file_content, "application/pdf")}
                )
            
            assert response.status_code == 200
            assert response.json()["document_id"] == TEST_DOCUMENT_ID
            assert response.json()["file_name"] == "test_doc.pdf"
    
    def test_get_documents(self, client, monkeypatch, test_document, mock_db):
        async def mock_get_all_documents(*args, **kwargs):
            return {
                "documents": [test_document],
                "total": 1
            }
            
        monkeypatch.setattr(document_service, "get_all_documents", mock_get_all_documents)
        
        response = client.get("/api/documents")
        assert response.status_code == 200
        assert response.json()["total"] == 1
        assert len(response.json()["documents"]) == 1
        assert response.json()["documents"][0]["document_id"] == TEST_DOCUMENT_ID
    
    def test_get_document(self, client, monkeypatch, test_document, mock_db):
        async def mock_get_document(doc_id):
            if doc_id == TEST_DOCUMENT_ID:
                return test_document
            return None
            
        monkeypatch.setattr(document_service, "get_document", mock_get_document)
        
        # Test valid document ID
        response = client.get(f"/api/documents/{TEST_DOCUMENT_ID}")
        assert response.status_code == 200
        assert response.json()["document_id"] == TEST_DOCUMENT_ID
        
        # Test non-existent document ID
        response = client.get("/api/documents/nonexistent-id")
        assert response.status_code == 404
    
    def test_delete_document(self, client, monkeypatch, mock_db):
        async def mock_delete_document(doc_id):
            return doc_id == TEST_DOCUMENT_ID
            
        monkeypatch.setattr(document_service, "delete_document", mock_delete_document)
        
        # Test valid document ID
        response = client.delete(f"/api/documents/{TEST_DOCUMENT_ID}")
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        
        # Test non-existent document ID
        response = client.delete("/api/documents/nonexistent-id")
        assert response.status_code == 404

# Query Routes Tests
class TestQueryRoutes:
    
    def test_query_documents(self, monkeypatch, test_query):
        async def mock_perform_query(query_req):
            return QueryResponse(
                query_id=TEST_QUERY_ID,
                query_text=query_req.query_text,
                answer=test_query["answer"],
                sources=test_query["sources"],
                latency=test_query["latency"],
                timestamp=test_query["timestamp"]
            )
            
        monkeypatch.setattr(query_service, "perform_query", mock_perform_query)
        
        query_data = {
            "query_text": "How do I reset a user's password?",
            "top_k": 3,
            "similarity_threshold": 0.7
        }
        
        response = client.post(
            "/api/query",
            json=query_data
        )
        
        assert response.status_code == 200
        assert response.json()["query_id"] == TEST_QUERY_ID
        assert response.json()["query_text"] == query_data["query_text"]
        assert response.json()["answer"] == test_query["answer"]
        assert len(response.json()["sources"]) == 1
    
    def test_get_query_history(self, monkeypatch, test_query):
        async def mock_get_query_history(*args, **kwargs):
            return {
                "queries": [test_query],
                "total": 1
            }
            
        monkeypatch.setattr(query_service, "get_query_history", mock_get_query_history)
        
        response = client.get("/api/queries")
        assert response.status_code == 200
        assert response.json()["total"] == 1
        assert len(response.json()["queries"]) == 1
        assert response.json()["queries"][0]["query_id"] == TEST_QUERY_ID
    
    def test_get_query(self, monkeypatch, test_query):
        async def mock_get_query(query_id):
            if query_id == TEST_QUERY_ID:
                return test_query
            return None
            
        monkeypatch.setattr(query_service, "get_query", mock_get_query)
        
        # Test valid query ID
        response = client.get(f"/api/queries/{TEST_QUERY_ID}")
        assert response.status_code == 200
        assert response.json()["query_id"] == TEST_QUERY_ID
        
        # Test non-existent query ID
        response = client.get("/api/queries/nonexistent-id")
        assert response.status_code == 404
    
    def test_get_demo_questions(self):
        response = client.get("/api/demo-questions")
        assert response.status_code == 200
        assert "demo_questions" in response.json()
        assert len(response.json()["demo_questions"]) > 0
        assert "question" in response.json()["demo_questions"][0]

# Metrics Routes Tests
class TestMetricsRoutes:
    
    def test_get_metrics_summary(self, monkeypatch):
        async def mock_get_metrics_summary(*args, **kwargs):
            return {
                "query_volume": [{"date": "2023-04-01", "count": 120}],
                "latency": [{"date": "2023-04-01", "avg_latency": 0.45}],
                "success_rate": [{"date": "2023-04-01", "success_rate": 0.98}],
                "top_queries": [{"query_text": "How to reset password", "count": 25}],
                "top_documents": [{"document_id": TEST_DOCUMENT_ID, "file_name": "user_guide.pdf", "count": 45}]
            }
            
        monkeypatch.setattr(metrics_service, "get_metrics_summary", mock_get_metrics_summary)
        
        response = client.get("/api/metrics/summary")
        assert response.status_code == 200
        assert "query_volume" in response.json()
        assert "latency" in response.json()
        assert "success_rate" in response.json()
        assert "top_queries" in response.json()
        assert "top_documents" in response.json()
    
    def test_get_query_volume(self, monkeypatch):
        async def mock_get_daily_query_volume(*args, **kwargs):
            return [
                {"date": "2023-04-01", "count": 120},
                {"date": "2023-04-02", "count": 135}
            ]
            
        monkeypatch.setattr(metrics_service, "get_daily_query_volume", mock_get_daily_query_volume)
        
        response = client.get("/api/metrics/query-volume")
        assert response.status_code == 200
        assert len(response.json()) == 2
        assert response.json()[0]["date"] == "2023-04-01"
        assert response.json()[0]["count"] == 120
    
    def test_get_latency(self, monkeypatch):
        async def mock_get_average_latency(*args, **kwargs):
            return [
                {"date": "2023-04-01", "avg_latency": 0.45},
                {"date": "2023-04-02", "avg_latency": 0.42}
            ]
            
        monkeypatch.setattr(metrics_service, "get_average_latency", mock_get_average_latency)
        
        response = client.get("/api/metrics/latency")
        assert response.status_code == 200
        assert len(response.json()) == 2
        assert response.json()[0]["date"] == "2023-04-01"
        assert response.json()[0]["avg_latency"] == 0.45
    
    def test_get_success_rate(self, monkeypatch):
        async def mock_get_success_rate(*args, **kwargs):
            return [
                {"date": "2023-04-01", "success_rate": 0.98},
                {"date": "2023-04-02", "success_rate": 0.97}
            ]
            
        monkeypatch.setattr(metrics_service, "get_success_rate", mock_get_success_rate)
        
        response = client.get("/api/metrics/success-rate")
        assert response.status_code == 200
        assert len(response.json()) == 2
        assert response.json()[0]["date"] == "2023-04-01"
        assert response.json()[0]["success_rate"] == 0.98
    
    def test_get_top_queries(self, monkeypatch):
        async def mock_get_top_queries(*args, **kwargs):
            return [
                {"query_text": "How to reset password", "count": 25},
                {"query_text": "What is the refund policy", "count": 18}
            ]
            
        monkeypatch.setattr(metrics_service, "get_top_queries", mock_get_top_queries)
        
        response = client.get("/api/metrics/top-queries")
        assert response.status_code == 200
        assert len(response.json()) == 2
        assert response.json()[0]["query_text"] == "How to reset password"
        assert response.json()[0]["count"] == 25
    
    def test_get_top_documents(self, monkeypatch):
        async def mock_get_top_documents(*args, **kwargs):
            return [
                {"document_id": TEST_DOCUMENT_ID, "file_name": "user_guide.pdf", "count": 45},
                {"document_id": "doc-789", "file_name": "faq.pdf", "count": 32}
            ]
            
        monkeypatch.setattr(metrics_service, "get_top_documents", mock_get_top_documents)
        
        response = client.get("/api/metrics/top-documents")
        assert response.status_code == 200
        assert len(response.json()) == 2
        assert response.json()[0]["document_id"] == TEST_DOCUMENT_ID
        assert response.json()[0]["file_name"] == "user_guide.pdf"
        assert response.json()[0]["count"] == 45

# End-to-end tests that test multiple components together
class TestEndToEnd:
    
    def test_document_upload_and_query(self, monkeypatch, test_document, test_query):
        # Mock document upload
        async def mock_save_uploaded_file(*args, **kwargs):
            return os.path.join(tempfile.gettempdir(), "test_doc.pdf")
            
        async def mock_create_document_record(*args, **kwargs):
            class MockDoc:
                document_id = TEST_DOCUMENT_ID
                file_name = "test_doc.pdf"
                file_type = "pdf"
                file_size = 1024
                upload_date = datetime.utcnow()
                embedding_status = "pending"
            return MockDoc()
        
        async def mock_process_document(*args, **kwargs):
            pass
        
        # Mock document retrieval
        async def mock_get_document(doc_id):
            if doc_id == TEST_DOCUMENT_ID:
                return test_document
            return None
        
        # Mock query execution
        async def mock_perform_query(query_req):
            return QueryResponse(
                query_id=TEST_QUERY_ID,
                query_text=query_req.query_text,
                answer=test_query["answer"],
                sources=test_query["sources"],
                latency=test_query["latency"],
                timestamp=test_query["timestamp"]
            )
        
        monkeypatch.setattr(document_service, "save_uploaded_file", mock_save_uploaded_file)
        monkeypatch.setattr(document_service, "create_document_record", mock_create_document_record)
        monkeypatch.setattr(document_service, "process_document", mock_process_document)
        monkeypatch.setattr(document_service, "get_document", mock_get_document)
        monkeypatch.setattr(query_service, "perform_query", mock_perform_query)
        
        # 1. Upload a document
        with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
            tmp.write(TEST_PDF_CONTENT)
            tmp.flush()
            tmp.seek(0)
            
            with open(tmp.name, "rb") as f:
                file_content = f.read()
                upload_response = client.post(
                    "/api/documents/upload",
                    files={"file": ("test_doc.pdf", file_content, "application/pdf")}
                )
            
            assert upload_response.status_code == 200
            doc_id = upload_response.json()["document_id"]
        
        # 2. Verify the document exists
        get_doc_response = client.get(f"/api/documents/{doc_id}")
        assert get_doc_response.status_code == 200
        
        # 3. Query against the document
        query_data = {
            "query_text": "How do I reset a user's password?",
            "top_k": 3,
            "similarity_threshold": 0.7,
            "document_ids": [doc_id]
        }
        
        query_response = client.post(
            "/api/query",
            json=query_data
        )
        
        assert query_response.status_code == 200
        assert query_response.json()["answer"] == test_query["answer"]
        assert len(query_response.json()["sources"]) == 1
        assert query_response.json()["sources"][0]["document_id"] == doc_id

# Error handling tests
class TestErrorHandling:
    
    def test_document_upload_invalid_type(self):
        with tempfile.NamedTemporaryFile(suffix=".xyz") as tmp:
            tmp.write(b"test content")
            tmp.flush()
            tmp.seek(0)
            
            with open(tmp.name, "rb") as f:
                file_content = f.read()
                response = client.post(
                    "/api/documents/upload",
                    files={"file": ("test_doc.xyz", file_content, "application/octet-stream")}
                )
            
            assert response.status_code == 415  # Unsupported media type
    
    def test_query_validation(self):
        # Missing required field
        response = client.post(
            "/api/query",
            json={"top_k": 3}
        )
        assert response.status_code == 422  # Validation error
        
        # Invalid values
        response = client.post(
            "/api/query",
            json={
                "query_text": "Test query",
                "top_k": -1,  # Invalid negative value
                "similarity_threshold": 2.0  # Invalid threshold > 1.0
            }
        )
        assert response.status_code == 422  # Validation error
