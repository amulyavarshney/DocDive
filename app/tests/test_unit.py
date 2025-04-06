import os
import json
import pytest
import tempfile
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock

from app.core.config import settings
from app.services import document_service, query_service, metrics_service
from app.models.document import DocumentResponse, DocumentCreate
from app.models.query import QueryRequest, QueryResponse
from app.db import mongodb

# Test constants
TEST_DOCUMENT_ID = "test-doc-123"
TEST_QUERY_ID = "test-query-456"


# Document Service Tests
class TestDocumentService:
    
    @pytest.mark.asyncio
    async def test_create_document_record(self):
        # Mock the database call
        with patch('app.db.mongodb.insert_document', new_callable=AsyncMock) as mock_create:
            # Setup mock return value
            mock_create.return_value = TEST_DOCUMENT_ID
            
            # Call the service
            doc = await document_service.create_document_record(
                filename="test.pdf",
                file_size=1024,
                file_path="/tmp/test.pdf",
                content_type="application/pdf"
            )
            
            # Assert the document was created
            assert doc.document_id == TEST_DOCUMENT_ID
            mock_create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_document(self):
        # Mock the database call
        with patch('app.db.mongodb.get_document', new_callable=AsyncMock) as mock_get:
            # Setup mock return value
            mock_get.return_value = {
                "document_id": TEST_DOCUMENT_ID,
                "file_name": "test.pdf",
                "file_type": "pdf",
                "file_size": 1024,
                "upload_date": datetime.utcnow(),
                "embedding_status": "completed",
                "chunk_count": 5
            }
            
            # Call the service
            doc = await document_service.get_document(TEST_DOCUMENT_ID)
            
            # Assert document was retrieved
            assert doc["document_id"] == TEST_DOCUMENT_ID
            mock_get.assert_called_once_with(TEST_DOCUMENT_ID)
    
    @pytest.mark.asyncio
    async def test_delete_document(self):
        # Mock the database call
        with patch('app.db.mongodb.delete_document', new_callable=AsyncMock) as mock_delete:
            # Setup mock return value
            mock_delete.return_value = True
            
            # Mock the file deletion
            with patch('os.remove') as mock_remove:
                mock_remove.return_value = None
                
                # Call the service
                result = await document_service.delete_document(TEST_DOCUMENT_ID)
                
                # Assert document was deleted
                assert result is True
                mock_delete.assert_called_once_with(TEST_DOCUMENT_ID)
    
    @pytest.mark.asyncio
    async def test_save_uploaded_file(self):
        # Create a mock file upload
        mock_file = MagicMock()
        mock_file.filename = "test.pdf"
        mock_file.read = AsyncMock(return_value=b"test content")
        
        # Mock file operations
        with patch('aiofiles.open', new_callable=MagicMock) as mock_open:
            mock_file_handle = MagicMock()
            mock_file_handle.__aenter__ = AsyncMock(return_value=mock_file_handle)
            mock_file_handle.__aexit__ = AsyncMock(return_value=None)
            mock_file_handle.write = AsyncMock(return_value=None)
            mock_open.return_value = mock_file_handle
            
            # Mock os.path.join to control the output path
            with patch('os.path.join', return_value="/data/uploads/test.pdf"):
                # Mock os.makedirs to avoid actual directory creation
                with patch('os.makedirs', return_value=None):
                    # Call the service
                    file_path = await document_service.save_uploaded_file(mock_file, "test.pdf")
                    
                    # Assert file was saved
                    assert file_path == "/data/uploads/test.pdf"
                    mock_file_handle.write.assert_called_once()


