"""
Test package for Document Search & Q&A Platform.

This package contains tests for the API endpoints, services, and utility functions.
"""

import os

# Ensure data directories exist for tests
os.makedirs("data/uploads", exist_ok=True)
os.makedirs("data/chroma_db", exist_ok=True)

# Set environment variables for testing
os.environ["MONGODB_URI"] = "mongodb://localhost:27017"
os.environ["DB_NAME"] = "document_qa_test"
os.environ["UPLOAD_FOLDER"] = "./data/uploads"
os.environ["VECTOR_DB_PATH"] = "./data/chroma_db"
os.environ["MAX_UPLOAD_SIZE"] = str(5 * 1024 * 1024)  # 5MB for tests 