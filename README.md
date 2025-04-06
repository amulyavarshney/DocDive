# DocDive
## Dive Deep into Document Intelligence: A Document Search and Q&A Platform

## Overview
DocDive is an advanced LLM-powered document search and Q&A platform that enables users to dive deep into their documents to extract meaningful insights and answers. Built for teams that need precise information retrieval from large document collections, DocDive combines vector embeddings, semantic search, and state-of-the-art language models to deliver accurate, context-aware responses with relevant citations.

## Features
- **Document Management**: Upload and manage PDF, Markdown, CSV, and text documents with automatic processing
- **AI-powered Q&A**: Query documents using LLM-based retrieval with relevant citations and context
- **Semantic Search**: Leverage vector embeddings to find information based on meaning, not just keywords
- **Multiple Embedding Models**: Fallback architecture ensures reliability with various embedding options
- **Performance Metrics**: Track query volume, latency, success rates, and popular queries
- **Interactive Dashboard**: Visualize performance metrics and system health
- **API-first Architecture**: Built with FastAPI for high performance and scalability

## Architecture
For a detailed architecture diagram and component descriptions, see [Architecture Documentation](architecture.md).

```
app/
├── api/            # API endpoints
├── core/           # Core application components
├── db/             # Database models and connections
├── models/         # Pydantic models
├── services/       # Business logic
│   ├── document/   # Document processing
│   ├── embedding/  # Vector embedding
│   ├── llm/        # LLM integration
│   └── metrics/    # Performance tracking
├── utils/          # Utility functions
└── frontend/       # Retool frontend components
```

## Tech Stack
- **Backend**: Python 3.11+ with FastAPI
- **Document Processing**: LangChain with RecursiveCharacterTextSplitter
- **LLM Integration**: Azure OpenAI, OpenAI, Anthropic Claude
- **Vector Store**: ChromaDB
- **Database**: MongoDB
- **Frontend**: Retool
- **Load Testing**: Locust

## Setup Instructions

### Prerequisites
- Python 3.11+
- MongoDB
- API keys for LLM services (OpenAI/Azure OpenAI/Anthropic)

### Installation
1. Clone the repository
   ```
   git clone https://github.com/amulyavarshney/docdive.git
   cd docdive
   ```

2. Create a virtual environment
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your configuration
   ```
   # Database settings
   MONGODB_URI=mongodb://localhost:27017
   DB_NAME=docdive
   
   # LLM API keys
   OPENAI_API_KEY=your_openai_key
   ANTHROPIC_API_KEY=your_anthropic_key
   AZURE_OPENAI_API_KEY=your_azure_key
   AZURE_OPENAI_API_VERSION=2023-05-15
   AZURE_OPENAI_ENDPOINT=your_azure_endpoint
   AZURE_OPENAI_MODEL=your_deployment_name
   AZURE_OPENAI_EMBEDDING_MODEL=your_embedding_deployment
   
   # Storage settings
   UPLOAD_FOLDER=./data/uploads
   VECTOR_DB_PATH=./data/chroma_db
   
   # Chunking settings
   DEFAULT_CHUNK_SIZE=1000
   DEFAULT_CHUNK_OVERLAP=200
   DEFAULT_TOP_K=4
   ```

5. Run the application
   ```
   uvicorn app.main:app --reload
   ```

### API Endpoints
- `POST /api/documents/upload` - Upload documents
- `GET /api/documents` - List all documents
- `GET /api/documents/{document_id}` - Get document details
- `DELETE /api/documents/{document_id}` - Delete document
- `POST /api/query` - Query documents with LLM
- `GET /api/query/history` - Get query history
- `GET /api/query/{query_id}` - Get specific query
- `GET /api/metrics` - Get performance metrics
- `GET /api/system/health` - Check system health

## Dashboard
Access the Retool dashboard at: [Dashboard URL]

## Load Testing
Run load tests with Locust:
```
locust -f app/tests/locustfile.py
```

## License
MIT 