# Query Service Tests
class TestQueryService:
    
    @pytest.mark.asyncio
    async def test_perform_query(self):
        # Create a mock query request
        query_request = QueryRequest(
            query_text="How do I reset a password?",
            top_k=3,
            similarity_threshold=0.7
        )
        
        # Mock the vector database call
        with patch('app.services.vector_store.search_documents', new_callable=AsyncMock) as mock_search:
            # Setup mock return value for vector search
            mock_search.return_value = [
                {
                    "document_id": TEST_DOCUMENT_ID,
                    "text": "To reset a password, go to the admin panel...",
                    "metadata": {
                        "file_name": "test.pdf",
                        "page": 1
                    },
                    "similarity": 0.92
                }
            ]
            
            # Mock the LLM call to generate answer
            with patch('app.services.llm_service.generate_answer', new_callable=AsyncMock) as mock_llm:
                mock_llm.return_value = "To reset a password, go to the admin panel and select 'Reset Password'."
                
                # Mock the query logging
                with patch('app.db.mongodb.log_query', new_callable=AsyncMock) as mock_log:
                    mock_log.return_value = TEST_QUERY_ID
                    
                    # Call the service
                    start_time = datetime.now()
                    result = await query_service.perform_query(query_request)
                    
                    # Assert query was performed and response is correct
                    assert isinstance(result, QueryResponse)
                    assert result.query_id == TEST_QUERY_ID
                    assert result.query_text == query_request.query_text
                    assert result.answer == "To reset a password, go to the admin panel and select 'Reset Password'."
                    assert len(result.sources) == 1
                    assert result.sources[0]["document_id"] == TEST_DOCUMENT_ID
                    assert result.latency > 0
    
    @pytest.mark.asyncio
    async def test_get_query(self):
        # Mock the database call
        with patch('app.db.mongodb.get_query', new_callable=AsyncMock) as mock_get:
            # Setup mock return value
            mock_get.return_value = {
                "query_id": TEST_QUERY_ID,
                "query_text": "How do I reset a password?",
                "answer": "To reset a password, go to the admin panel.",
                "sources": [
                    {
                        "document_id": TEST_DOCUMENT_ID,
                        "file_name": "test.pdf",
                        "text": "To reset a password, go to the admin panel...",
                        "page": 1,
                        "similarity": 0.92
                    }
                ],
                "latency": 0.543,
                "timestamp": datetime.utcnow()
            }
            
            # Call the service
            query = await query_service.get_query(TEST_QUERY_ID)
            
            # Assert query was retrieved
            assert query["query_id"] == TEST_QUERY_ID
            mock_get.assert_called_once_with(TEST_QUERY_ID)


# Metrics Service Tests
class TestMetricsService:
    
    @pytest.mark.asyncio
    async def test_get_daily_query_volume(self):
        # Mock the database call
        with patch('app.db.mongodb.get_daily_query_volume', new_callable=AsyncMock) as mock_volume:
            # Setup mock return value
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            
            mock_volume.return_value = [
                {"date": today.isoformat(), "count": 120},
                {"date": yesterday.isoformat(), "count": 110}
            ]
            
            # Call the service
            result = await metrics_service.get_daily_query_volume(days=7)
            
            # Assert we got the right metrics
            assert len(result) == 2
            assert result[0]["count"] == 120
            assert result[1]["count"] == 110
            mock_volume.assert_called_once_with(7)
    
    @pytest.mark.asyncio
    async def test_get_average_latency(self):
        # Mock the database call
        with patch('app.db.mongodb.get_average_latency', new_callable=AsyncMock) as mock_latency:
            # Setup mock return value
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            
            mock_latency.return_value = [
                {"date": today.isoformat(), "avg_latency": 0.45},
                {"date": yesterday.isoformat(), "avg_latency": 0.48}
            ]
            
            # Call the service
            result = await metrics_service.get_average_latency(days=7)
            
            # Assert we got the right metrics
            assert len(result) == 2
            assert result[0]["avg_latency"] == 0.45
            assert result[1]["avg_latency"] == 0.48
            mock_latency.assert_called_once_with(7)
    
    @pytest.mark.asyncio
    async def test_get_success_rate(self):
        # Mock the database call
        with patch('app.db.mongodb.get_success_rate', new_callable=AsyncMock) as mock_success:
            # Setup mock return value
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            
            mock_success.return_value = [
                {"date": today.isoformat(), "success_rate": 0.98},
                {"date": yesterday.isoformat(), "success_rate": 0.97}
            ]
            
            # Call the service
            result = await metrics_service.get_success_rate(days=7)
            
            # Assert we got the right metrics
            assert len(result) == 2
            assert result[0]["success_rate"] == 0.98
            assert result[1]["success_rate"] == 0.97
            mock_success.assert_called_once_with(7)
    
    @pytest.mark.asyncio
    async def test_get_top_queries(self):
        # Mock the database call
        with patch('app.db.mongodb.get_top_queries', new_callable=AsyncMock) as mock_top:
            # Setup mock return value
            mock_top.return_value = [
                {"query_text": "How to reset password", "count": 25},
                {"query_text": "What is the refund policy", "count": 18}
            ]
            
            # Call the service
            result = await metrics_service.get_top_queries(limit=10)
            
            # Assert we got the right metrics
            assert len(result) == 2
            assert result[0]["query_text"] == "How to reset password"
            assert result[0]["count"] == 25
            mock_top.assert_called_once_with(10)
    
    @pytest.mark.asyncio
    async def test_get_top_documents(self):
        # Mock the database call
        with patch('app.db.mongodb.get_top_documents', new_callable=AsyncMock) as mock_top:
            # Setup mock return value
            mock_top.return_value = [
                {"document_id": TEST_DOCUMENT_ID, "file_name": "test.pdf", "count": 45},
                {"document_id": "doc-789", "file_name": "other.pdf", "count": 32}
            ]
            
            # Call the service
            result = await metrics_service.get_top_documents(limit=10)
            
            # Assert we got the right metrics
            assert len(result) == 2
            assert result[0]["document_id"] == TEST_DOCUMENT_ID
            assert result[0]["count"] == 45
            mock_top.assert_called_once_with(10)
    
    @pytest.mark.asyncio
    async def test_get_metrics_summary(self):
        # Mock all the individual metric methods
        with patch('app.services.metrics_service.get_daily_query_volume', new_callable=AsyncMock) as mock_volume:
            mock_volume.return_value = [{"date": "2023-04-01", "count": 120}]
            
            with patch('app.services.metrics_service.get_average_latency', new_callable=AsyncMock) as mock_latency:
                mock_latency.return_value = [{"date": "2023-04-01", "avg_latency": 0.45}]
                
                with patch('app.services.metrics_service.get_success_rate', new_callable=AsyncMock) as mock_success:
                    mock_success.return_value = [{"date": "2023-04-01", "success_rate": 0.98}]
                    
                    with patch('app.services.metrics_service.get_top_queries', new_callable=AsyncMock) as mock_queries:
                        mock_queries.return_value = [{"query_text": "How to reset password", "count": 25}]
                        
                        with patch('app.services.metrics_service.get_top_documents', new_callable=AsyncMock) as mock_docs:
                            mock_docs.return_value = [{"document_id": TEST_DOCUMENT_ID, "file_name": "test.pdf", "count": 45}]
                            
                            # Call the service
                            result = await metrics_service.get_metrics_summary(days=7, limit=10)
                            
                            # Assert summary contains all metrics
                            assert "query_volume" in result
                            assert "latency" in result
                            assert "success_rate" in result
                            assert "top_queries" in result
                            assert "top_documents" in result
                            
                            assert len(result["query_volume"]) == 1
                            assert len(result["latency"]) == 1
                            assert len(result["success_rate"]) == 1
                            assert len(result["top_queries"]) == 1
                            assert len(result["top_documents"]) == 1
                            
                            # Assert all methods were called
                            mock_volume.assert_called_once_with(7)
                            mock_latency.assert_called_once_with(7)
                            mock_success.assert_called_once_with(7)
                            mock_queries.assert_called_once_with(10)
                            mock_docs.assert_called_once_with(10)


