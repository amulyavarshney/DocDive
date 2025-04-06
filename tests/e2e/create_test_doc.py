#!/usr/bin/env python3
"""
Creates a test document for e2e tests.
This script ensures that the test document is properly formatted and contains
adequate test content for document processing systems to work with.
"""

import os
import random
from pathlib import Path

# Define the file path
SCRIPT_DIR = Path(__file__).parent
TEST_DOC_PATH = SCRIPT_DIR / "test_document.pdf"

def create_test_document():
    """Create a test PDF document for testing."""
    print(f"Creating test document at {TEST_DOC_PATH}")
    
    try:
        # Try to use reportlab to create a proper PDF
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        c = canvas.Canvas(str(TEST_DOC_PATH), pagesize=letter)
        
        # Add a title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, "E2E Test Document")
        
        # Add content
        c.setFont("Helvetica", 12)
        y_position = 700
        
        paragraphs = [
            "This is a test document created for end-to-end testing of the document search system.",
            f"Document ID: TEST-{random.randint(1000, 9999)}",
            "The system should be able to process this document and extract its content for searching.",
            "",
            "Machine learning and artificial intelligence technologies enable powerful document search capabilities.",
            "Natural language processing allows computers to understand human language patterns.",
            "Vector embeddings represent text as mathematical objects to find semantic similarities.",
            "",
            "This document contains various terms that can be used to test search functionality:",
            "- Artificial Intelligence",
            "- Machine Learning",
            "- Natural Language Processing",
            "- Document Search",
            "- Question Answering",
            "- Information Retrieval",
            "",
            f"Generated at: {random.randint(1000000, 9999999)}"
        ]
        
        for paragraph in paragraphs:
            if paragraph == "":
                y_position -= 20
                continue
                
            c.drawString(100, y_position, paragraph)
            y_position -= 20
            
            # Start a new page if we're running out of space
            if y_position < 100:
                c.showPage()
                y_position = 750
        
        # Add a second page with more content
        c.showPage()
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, 750, "Additional Test Content")
        
        c.setFont("Helvetica", 12)
        y_position = 700
        
        more_paragraphs = [
            "This is a second page of the test document.",
            "Multiple pages help test the document processing capability.",
            "",
            "Document retrieval systems should be able to:",
            "- Process multi-page documents",
            "- Extract text from various formats",
            "- Split content into chunks",
            "- Create embeddings of the content",
            "- Index the content for fast retrieval",
            "",
            "When a query is submitted, the system should:",
            "1. Parse the query text",
            "2. Convert it to an embedding",
            "3. Find similar content in the document",
            "4. Return relevant responses",
            "",
            f"Test document reference code: {random.randint(10000, 99999)}"
        ]
        
        for paragraph in more_paragraphs:
            if paragraph == "":
                y_position -= 20
                continue
                
            c.drawString(100, y_position, paragraph)
            y_position -= 20
        
        # Save the document
        c.save()
        print("PDF document created successfully using reportlab")
        return True
        
    except ImportError:
        # Fall back to creating a simple PDF if reportlab is not available
        print("reportlab not available, creating basic PDF file")
        with open(TEST_DOC_PATH, "wb") as f:
            f.write(b"%PDF-1.4\n")
            f.write(b"1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n")
            f.write(b"2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n")
            f.write(b"3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Contents 4 0 R/Resources<<>>>>\nendobj\n")
            f.write(b"4 0 obj\n<</Length 71>>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(This is a test document for e2e testing) Tj\nET\nendstream\nendobj\n")
            f.write(b"xref\n0 5\n0000000000 65535 f\n0000000010 00000 n\n0000000053 00000 n\n0000000102 00000 n\n0000000179 00000 n\ntrailer\n<</Size 5/Root 1 0 R>>\nstartxref\n299\n%%EOF\n")
        print("Basic PDF document created")
        return True
    
    except Exception as e:
        print(f"Error creating test document: {str(e)}")
        return False


if __name__ == "__main__":
    # Create the parent directory if it doesn't exist
    os.makedirs(SCRIPT_DIR, exist_ok=True)
    
    # Create the test document
    if create_test_document():
        print(f"Test document created at: {TEST_DOC_PATH}")
    else:
        print("Failed to create test document") 