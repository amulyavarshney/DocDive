# DocDive
## Dive Deep into Document Intelligence: A Document Search and Q&A Platform

## Architecture Diagram

```
┌───────────────────┐   Document Upload    ┌─────────────────────┐
│                   │─────────────────────>│                     │
│                   │                      │                     │
│   Retool UI       │   Query Documents    │  FastAPI Backend    │
│   Dashboard       │─────────────────────>│                     │
│                   │                      │                     │
│                   │   Get Metrics        │                     │
│                   │─────────────────────>│                     │
└───────────────────┘                      └─────────────────────┘
                                                   │
                                                   │
                                                   ▼
┌───────────────────┐                      ┌─────────────────────┐
│                   │                      │                     │
│  MongoDB          │◄────────────────────►│  Document Service   │
│  - Documents      │                      │  - Process Docs     │
│  - Queries        │                      │  - Embeddings       │
│  - Metrics        │                      │  - Storage          │
│                   │                      │                     │
└───────────────────┘                      └─────────────────────┘
         │                                            │
         │                                            ▼
         │                                 ┌─────────────────────┐
         │                                 │                     │
         │                                 │  Vector Database    │
         │                                 │  (ChromaDB)         │
         │                                 │  - Document Chunks  │
         │                                 │  - Embeddings       │
         │                                 │                     │
         │                                 └─────────────────────┘
         │                                            │
         ▼                                            ▼
┌───────────────────┐                      ┌─────────────────────┐
│                   │                      │                     │
│  Metrics Service  │                      │  Query Service      │
│  - Query Volume   │                      │  - Semantic Search  │
│  - Latency        │◄────────────────────►│  - LLM Integration  │
│  - Success Rate   │                      │  - Document Ranking │
│  - Top Queries    │                      │  - Citation         │
│                   │                      │                     │
└───────────────────┘                      └─────────────────────┘
                                                   │
                                                   ▼
                                          ┌─────────────────────┐
                                          │                     │
                                          │  LLM Service        │
                                          │  - Claude/GPT-4     │
                                          │  - Response Gen.    │
                                          │  - Citations        │
                                          │                     │
                                          └─────────────────────┘
```

## Component Descriptions

### Frontend Layer
- **Retool Dashboard**: Interactive UI for document management, Q&A interface, and metrics visualization.
  - Document upload and management interface with status tracking
  - Interactive Q&A interface with document selection and context highlighting
  - Real-time analytics dashboard with key performance indicators
  - User-friendly document browser with filtering capabilities

### API Layer
- **FastAPI Backend**: High-performance asynchronous API providing endpoints for document management, queries, and metrics.
  - RESTful API design with proper request validation
  - Comprehensive error handling and logging
  - Asynchronous processing for improved performance
  - OpenAPI documentation with interactive testing interface

### Service Layer
- **Document Service**: Handles document processing, chunking, and embedding generation.
  - Multi-format document parsing (PDF, Markdown, CSV, TXT)
  - Intelligent text chunking with configurable size and overlap
  - Multi-model embedding generation with automatic fallback system
  - Robust error handling and retry logic for processing reliability

- **Query Service**: Manages semantic search and LLM-powered answering.
  - Vector-based semantic search for context-aware retrieval
  - Dynamic prompt engineering to produce accurate, contextual responses
  - Source citation with document and chunk tracking
  - Automatic result filtering and ranking based on relevance

- **Metrics Service**: Collects, analyzes, and visualizes system performance data.
  - Real-time query tracking and performance monitoring
  - Advanced latency analysis with percentile breakdowns
  - Success rate calculation with error categorization
  - Identification of popular queries and documents
  - Trend analysis for system optimization

### Data Layer
- **MongoDB**: Document-oriented database for metadata and analytics.
  - Document metadata storage with indexing for fast retrieval
  - Query history with comprehensive logging
  - Performance metrics with time-series capabilities
  - System health and status tracking

- **ChromaDB**: Vector database optimized for similarity search.
  - Efficient similarity search with scalable indexing
  - Document chunks with rich metadata associations
  - Persistent vector embedding storage
  - Collection-based organization for logical separation

### External Services
- **LLM Integration**: Flexible connection to multiple language models.
  - Primary support for Azure OpenAI services
  - Fallback to OpenAI direct API
  - Alternative support for Anthropic Claude
  - Configurable model parameters for response quality
  - Comprehensive error handling with rate limiting and retries

### Infrastructure Components
- **Model Fallback System**: Ensures system reliability through model redundancy.
  - Cascading model selection based on availability and performance
  - Automatic switching between embedding providers
  - Performance monitoring to detect degraded services

- **Monitoring System**: Tracks system health and performance metrics.
  - API endpoint monitoring for availability
  - Database connection health checks
  - LLM service status tracking
  - Response time and error rate monitoring

### Testing & QA
- **Locust**: Load testing framework for performance evaluation.
  - Simulated user behavior for realistic testing
  - Performance benchmarking across various load scenarios
  - Bottleneck identification and optimization guidance
  - Regression testing for continuous improvement 