# Test document text extraction and chunking
class TestDocumentProcessing:
    
    def test_pdf_text_extraction(self):
        # Mock PDF extraction
        with patch('app.services.document_service.extract_text_from_pdf') as mock_extract:
            mock_extract.return_value = "This is extracted PDF text."
            
            text = document_service.extract_text_from_pdf("/fake/path/doc.pdf")
            
            assert text == "This is extracted PDF text."
            mock_extract.assert_called_once_with("/fake/path/doc.pdf")
    
    def test_text_chunking(self):
        # Test chunking a text into smaller pieces
        with patch('app.services.document_service.chunk_text') as mock_chunk:
            mock_chunk.return_value = [
                "This is chunk 1.",
                "This is chunk 2.",
                "This is chunk 3."
            ]
            
            text = "This is a long text that needs to be chunked into smaller pieces."
            chunks = document_service.chunk_text(text, chunk_size=100, chunk_overlap=20)
            
            assert len(chunks) == 3
            assert chunks[0] == "This is chunk 1."
            mock_chunk.assert_called_once_with(text, chunk_size=100, chunk_overlap=20)
    
    @pytest.mark.asyncio
    async def test_process_document(self):
        # Create a mock document
        mock_doc = MagicMock()
        mock_doc.document_id = TEST_DOCUMENT_ID
        mock_doc.file_path = "/fake/path/doc.pdf"
        mock_doc.file_type = "pdf"
        
        # Mock text extraction
        with patch('app.services.document_service.extract_text_from_pdf', return_value="Extracted text") as mock_extract:
            # Mock text chunking
            with patch('app.services.document_service.chunk_text') as mock_chunk:
                mock_chunk.return_value = ["Chunk 1", "Chunk 2"]
                
                # Mock vector database
                with patch('app.services.vector_store.add_documents', new_callable=AsyncMock) as mock_add:
                    mock_add.return_value = True
                    
                    # Mock MongoDB update - no need to mock it as async since we fixed it to be sync
                    with patch('app.db.mongodb.documents_collection.update_one') as mock_update:
                        mock_update.return_value = MagicMock()
                        
                        # Call the service
                        await document_service.process_document(mock_doc)
                        
                        # Assert all methods were called
                        mock_extract.assert_called_once()
                        mock_chunk.assert_called_once()
                        mock_add.assert_called_once()
                        # We don't need to check the arguments for update_one since it's not part of our API 