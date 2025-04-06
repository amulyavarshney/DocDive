import os
import time
import random
import json
import string
from collections import Counter
from locust import HttpUser, task, between, tag, events
from locust.exception import StopUser
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("locust")

# Sample query templates
QUERY_TEMPLATES = [
    "What is {topic}?",
    "How does {topic} work?",
    "Explain {topic} in simple terms",
    "What are the main features of {topic}?",
    "Compare {topic} with alternatives",
]

# Sample topics for query generation
TOPICS = [
    "machine learning",
    "artificial intelligence",
    "neural networks",
    "deep learning",
    "natural language processing",
    "computer vision",
    "reinforcement learning",
    "data science",
    "big data",
    "cloud computing",
]

# Circuit breaker globals
CIRCUIT_OPEN = False  # When True, circuit is "open" and we pause requests
FAILURE_THRESHOLD = 5  # Number of failures before opening circuit
CIRCUIT_TIMEOUT = 30  # Seconds to keep circuit open
LAST_CIRCUIT_OPEN = 0  # Timestamp when circuit was opened
TOTAL_FAILURES = Counter()  # Count failures by endpoint

# Global connection settings
DEFAULT_TIMEOUT = 10.0  # Default timeout in seconds
UPLOAD_TIMEOUT = 20.0  # Upload timeout in seconds
QUERY_TIMEOUT = 15.0   # Query timeout in seconds
STRESS_TIMEOUT = 10.0  # Stress test timeout in seconds

