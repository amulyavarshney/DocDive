import os
import time
import random
import json
import string
import logging
import warnings
from typing import Dict, List, Optional, Union
from locust import HttpUser, task, between, events, constant_pacing, TaskSet
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("locust")

# Suppress SSL warnings when verification is disabled
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# TEST CONFIGURATION
# These settings control the test behavior
TEST_DURATION_SECONDS = 60  # 1 minute test
TARGET_RPS_MIN = 10
TARGET_RPS_MAX = 50
MAX_USERS = 20  # Maximum number of simulated users
VERIFY_SSL = False  # Set to False to disable SSL certificate verification for deployed endpoints

# Sample data for generating test content
QUERY_TEMPLATES = [
    "Explain {topic} in simple terms",
    "What is {topic}?",
    "How does {topic} work?",
    "What are the advantages of {topic}?",
    "Compare {topic} with alternatives",
]

TOPICS = [
    "machine learning",
    "artificial intelligence",
    "natural language processing",
    "deep learning",
    "transformers",
    "neural networks",
    "computer vision",
    "large language models",
    "document retrieval",
    "vector databases",
]

# Global tracking of created resources for cleanup
created_document_ids = []
created_query_ids = []

# Cleanup event handler - runs at test end
@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Clean up all test data after the load test is complete"""
    logger.info("🧹 Starting test data cleanup...")
    
    # Check if we have any documents to clean up
    if not created_document_ids:
        logger.info("No documents to clean up")
        return
        
    # Get a client for cleanup
    cleanup_client = None
    try:
        if environment.runner and hasattr(environment.runner, "user_classes") and environment.runner.user_classes:
            # Create a new client for cleanup
            user_class = environment.runner.user_classes[0]
            cleanup_client = user_class(environment)
            cleanup_client.client.timeout = 30.0
            cleanup_client.client.verify = VERIFY_SSL  # Apply SSL verification setting
        else:
            logger.warning("Could not create cleanup client - runner or user classes not available")
            return
    except Exception as e:
        logger.error(f"Failed to create cleanup client: {str(e)}")
        return
    
    # Delete created documents
    cleanup_successful = True
    for doc_id in created_document_ids[:]:
        try:
            response = cleanup_client.client.delete(
                f"/api/documents/{doc_id}", 
                name="/api/documents/{id} [cleanup]",
                timeout=10.0,
                verify=VERIFY_SSL
            )
            if response.status_code in [200, 204, 404]:
                created_document_ids.remove(doc_id)
                logger.info(f"✅ Deleted document: {doc_id}")
            else:
                logger.warning(f"❌ Failed to delete document {doc_id}: HTTP {response.status_code}")
                cleanup_successful = False
        except Exception as e:
            logger.error(f"❌ Error deleting document {doc_id}: {str(e)}")
            cleanup_successful = False
    
    # Reset system data if necessary
    if not cleanup_successful or created_document_ids:
        try:
            logger.warning(f"⚠️ {len(created_document_ids)} documents could not be deleted, resetting databases...")
            
            try:
                cleanup_client.client.delete(
                    "/api/reset-mongodb", 
                    name="/api/reset-mongodb [cleanup]",
                    timeout=10.0,
                    verify=VERIFY_SSL
                )
                logger.info("✅ MongoDB reset")
            except Exception as mongo_err:
                logger.error(f"❌ Error resetting MongoDB: {str(mongo_err)}")
                
            try:
                cleanup_client.client.delete(
                    "/api/reset-chromadb", 
                    name="/api/reset-chromadb [cleanup]",
                    timeout=10.0,
                    verify=VERIFY_SSL
                )
                logger.info("✅ ChromaDB reset")
            except Exception as chroma_err:
                logger.error(f"❌ Error resetting ChromaDB: {str(chroma_err)}")
                
        except Exception as e:
            logger.error(f"❌ Error during database reset: {str(e)}")
    
    # Clean up the temporary client
    try:
        if cleanup_client and hasattr(cleanup_client, "on_stop"):
            cleanup_client.on_stop()
    except Exception as e:
        logger.error(f"Error during cleanup client shutdown: {str(e)}")
    
    logger.info("🏁 Cleanup complete")

class DocumentOperations(TaskSet):
    """Document-related API operations"""
    
    def make_request(self, method, url, **kwargs):
        """Helper method to ensure consistent request settings"""
        if 'verify' not in kwargs:
            kwargs['verify'] = VERIFY_SSL
        if 'timeout' not in kwargs:
            kwargs['timeout'] = 30.0
            
        return getattr(self.client, method)(url, **kwargs)
    
    @task(3)
    def upload_document(self):
        """Upload a test document"""
        # Create a unique test document
        timestamp = int(time.time())
        random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        filename = f"test_doc_{timestamp}_{random_id}.txt"
        
        # Generate document content
        content = self._generate_document_content()
        
        # Create file in memory
        try:
            # Upload the document
            response = self.make_request(
                'post',
                "/api/documents/upload",
                files={"file": (filename, content, "text/plain")},
                name="/api/documents/upload"
            )
            
            # Track the document for cleanup
            if response.status_code == 201:
                doc_id = response.json().get("document_id")
                if doc_id:
                    created_document_ids.append(doc_id)
                    logger.info(f"📄 Created document: {doc_id}")
        except Exception as e:
            logger.error(f"❌ Upload error: {str(e)}")
    
    @task(5)
    def get_documents(self):
        """Get list of documents"""
        limit = random.randint(5, 20)
        skip = random.randint(0, 5)
        try:
            self.make_request(
                'get',
                f"/api/documents?limit={limit}&skip={skip}",
                name="/api/documents"
            )
        except Exception as e:
            logger.error(f"❌ Get documents error: {str(e)}")
    
    @task(2)
    def get_document_details(self):
        """Get details of a specific document"""
        # Use an existing document ID if available
        if not created_document_ids:
            return
            
        doc_id = random.choice(created_document_ids)
        try:
            self.make_request(
                'get',
                f"/api/documents/{doc_id}",
                name="/api/documents/{id}"
            )
        except Exception as e:
            logger.error(f"❌ Get document details error: {str(e)}")
    
    @task(1)
    def get_document_stats(self):
        """Get document statistics"""
        try:
            self.make_request(
                'get',
                "/api/documents/stats", 
                name="/api/documents/stats"
            )
        except Exception as e:
            logger.error(f"❌ Get document stats error: {str(e)}")
    
    @task(1)
    def get_document_types(self):
        """Get document type distribution"""
        try:
            self.make_request(
                'get',
                "/api/documents/types", 
                name="/api/documents/types"
            )
        except Exception as e:
            logger.error(f"❌ Get document types error: {str(e)}")
    
    @task(1)
    def delete_document(self):
        """Delete a document"""
        # Skip if no documents available
        if not created_document_ids:
            return
            
        # Get a random document ID and remove it from our tracking list
        doc_id = random.choice(created_document_ids)
        try:
            response = self.make_request(
                'delete',
                f"/api/documents/{doc_id}",
                name="/api/documents/{id}"
            )
            
            # Remove from our tracking if successful
            if response.status_code == 200:
                created_document_ids.remove(doc_id)
                logger.info(f"🗑️ Deleted document: {doc_id}")
        except Exception as e:
            logger.error(f"❌ Delete document error: {str(e)}")
    
    def _generate_document_content(self) -> str:
        """Generate a random document with sections and content"""
        topic = random.choice(TOPICS)
        paragraphs = [
            f"# Test Document: {topic.title()}",
            f"This is a test document about {topic} for load testing purposes.",
            "## Introduction",
            f"{topic.title()} is a field that has seen significant advancement in recent years.",
            "## Key Concepts",
            f"Understanding {topic} requires familiarity with several core concepts:",
            "- Data processing",
            "- Algorithm design",
            "- Evaluation metrics",
            f"## Applications of {topic.title()}",
            f"{topic.title()} has many real-world applications including:",
            "1. Business automation",
            "2. Decision support systems",
            "3. Predictive analytics",
            "## Summary",
            f"This test document showcases content about {topic} for retrieval testing."
        ]
        return "\n\n".join(paragraphs)

class QueryOperations(TaskSet):
    """Query-related API operations"""
    
    def make_request(self, method, url, **kwargs):
        """Helper method to ensure consistent request settings"""
        if 'verify' not in kwargs:
            kwargs['verify'] = VERIFY_SSL
        if 'timeout' not in kwargs:
            kwargs['timeout'] = 30.0
            
        return getattr(self.client, method)(url, **kwargs)
    
    @task(10)
    def query_documents(self):
        """Query documents with generated questions"""
        if not created_document_ids:
            return
            
        # Generate a query
        query_text = self._generate_query()
        max_results = random.randint(1, 3)
        
        try:
            response = self.make_request(
                'post',
                "/api/query",
                json={"query_text": query_text, "max_results": max_results},
                name="/api/query"
            )
            
            # Track query ID
            if response.status_code == 200:
                query_id = response.json().get("query_id")
                if query_id:
                    created_query_ids.append(query_id)
        except Exception as e:
            logger.error(f"❌ Query error: {str(e)}")
    
    @task(3)
    def get_query_history(self):
        """Get query history"""
        limit = random.randint(5, 20)
        skip = random.randint(0, 5)
        sort = random.choice(["asc", "desc"])
        
        try:
            self.make_request(
                'get',
                f"/api/queries?limit={limit}&skip={skip}&sort={sort}",
                name="/api/queries"
            )
        except Exception as e:
            logger.error(f"❌ Query history error: {str(e)}")
    
    @task(2)
    def get_query_details(self):
        """Get specific query details"""
        if not created_query_ids:
            return
            
        query_id = random.choice(created_query_ids)
        try:
            self.make_request(
                'get',
                f"/api/queries/{query_id}",
                name="/api/queries/{id}"
            )
        except Exception as e:
            logger.error(f"❌ Query details error: {str(e)}")
    
    def _generate_query(self) -> str:
        """Generate a random query"""
        template = random.choice(QUERY_TEMPLATES)
        topic = random.choice(TOPICS)
        return template.format(topic=topic)

class MetricsOperations(TaskSet):
    """Metrics API operations"""
    
    def make_request(self, method, url, **kwargs):
        """Helper method to ensure consistent request settings"""
        if 'verify' not in kwargs:
            kwargs['verify'] = VERIFY_SSL
        if 'timeout' not in kwargs:
            kwargs['timeout'] = 30.0
            
        return getattr(self.client, method)(url, **kwargs)
    
    @task(1)
    def get_metrics_summary(self):
        """Get metrics summary"""
        days = random.randint(1, 7)
        limit = random.randint(5, 10)
        try:
            self.make_request(
                'get',
                f"/api/metrics/summary?days={days}&limit={limit}",
                name="/api/metrics/summary"
            )
        except Exception as e:
            logger.error(f"❌ Metrics summary error: {str(e)}")
    
    @task(1)
    def get_query_volume(self):
        """Get query volume metrics"""
        days = random.randint(1, 7)
        try:
            self.make_request(
                'get',
                f"/api/metrics/query-volume?days={days}",
                name="/api/metrics/query-volume"
            )
        except Exception as e:
            logger.error(f"❌ Query volume error: {str(e)}")
    
    @task(1)
    def get_latency_metrics(self):
        """Get latency metrics"""
        days = random.randint(1, 7)
        try:
            self.make_request(
                'get',
                f"/api/metrics/latency?days={days}",
                name="/api/metrics/latency"
            )
        except Exception as e:
            logger.error(f"❌ Latency metrics error: {str(e)}")
    
    @task(1)
    def get_success_rate(self):
        """Get success rate metrics"""
        days = random.randint(1, 7)
        try:
            self.make_request(
                'get',
                f"/api/metrics/success-rate?days={days}",
                name="/api/metrics/success-rate"
            )
        except Exception as e:
            logger.error(f"❌ Success rate error: {str(e)}")
    
    @task(1)
    def get_top_queries(self):
        """Get top queries metrics"""
        days = random.randint(1, 7)
        limit = random.randint(5, 10)
        try:
            self.make_request(
                'get',
                f"/api/metrics/top-queries?days={days}&limit={limit}",
                name="/api/metrics/top-queries"
            )
        except Exception as e:
            logger.error(f"❌ Top queries error: {str(e)}")
    
    @task(1)
    def get_top_documents(self):
        """Get top documents metrics"""
        days = random.randint(1, 7)
        limit = random.randint(5, 10)
        try:
            self.make_request(
                'get',
                f"/api/metrics/top-documents?days={days}&limit={limit}",
                name="/api/metrics/top-documents"
            )
        except Exception as e:
            logger.error(f"❌ Top documents error: {str(e)}")

class SystemOperations(TaskSet):
    """System API operations"""
    
    def make_request(self, method, url, **kwargs):
        """Helper method to ensure consistent request settings"""
        if 'verify' not in kwargs:
            kwargs['verify'] = VERIFY_SSL
        if 'timeout' not in kwargs:
            kwargs['timeout'] = 30.0
            
        return getattr(self.client, method)(url, **kwargs)
    
    @task(1)
    def get_diagnostics(self):
        """Get system diagnostics"""
        try:
            self.make_request(
                'get',
                "/api/diagnostics", 
                name="/api/diagnostics"
            )
        except Exception as e:
            logger.error(f"❌ Diagnostics error: {str(e)}")

class DocDiveUser(HttpUser):
    """
    Main user class that simulates realistic user behavior
    with all API endpoints
    """
    # Set pacing to control request rate to achieve 10-50 RPS
    # Starting with a conservative wait time, the runner will adjust based on metrics
    wait_time = constant_pacing(0.5)  # Start with 2 RPS per user
    
    # TaskSets with weights
    tasks = {
        DocumentOperations: 4,
        QueryOperations: 5, 
        MetricsOperations: 2,
        SystemOperations: 1
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client.timeout = 30.0  # Set a reasonable timeout
        self.client.verify = VERIFY_SSL  # Apply SSL verification setting
        self.start_time = None
    
    def on_start(self):
        """Initialize user session"""
        self.start_time = time.time()
        self.client.headers.update({
            "Accept": "application/json",
            "User-Agent": "DocDiveLoadTest/1.0",
            "Connection": "close"  # Prevent connection pooling issues
        })
        logger.info(f"👤 User started at {self.start_time} (SSL verification: {VERIFY_SSL})")
    
    def on_stop(self):
        """Clean up user session"""
        if self.start_time:
            duration = time.time() - self.start_time
            logger.info(f"👤 User stopped after {duration:.2f}s")

# If running locally for development
if __name__ == "__main__":
    print("DocDive Load Test")
    print("=================")
    print(f"Target: {TARGET_RPS_MIN}-{TARGET_RPS_MAX} RPS for {TEST_DURATION_SECONDS} seconds")
    print(f"SSL verification: {'Enabled' if VERIFY_SSL else 'Disabled'}")
    print("\nTo run the load test against a local endpoint:")
    print("locust -f locustfile.py --host=http://localhost:8000 --users 10 --spawn-rate 2 --run-time 1m --headless")
    print("\nTo run against a deployed HTTPS endpoint with SSL verification disabled:")
    print("locust -f locustfile.py --host=https://your-deployed-endpoint.com --users 10 --spawn-rate 2 --run-time 1m --headless")
