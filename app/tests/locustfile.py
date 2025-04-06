import json
import random
import time
from locust import HttpUser, task, between, constant, constant_pacing, tag, LoadTestShape
import os
import io

class DocumentQAUser(HttpUser):
    """
    Simulated user for load testing the Document Q&A Platform.
    
    This user simulates realistic behavior of interacting with the API:
    1. Getting a list of documents
    2. Querying documents
    3. Getting metrics
    """
    
    # Wait between 1 and 5 seconds between tasks
    wait_time = between(1, 5)
    
    def on_start(self):
        """Initialize the user session."""
        # Store IDs of documents we've seen
        self.document_ids = []
        # Store some sample queries
        self.sample_queries = [
            "How do I reset a user's password?",
            "What is our refund policy?",
            "How to troubleshoot API connection issues?",
            "What are the system requirements?",
            "How to upgrade to the premium plan?",
            "What are the key features of the product?",
            "How to contact customer support?",
            "What's the difference between basic and premium?",
            "How to export data from the system?",
            "What security measures are in place?"
        ]
        # Track errors for reporting
        self.errors = 0
        self.total_requests = 0
    
    @tag('health')
    @task(1)
    def get_health(self):
        """Check API health."""
        self.total_requests += 1
        response = self.client.get("/")
        if response.status_code != 200:
            self.errors += 1
    
    @tag('documents')
    @task(3)
    def get_documents(self):
        """Get a list of documents."""
        self.total_requests += 1
        response = self.client.get("/api/documents")
        
        if response.status_code == 200:
            data = response.json()
            if data["documents"]:
                # Store document IDs for later use
                self.document_ids = [doc["document_id"] for doc in data["documents"]]
        else:
            self.errors += 1
    
    @tag('query')
    @task(5)
    def query_documents(self):
        """Query documents."""
        self.total_requests += 1
        # Randomly select a query
        query_text = random.choice(self.sample_queries)
        
        # Create the request payload
        payload = {
            "query_text": query_text,
            "top_k": 4,
            "similarity_threshold": 0.7
        }
        
        # If we have document IDs and 50% chance, query specific documents
        if self.document_ids and random.random() > 0.5:
            # Select a random subset of documents
            doc_count = min(len(self.document_ids), 3)
            payload["document_ids"] = random.sample(self.document_ids, doc_count)
        
        # Make the request
        with self.client.post("/api/query", json=payload, catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Failed to query documents: {response.text}")
                self.errors += 1
    
    @tag('metrics')
    @task(2)
    def get_metrics_summary(self):
        """Get metrics summary."""
        self.total_requests += 1
        response = self.client.get("/api/metrics/summary")
        if response.status_code != 200:
            self.errors += 1
    
    @tag('metrics')
    @task(1)
    def get_query_volume(self):
        """Get query volume metrics."""
        self.total_requests += 1
        # Randomly choose different time periods
        days = random.choice([7, 14, 30])
        response = self.client.get(f"/api/metrics/query-volume?days={days}")
        if response.status_code != 200:
            self.errors += 1
    
    @tag('metrics')
    @task(1)
    def get_latency_metrics(self):
        """Get latency metrics."""
        self.total_requests += 1
        # Randomly choose different time periods
        days = random.choice([7, 14, 30])
        response = self.client.get(f"/api/metrics/latency?days={days}")
        if response.status_code != 200:
            self.errors += 1
    
    @tag('metrics')
    @task(1)
    def get_success_rate(self):
        """Get success rate metrics."""
        self.total_requests += 1
        # Randomly choose different time periods
        days = random.choice([7, 14, 30])
        response = self.client.get(f"/api/metrics/success-rate?days={days}")
        if response.status_code != 200:
            self.errors += 1
    
    @tag('metrics')
    @task(1)
    def get_top_queries(self):
        """Get top queries metrics."""
        self.total_requests += 1
        # Randomly choose different limits
        limit = random.choice([5, 10, 20])
        response = self.client.get(f"/api/metrics/top-queries?limit={limit}")
        if response.status_code != 200:
            self.errors += 1
    
    @tag('metrics')
    @task(1)
    def get_top_documents(self):
        """Get top documents metrics."""
        self.total_requests += 1
        # Randomly choose different limits
        limit = random.choice([5, 10, 20])
        response = self.client.get(f"/api/metrics/top-documents?limit={limit}")
        if response.status_code != 200:
            self.errors += 1
    
    @tag('query')
    @task(1)
    def get_demo_questions(self):
        """Get demo questions."""
        self.total_requests += 1
        response = self.client.get("/api/demo-questions")
        if response.status_code != 200:
            self.errors += 1


class DocumentUploadUser(HttpUser):
    """
    Simulated user for load testing document uploads.
    
    This user type focuses specifically on document upload operations,
    which are more resource-intensive than other API calls.
    """
    
    # Wait between 5 and 10 seconds between uploads
    wait_time = between(5, 10)
    
    def on_start(self):
        """Initialize the user session."""
        # Create a simple PDF-like content for testing
        self.pdf_content = b"%PDF-1.7\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 100>>\nstream\nBT\n/F1 12 Tf\n50 700 Td\n(Hello World) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000079 00000 n \n0000000173 00000 n \n0000000301 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n406\n%%EOF"
        self.uploaded_docs = []
        # Track errors for reporting
        self.errors = 0
        self.total_requests = 0
    
    @tag('upload')
    @task(1)
    def upload_document(self):
        """Upload a document."""
        self.total_requests += 1
        
        # Generate a unique filename
        filename = f"test_doc_{int(time.time())}_{random.randint(1000, 9999)}.pdf"
        
        # Create file-like object
        file_data = io.BytesIO(self.pdf_content)
        
        # Upload the file
        with self.client.post(
            "/api/documents/upload",
            files={"file": (filename, file_data, "application/pdf")},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.uploaded_docs.append(data["document_id"])
            else:
                response.failure(f"Failed to upload document: {response.text}")
                self.errors += 1
    
    @tag('upload_error')
    @task(1)
    def upload_invalid_document(self):
        """Upload an invalid document to test error handling."""
        self.total_requests += 1
        
        # Generate a unique filename with unsupported extension
        filename = f"test_doc_{int(time.time())}_{random.randint(1000, 9999)}.xyz"
        
        # Create file-like object with invalid content
        file_data = io.BytesIO(b"This is not a valid document format")
        
        # Upload the file - expecting a 415 Unsupported Media Type response
        with self.client.post(
            "/api/documents/upload",
            files={"file": (filename, file_data, "application/octet-stream")},
            catch_response=True
        ) as response:
            if response.status_code == 415:  # Expected error
                response.success()  # Mark as success since we're testing error handling
            else:
                response.failure(f"Expected 415 status code, got {response.status_code}")
                self.errors += 1
    
    @tag('check_docs')
    @task(2)
    def check_uploaded_documents(self):
        """Check status of previously uploaded documents."""
        self.total_requests += 1
        
        if not self.uploaded_docs:
            return
            
        # Randomly select one of the uploaded documents
        doc_id = random.choice(self.uploaded_docs)
        
        # Check document status
        response = self.client.get(f"/api/documents/{doc_id}")
        if response.status_code != 200:
            self.errors += 1


class ErrorTestUser(HttpUser):
    """
    User for testing error handling and edge cases.
    
    This user type focuses on sending invalid requests to test the API's error handling.
    """
    
    # Use constant wait time
    wait_time = constant(1)
    
    def on_start(self):
        """Initialize the user session."""
        # Track errors for reporting
        self.errors = 0
        self.total_requests = 0
    
    @tag('error')
    @task(1)
    def invalid_query(self):
        """Send an invalid query request."""
        self.total_requests += 1
        
        # Missing required field
        payload = {
            "top_k": 4,
            "similarity_threshold": 0.7
        }
        
        with self.client.post(
            "/api/query",
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code == 422:  # Expected validation error
                response.success()
            else:
                response.failure(f"Expected 422 status code, got {response.status_code}")
                self.errors += 1
    
    @tag('error')
    @task(1)
    def invalid_document_id(self):
        """Request a non-existent document."""
        self.total_requests += 1
        
        # Generate a random non-existent ID
        fake_id = f"nonexistent-{random.randint(10000, 99999)}"
        
        with self.client.get(
            f"/api/documents/{fake_id}",
            catch_response=True
        ) as response:
            if response.status_code == 404:  # Expected not found
                response.success()
            else:
                response.failure(f"Expected 404 status code, got {response.status_code}")
                self.errors += 1
    
    @tag('error')
    @task(1)
    def invalid_metrics_parameter(self):
        """Request metrics with invalid parameters."""
        self.total_requests += 1
        
        # Invalid days parameter (outside allowed range)
        invalid_days = random.choice([-10, 0, 100])
        
        with self.client.get(
            f"/api/metrics/query-volume?days={invalid_days}",
            catch_response=True
        ) as response:
            if response.status_code == 422:  # Expected validation error
                response.success()
            else:
                response.failure(f"Expected 422 status code, got {response.status_code}")
                self.errors += 1


class StressTest(LoadTestShape):
    """
    Custom load shape for stress testing.
    
    This shape increases the load gradually until reaching a peak,
    then sustains that peak for a period before gradually decreasing.
    """
    
    min_users = 5
    peak_users = 50
    time_limit = 600  # 10 minutes
    
    # How long it takes to ramp up to peak users
    ramp_up_time = 180  # 3 minutes
    
    # How long to stay at peak users
    peak_duration = 240  # 4 minutes
    
    # How long to ramp down from peak to min users
    ramp_down_time = 180  # 3 minutes
    
    def tick(self):
        run_time = self.get_run_time()
        
        if run_time < self.time_limit:
            if run_time < self.ramp_up_time:
                # Ramp up phase
                user_count = self.min_users + ((self.peak_users - self.min_users) * 
                                            (run_time / self.ramp_up_time))
                return (round(user_count), round(user_count / 10))  # (users, spawn_rate)
            elif run_time < (self.ramp_up_time + self.peak_duration):
                # Sustained peak phase
                return (self.peak_users, round(self.peak_users / 10))
            else:
                # Ramp down phase
                remaining = self.time_limit - run_time
                user_count = self.min_users + ((self.peak_users - self.min_users) * 
                                            (remaining / self.ramp_down_time))
                return (round(user_count), round(user_count / 10))
        return None  # End the test


class SpikeTest(LoadTestShape):
    """
    Custom load shape for spike testing.
    
    This shape creates sudden spikes in user traffic to test
    how the application handles abrupt changes in load.
    """
    
    stages = [
        {"duration": 60, "users": 5, "spawn_rate": 5},    # Normal load for 1 minute
        {"duration": 120, "users": 50, "spawn_rate": 10},  # Sudden spike to 50 users
        {"duration": 180, "users": 10, "spawn_rate": 10},  # Drop to 10 users
        {"duration": 240, "users": 40, "spawn_rate": 10},  # Another spike to 40 users
        {"duration": 300, "users": 5, "spawn_rate": 5},    # Back to normal load
    ]
    
    def tick(self):
        run_time = self.get_run_time()
        
        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])
                
        return None  # End the test 