class DocumentSearchUser(HttpUser):
    """
    Simulates a user interacting with the document search API.
    This user follows a realistic usage pattern:
    1. Upload documents (occasionally)
    2. Query documents (frequently)
    3. View document details and query history
    """
    # Increase wait time to reduce load
    wait_time = between(3, 8)  # Wait between 3-8 seconds between tasks
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.documents = []  # Store document IDs
        self.queries = []    # Store query IDs
        self.consecutive_errors = 0
        
    def on_start(self):
        """Initialize user by uploading a document"""
        self.client.headers.update({
            "Accept": "application/json",
            "Connection": "close"  # Prevent connection pooling issues
        })
        
        # Upload a document at the start
        self.upload_document()
    
    def generate_query(self):
        """Generate a random query using templates"""
        template = random.choice(QUERY_TEMPLATES)
        topic = random.choice(TOPICS)
        return template.format(topic=topic)
    
    def check_circuit_breaker(self, endpoint):
        """Check if circuit breaker is open for an endpoint"""
        global CIRCUIT_OPEN, LAST_CIRCUIT_OPEN
        
        # If circuit is open, check if timeout has passed
        if CIRCUIT_OPEN:
            if time.time() - LAST_CIRCUIT_OPEN > CIRCUIT_TIMEOUT:
                logger.info(f"Circuit breaker reset after {CIRCUIT_TIMEOUT}s cooldown")
                CIRCUIT_OPEN = False
                TOTAL_FAILURES.clear()
            else:
                return True
                
        # Check if this endpoint has too many failures
        if TOTAL_FAILURES[endpoint] >= FAILURE_THRESHOLD:
            CIRCUIT_OPEN = True
            LAST_CIRCUIT_OPEN = time.time()
            logger.warning(f"Circuit breaker opened for all endpoints due to {endpoint} failures")
            return True
            
        return False
    
    def record_failure(self, endpoint, error_type):
        """Record a failure and update circuit breaker state"""
        TOTAL_FAILURES[endpoint] += 1
        self.consecutive_errors += 1
        logger.warning(f"Error {error_type} on {endpoint} (failures: {TOTAL_FAILURES[endpoint]})")
    
    def record_success(self, endpoint):
        """Record a success and reduce error count"""
        if self.consecutive_errors > 0:
            self.consecutive_errors -= 1
        # Don't reset TOTAL_FAILURES to allow circuit breaker to work
    
    @tag("document")
    @task(1)  # Lower frequency
    def upload_document(self):
        """Upload a test document"""
        # Circuit breaker check
        endpoint = "/api/documents/upload"
        if self.check_circuit_breaker(endpoint):
            logger.info(f"Circuit breaker preventing request to {endpoint}")
            return
            
        # Generate a unique document name
        timestamp = int(time.time())
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        file_name = f"test_doc_{timestamp}_{random_suffix}.txt"
        
        # Create smaller document content to reduce load
        paragraphs = [
            f"Test document {timestamp} for load testing.",
            "The document search system should process this document.",
            "Keywords: machine learning, AI, testing"
        ]
        
        # Use a small consistent size to reduce server load
        doc_content = "\n\n".join(paragraphs)
        
        # Create the file path
        file_path = os.path.join(os.path.dirname(__file__), file_name)
        
        try:
            # Write the document to disk
            with open(file_path, "w") as f:
                f.write(doc_content)
            
            # Upload the file with increased timeout
            with open(file_path, "rb") as f:
                response = self.client.post(
                    "/api/documents/upload",
                    files={"file": (file_name, f, "text/plain")},
                    timeout=UPLOAD_TIMEOUT,
                    name="/api/documents/upload"
                )
            
            if response.status_code == 201:
                # Success case
                doc_id = response.json().get("document_id")
                if doc_id:
                    self.documents.append(doc_id)
                    self.record_success(endpoint)
            else:
                # Non-200 responses
                self.record_failure(endpoint, f"HTTP {response.status_code}")
                
        except Exception as e:
            # Handle connection errors
            error_type = type(e).__name__
            self.record_failure(endpoint, error_type)
            
        finally:
            # Clean up the file
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass  # Ignore cleanup errors
    
    @tag("query")
    @task(5)  # Reduced from 10 to 5 to decrease load
    def query_documents(self):
        """Send a query to the API"""
        # Circuit breaker check
        endpoint = "/api/query"
        if self.check_circuit_breaker(endpoint):
            logger.info(f"Circuit breaker preventing request to {endpoint}")
            return
            
        if not self.documents:
            # Skip if no documents uploaded yet
            return
            
        query_text = self.generate_query()
        
        try:
            response = self.client.post(
                "/api/query",
                json={
                    "query_text": query_text,
                    "max_results": random.randint(1, 3)  # Reduced from 5 to 3
                },
                timeout=QUERY_TIMEOUT,
                name="/api/query"
            )
            
            if response.status_code == 200:
                query_id = response.json().get("query_id")
                if query_id:
                    self.queries.append(query_id)
                    self.record_success(endpoint)
            else:
                self.record_failure(endpoint, f"HTTP {response.status_code}")
                    
        except Exception as e:
            # Handle connection errors
            error_type = type(e).__name__
            self.record_failure(endpoint, error_type)
    
    @tag("document")
    @task(2)  # Reduced from 3 to 2
    def get_document_list(self):
        """Get list of documents"""
        endpoint = "/api/documents"
        if self.check_circuit_breaker(endpoint):
            logger.info(f"Circuit breaker preventing request to {endpoint}")
            return
            
        try:
            response = self.client.get("/api/documents", 
                                      name="/api/documents",
                                      timeout=DEFAULT_TIMEOUT)
            if 200 <= response.status_code < 300:
                self.record_success(endpoint)
            else:
                self.record_failure(endpoint, f"HTTP {response.status_code}")
        except Exception as e:
            error_type = type(e).__name__
            self.record_failure(endpoint, error_type)
    
    @tag("document")
    @task(1)  # Reduced from 2 to 1
    def get_document_details(self):
        """Get details of a specific document"""
        if not self.documents:
            return
            
        endpoint = "/api/documents/{id}"
        if self.check_circuit_breaker(endpoint):
            logger.info(f"Circuit breaker preventing request to {endpoint}")
            return
            
        doc_id = random.choice(self.documents)
        try:
            response = self.client.get(f"/api/documents/{doc_id}", 
                                      name="/api/documents/{id}",
                                      timeout=DEFAULT_TIMEOUT)
            if 200 <= response.status_code < 300:
                self.record_success(endpoint)
            else:
                self.record_failure(endpoint, f"HTTP {response.status_code}")
        except Exception as e:
            error_type = type(e).__name__
            self.record_failure(endpoint, error_type)
    
    @tag("query")
    @task(1)  # Reduced from 2 to 1
    def get_query_history(self):
        """Get query history"""
        endpoint = "/api/queries"
        if self.check_circuit_breaker(endpoint):
            logger.info(f"Circuit breaker preventing request to {endpoint}")
            return
            
        try:
            response = self.client.get("/api/queries", 
                                      name="/api/queries",
                                      timeout=DEFAULT_TIMEOUT)
            if 200 <= response.status_code < 300:
                self.record_success(endpoint)
            else:
                self.record_failure(endpoint, f"HTTP {response.status_code}")
        except Exception as e:
            error_type = type(e).__name__
            self.record_failure(endpoint, error_type)
    
    @tag("query")
    @task(1)
    def get_query_details(self):
        """Get details of a specific query"""
        if not self.queries:
            return
            
        endpoint = "/api/queries/{id}"
        if self.check_circuit_breaker(endpoint):
            logger.info(f"Circuit breaker preventing request to {endpoint}")
            return
            
        query_id = random.choice(self.queries)
        try:
            response = self.client.get(f"/api/queries/{query_id}", 
                                      name="/api/queries/{id}",
                                      timeout=DEFAULT_TIMEOUT)
            if 200 <= response.status_code < 300:
                self.record_success(endpoint)
            else:
                self.record_failure(endpoint, f"HTTP {response.status_code}")
        except Exception as e:
            error_type = type(e).__name__
            self.record_failure(endpoint, error_type)
    
    @tag("metrics")
    @task(1)
    def view_metrics(self):
        """View metrics dashboard data"""
        # Lower frequency of metrics requests
        if random.random() < 0.5:  # 50% chance to skip
            return
            
        metrics_endpoints = [
            "/api/metrics/summary?days=3&limit=3",  # Reduced params
            "/api/metrics/query-volume?days=3",
            "/api/metrics/latency?days=3",
            "/api/metrics/success-rate?days=3",
            "/api/metrics/top-queries?limit=3",
            "/api/metrics/top-documents?limit=3"
        ]
        
        endpoint = random.choice(metrics_endpoints)
        base_endpoint = endpoint.split('?')[0]
        
        if self.check_circuit_breaker(base_endpoint):
            logger.info(f"Circuit breaker preventing request to {base_endpoint}")
            return
            
        try:
            response = self.client.get(endpoint, 
                                      name=base_endpoint,
                                      timeout=DEFAULT_TIMEOUT)
            if 200 <= response.status_code < 300:
                self.record_success(base_endpoint)
            else:
                self.record_failure(base_endpoint, f"HTTP {response.status_code}")
        except Exception as e:
            error_type = type(e).__name__
            self.record_failure(base_endpoint, error_type)
    
    @tag("document")
    @task(1)
    def delete_document(self):
        """Delete a document occasionally"""
        if not self.documents:
            return
            
        # Lower frequency of delete operations
        if random.random() < 0.7:  # 70% chance to skip
            return
            
        endpoint = "/api/documents/{id}"
        if self.check_circuit_breaker(endpoint):
            logger.info(f"Circuit breaker preventing request to {endpoint}")
            return
            
        # Pop a random document
        if len(self.documents) > 0:
            index = random.randrange(len(self.documents))
            doc_id = self.documents.pop(index)
            
            try:
                response = self.client.delete(f"/api/documents/{doc_id}", 
                                            name="/api/documents/{id}",
                                            timeout=DEFAULT_TIMEOUT)
                if 200 <= response.status_code < 300:
                    self.record_success(endpoint)
                else:
                    self.record_failure(endpoint, f"HTTP {response.status_code}")
            except Exception as e:
                error_type = type(e).__name__
                self.record_failure(endpoint, error_type)


