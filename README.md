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

## Backend
```
app/
├── api/            # API endpoints
├── core/           # Core application components
├── db/             # Database models and connections
├── models/         # Pydantic models
├── services/       # Business logic
│   ├── document_service.py   # Document processing
│   ├── query_service.py      # LLM integration & search
│   ├── metrics_service.py    # Performance tracking
│   ├── system_service.py     # System monitoring
│   └── chroma_client.py      # Vector DB client
└── main.py         # Application entry point
```

## Frontend
For a detailed frontend component descriptions, see [Frontend Documentation](frontend/README.md).

## Tech Stack
- **Backend**: Python 3.11+ with FastAPI
- **Document Processing**: LangChain with RecursiveCharacterTextSplitter
- **LLM Integration**: Azure OpenAI, OpenAI, Anthropic Claude
- **Vector Store**: ChromaDB
- **Database**: MongoDB
- **Frontend**: React + TypeScript with Vite
  - UI Components: shadcn/ui
  - Styling: Tailwind CSS
- **Load Testing**: Locust

## Setup Instructions

### Prerequisites
- Python 3.11+
- MongoDB
- Node.js 20+ and npm
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

3. Install backend dependencies
   ```
   pip install -r app/requirements.txt
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

5. Install frontend dependencies
   ```
   cd frontend
   npm install
   ```

6. Run the backend application
   ```
   cd ..  # Return to project root
   uvicorn app.main:app --reload
   ```

7. Run the frontend application (in a separate terminal)
   ```
   cd frontend
   npm run dev
   ```

### API Endpoints

#### Document Management
- `POST /api/documents/upload` - Upload documents
- `GET /api/documents` - List all documents
- `GET /api/documents/{document_id}` - Get document details
- `DELETE /api/documents/{document_id}` - Delete document
- `GET /api/documents/stats` - Get document statistics
- `GET /api/documents/type-distribution` - Get document type distribution

#### Query Operations
- `POST /api/query` - Query documents with LLM
- `GET /api/query/history` - Get query history
- `GET /api/query/{query_id}` - Get specific query

#### Metrics
- `GET /api/metrics` - Get performance metrics summary
- `GET /api/metrics/query-volume` - Get daily query volume
- `GET /api/metrics/latency` - Get average latency metrics
- `GET /api/metrics/success-rate` - Get query success rate
- `GET /api/metrics/top-queries` - Get most frequent queries
- `GET /api/metrics/top-documents` - Get most queried documents

#### System Operations
- `GET /api/system/health` - Check system health
- `GET /api/diagnostics` - Run system diagnostics
- `DELETE /api/reset-chromadb` - Reset ChromaDB
- `DELETE /api/reset-mongodb` - Reset MongoDB
- `POST /api/run-locust` - Run load tests

## Docker Deployment
You can also run the application using Docker:
```
docker-compose up -d
```

## Testing
DocDive includes comprehensive test suites for ensuring functionality and performance. For detailed information about running and extending tests, see the [Tests Documentation](tests/README.md).

### Running Tests
```
# Run all tests
python tests/run_tests.py all

# Run only E2E tests
python tests/run_tests.py e2e

# Run load tests
python tests/run_tests.py load
```

## Load Testing
Run load tests with Locust:
```
locust -f tests/locustfile.py
```

## Troubleshooting & FAQ

### Common Issues

**Q: ChromaDB connection fails when starting the application**
A: Ensure that the `VECTOR_DB_PATH` in your `.env` file points to a valid directory and that you have write permissions to that location.

**Q: LLM responses are slow or timing out**
A: Check your API key rate limits and connection to the LLM provider. You may need to increase the timeout settings in the config.

**Q: Document uploads fail for certain file types**
A: Verify that the file type is supported and that the document isn't corrupted or password-protected.

**Q: MongoDB connection errors**
A: Ensure MongoDB is running and accessible at the URI specified in your `.env` file.

## License
MIT 