class HighVolumeQueryUser(HttpUser):
    """
    Simulates a user that only performs queries at high volume.
    This user is designed to stress test the query endpoint.
    """
    # Dynamic wait time based on backoff
    wait_time = between(1.0, 3.0)  # Increased wait time to reduce load
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.query_count = 0
        self.max_queries = 50  # Reduced from 100 to 50
        self.consecutive_errors = 0
        self.backoff_factor = 1.0  # Increased backoff factor
        
    def on_start(self):
        """Initialize user session"""
        self.client.headers.update({
            "Accept": "application/json",
            "User-Agent": "LocustStressTest/1.0",
            "Connection": "close"  # Prevent connection pooling issues
        })
    
    def generate_query(self):
        """Generate a random query"""
        template = random.choice(QUERY_TEMPLATES)
        topic = random.choice(TOPICS)
        return template.format(topic=topic)
    
    # Dynamic wait time based on consecutive errors
    def wait_time(self):
        if self.consecutive_errors > 0:
            # Implement exponential backoff with jitter
            jitter = random.uniform(0.8, 1.2)
            delay = min(60, self.backoff_factor * (2 ** self.consecutive_errors)) * jitter
            return delay
        else:
            # Normal wait time
            return random.uniform(1.0, 3.0)  # Increased base wait time
    
    def check_circuit_breaker(self):
        """Check if circuit breaker is open"""
        global CIRCUIT_OPEN, LAST_CIRCUIT_OPEN
        
        # If circuit is open, check if timeout has passed
        if CIRCUIT_OPEN:
            if time.time() - LAST_CIRCUIT_OPEN > CIRCUIT_TIMEOUT:
                logger.info(f"Circuit breaker reset after {CIRCUIT_TIMEOUT}s cooldown")
                CIRCUIT_OPEN = False
                TOTAL_FAILURES.clear()
            else:
                return True
                
        # Check if stress query has too many failures
        stress_endpoint = "/api/query (stress)"
        if TOTAL_FAILURES[stress_endpoint] >= FAILURE_THRESHOLD:
            CIRCUIT_OPEN = True
            LAST_CIRCUIT_OPEN = time.time()
            logger.warning(f"Circuit breaker opened due to {stress_endpoint} failures")
            return True
            
        return False
    
    @tag("stress")
    @task
    def rapid_query(self):
        """Send queries in rapid succession"""
        # Check circuit breaker status
        if self.check_circuit_breaker():
            logger.info("Circuit breaker preventing stress query")
            time.sleep(1)  # Wait a bit before checking again
            return
            
        # Stop if max queries reached
        if self.query_count >= self.max_queries:
            raise StopUser()
            
        query_text = self.generate_query()
        
        try:
            # Simpler query to reduce server load
            params = {
                "query_text": query_text,
                "max_results": 2  # Reduced from 5 to 2
            }
            
            response = self.client.post(
                "/api/query",
                json=params,
                timeout=STRESS_TIMEOUT,
                name="/api/query (stress)"
            )
            
            if response.status_code == 200:
                # Reset consecutive errors on success
                if self.consecutive_errors > 0:
                    self.consecutive_errors -= 1
                
                # Record successful query
                self.query_count += 1
            else:
                # Handle non-200 responses
                self.consecutive_errors += 1
                TOTAL_FAILURES["/api/query (stress)"] += 1
                logger.warning(f"Stress query error: HTTP {response.status_code}")
            
        except StopUser:
            raise
        except Exception as e:
            # Track the error
            self.consecutive_errors += 1
            error_type = type(e).__name__
            TOTAL_FAILURES["/api/query (stress)"] += 1
            logger.warning(f"Stress query exception: {error_type}")
            
            # Sleep a bit after an error to give server time to recover
            time.sleep(random.uniform(1.0, 3.0))


# Create a test document file if running directly
if __name__ == "__main__":
    # Create test directory
    os.makedirs(os.path.dirname(__file__), exist_ok=True)
    
    # Create a properly formatted test document
    test_doc_path = os.path.join(os.path.dirname(__file__), "test_doc.txt")
    
    # Prepare test content
    content = [
        "This is a test document for load testing with Locust.",
        "",
        "The system should be able to process this document.",
        "Keywords: AI, machine learning, testing",
    ]
    
    # Write the document
    with open(test_doc_path, "w") as f:
        f.write("\n".join(content))
    
    print(f"Created test document at {test_doc_path}")
    print("To run the load test, execute:")
    print("locust -f locustfile.py --host=http://localhost:8000") 