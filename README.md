# Sales Call Analytics API

A production-ready FastAPI microservice for ingesting, analyzing, and providing AI-powered insights on sales call transcripts. Features include sentiment analysis, semantic similarity search, agent performance analytics, and personalized coaching recommendations using state-of-the-art machine learning models.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip or conda
- Git
- Docker (optional, for containerization)
- PostgreSQL (for production setup)

### Setup Steps

#### Option 1: Quick Setup (Recommended)
```bash
# Clone and navigate to the project
git clone <repo-link>
cd sales-call-analytics

# Run automated setup
python setup_dev.py

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Option 2: Manual Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create data directory and run migrations
mkdir data
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Generate Sample Data
```bash
# Generate synthetic sales call data for testing
python scripts/ingest_data.py

# Alternative: Create basic sample data
python create_sample_data.py
```

### Run Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## 📚 API Documentation

The API provides endpoints for retrieving call data, analytics, and AI-powered recommendations. Ensure the server is running on `http://localhost:8000`.

### Core Endpoints

#### 1. Health Check
**GET** `/api/v1/health`

Check the health status of the API service.

```bash
curl -X GET "http://localhost:8000/api/v1/health" \
  -H "accept: application/json"
```

**Response:**
```json
{
  "status": "healthy",
  "service": "sales-call-analytics",
  "version": "1.0.0",
  "timestamp": "<ISO formatted timestamp>"
}
```

#### 2. API Root
**GET** `/`

Get API information and documentation links.

```bash
curl -X GET "http://localhost:8000/" \
  -H "accept: application/json"
```

**Response:**
```json
{
  "message": "Sales Call Analytics API",
  "version": "1.0.0",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

### Call Management Endpoints

#### 3. Get Calls (with Filtering)
**GET** `/api/v1/calls`

Retrieve calls with optional filtering and pagination.

**Query Parameters:**
- `limit` (int, 1-100): Number of calls to return (default: 10)
- `offset` (int, ≥0): Number of calls to skip (default: 0)
- `agent_id` (string): Filter by specific agent
- `from_date` (datetime): Filter calls after this date
- `to_date` (datetime): Filter calls before this date
- `min_sentiment` (float, -1 to 1): Minimum sentiment score
- `max_sentiment` (float, -1 to 1): Maximum sentiment score

**Examples:**

```bash
# Get all calls (default pagination)
curl -X GET "http://localhost:8000/api/v1/calls" \
  -H "accept: application/json"

# Get calls by specific agent
curl -X GET "http://localhost:8000/api/v1/calls?agent_id=agent_001&limit=5" \
  -H "accept: application/json"

# Get calls with positive sentiment
curl -X GET "http://localhost:8000/api/v1/calls?min_sentiment=0.5&limit=10" \
  -H "accept: application/json"

# Get calls with date range and pagination
curl -X GET "http://localhost:8000/api/v1/calls?from_date=2023-07-01T00:00:00&to_date=2023-07-31T23:59:59&offset=20&limit=10" \
  -H "accept: application/json"
```

#### 4. Get Call Details
**GET** `/api/v1/calls/{call_id}`

Retrieve complete details of a specific call, including transcript and embeddings.

```bash
# Get specific call details
curl -X GET "http://localhost:8000/api/v1/calls/call_0001" \
  -H "accept: application/json"

# Example with different call ID
curl -X GET "http://localhost:8000/api/v1/calls/call_0015" \
  -H "accept: application/json"
```

**Response includes:**
- Full transcript
- Sentiment scores
- Agent talk ratio
- Embedding vectors (if available)
- Timestamps

#### 5. Get Call Recommendations
**GET** `/api/v1/calls/{call_id}/recommendations`

Get AI-powered recommendations including similar calls and coaching nudges.

```bash
# Get recommendations for a specific call
curl -X GET "http://localhost:8000/api/v1/calls/call_0001/recommendations" \
  -H "accept: application/json"

# Get recommendations for another call
curl -X GET "http://localhost:8000/api/v1/calls/call_0010/recommendations" \
  -H "accept: application/json"
```

**Response includes:**
- Similar calls (based on embedding similarity)
- Coaching nudges (AI-generated improvement suggestions)
- Similarity scores

### Analytics Endpoints

#### 6. Get Agent Analytics
**GET** `/api/v1/analytics/agents`

Retrieve performance analytics for all agents.

```bash
curl -X GET "http://localhost:8000/api/v1/analytics/agents" \
  -H "accept: application/json"
```

**Response includes:**
- Average sentiment scores per agent
- Average talk ratios
- Total call counts
- Performance rankings

### WebSocket Endpoint (Real-time)

#### 7. Real-time Sentiment Updates
**WebSocket** `/api/v1/ws/sentiment/{call_id}`

Stream real-time sentiment updates for a specific call (demonstration feature).

```javascript
// JavaScript WebSocket example
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/sentiment/call_0001');
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Sentiment update:', data);
};
```

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Technical Architecture

### Technology Stack

#### Core Framework
- **FastAPI**: High-performance async web framework with automatic OpenAPI documentation
- **Uvicorn**: ASGI server for production-grade performance
- **Pydantic**: Data validation and serialization with type hints

#### Database & ORM
- **SQLAlchemy**: Full-featured ORM with async support
- **Alembic**: Version-controlled database migrations
- **SQLite**: Development database with easy setup
- **PostgreSQL**: Production database with full-text search capabilities

#### AI/ML Stack
- **Sentence Transformers**: Pre-trained models for semantic embeddings
- **Transformers (Hugging Face)**: State-of-the-art NLP models
- **scikit-learn**: Machine learning utilities for similarity calculations
- **OpenAI API**: Optional integration for advanced coaching insights
- **NumPy**: Efficient numerical computing for vector operations

#### Development & Testing
- **Pytest**: Comprehensive testing framework with async support
- **Black & isort**: Code formatting and import organization
- **MyPy**: Static type checking for Python
- **Docker**: Containerization for consistent deployments

#### Data Processing
- **aiohttp & asyncio**: Async HTTP client and concurrency primitives
- **Faker**: Synthetic data generation for testing and development

### AI/ML Components
1. **Sentiment Analysis**: DistilBERT-base model (`distilbert-base-uncased-finetuned-sst-2-english`) for accurate customer sentiment scoring (-1 to +1 scale)
2. **Semantic Embeddings**: Sentence-BERT model (`sentence-transformers/all-MiniLM-L6-v2`) for generating 384-dimensional vector representations
3. **Similarity Search**: Cosine similarity with scikit-learn for finding semantically related calls
4. **Talk Ratio Analysis**: Regex-based parsing to calculate agent vs customer speaking time
5. **Coaching Recommendations**: OpenAI GPT-3.5-turbo integration with intelligent rule-based fallbacks
6. **Async Data Pipeline**: High-performance ingestion with aiohttp and asyncio for scalable data processing

### Database Schema

#### Calls Table
- `id`: Primary key (integer)
- `call_id`: Unique call identifier (string)
- `agent_id`: Agent identifier for performance tracking
- `customer_id`: Customer identifier for relationship mapping
- `language`: Call language (default: English)
- `start_time`: Call timestamp with timezone support
- `duration_seconds`: Call duration for efficiency analysis
- `transcript`: Full call transcript text
- `agent_talk_ratio`: Calculated speaking time ratio (0.0-1.0)
- `customer_sentiment_score`: AI-computed sentiment (-1.0 to +1.0)
- `embedding`: JSON-stored 384-dimensional vector for similarity search
- `created_at`/`updated_at`: Record lifecycle timestamps

#### Analytics Table
- Pre-computed agent performance metrics
- Average sentiment scores per agent
- Average talk ratios and call volumes
- Optimized for dashboard queries

#### Database Indexes
- `idx_calls_agent_id`: Fast agent filtering
- `idx_calls_start_time`: Temporal queries
- `idx_calls_call_id`: Unique call lookups
- Composite indexes for common filter combinations

## ⚖️ Trade-offs and Assumptions

### Design Trade-offs

1. **SQLite vs PostgreSQL**
   - **Choice**: SQLite for development, PostgreSQL recommended for production
   - **Trade-off**: SQLite enables quick local setup but lacks concurrent write performance
   - **Impact**: Single-user development vs. multi-user production requirements

2. **Synchronous vs Asynchronous Processing**
   - **Choice**: Synchronous API responses with async framework support
   - **Trade-off**: Immediate responses vs. potentially longer wait times for complex operations
   - **Impact**: Better user experience but may require background job processing for large datasets

3. **In-Memory vs Persistent Embeddings**
   - **Choice**: Store embeddings in database as JSON strings
   - **Trade-off**: Database size increase vs. real-time embedding computation
   - **Impact**: Faster similarity searches but larger storage requirements

4. **Local Models vs Cloud APIs**
   - **Choice**: Local Hugging Face models with OpenAI as optional enhancement
   - **Trade-off**: Privacy and cost control vs. cutting-edge model performance
   - **Impact**: System works fully offline but can leverage cloud AI when available

5. **Pagination Strategy**
   - **Choice**: Offset-based pagination with configurable limits
   - **Trade-off**: Simple implementation vs. cursor-based pagination for large datasets
   - **Impact**: Works well for moderate datasets but may have performance issues at scale

### Key Assumptions

1. **Data Quality**
   - Assumes call transcripts are reasonably clean and formatted
   - Assumes agent/customer speaker identification is available in transcripts
   - Impact: Affects accuracy of talk ratio calculations and sentiment analysis

2. **Scale Requirements**
   - Assumes moderate dataset size (thousands, not millions of calls)
   - Assumes single-instance deployment for MVP
   - Impact: Architecture choices optimized for development and small-scale production

3. **Network Availability**
   - Assumes internet connectivity for downloading ML models initially
   - Assumes optional connectivity for OpenAI API features
   - Impact: First-time setup requires internet; runtime can be fully offline

4. **Language Support**
   - Assumes English-language calls primarily
   - Models are trained on English datasets
   - Impact: May require model changes for multilingual support

5. **Security Model**
   - JWT authentication middleware implemented but not enforced by default
   - Assumes deployment in trusted network environment for MVP
   - Impact: Security infrastructure ready but requires configuration for production

### Mitigation Strategies

1. **Scalability**: Implement caching, database connection pooling, and consider microservices architecture
2. **Performance**: Add database indexes, implement background job processing with Celery
3. **Reliability**: Add comprehensive error handling, retry mechanisms, and health checks
4. **Security**: Implement API key authentication, rate limiting, and input validation
5. **Monitoring**: Add logging, metrics collection, and alerting for production deployment

## 📊 Performance Considerations

### Current Optimizations
- **Database Queries**: Strategic indexes on `agent_id`, `start_time`, and `call_id` for sub-second query performance
- **Embedding Storage**: JSON format in database for immediate deployment, with vector database migration path
- **Model Loading**: AI models loaded once at startup and cached in memory for consistent response times
- **Async Architecture**: FastAPI's async capabilities handle 1000+ concurrent requests efficiently
- **Query Optimization**: Intelligent pagination and filtering to minimize database load

### Scalability Recommendations
- **Vector Database**: Migrate to Pinecone, Weaviate, or pgvector for large-scale similarity search
- **Caching Layer**: Add Redis for frequently accessed analytics and recommendations
- **Background Processing**: Implement Celery for async embedding generation and batch analytics
- **Database Sharding**: Partition by time periods for datasets exceeding 1M calls
- **CDN Integration**: Cache static model files and API responses at edge locations

## 🐳 Docker Deployment

### Build and Run with Docker

```bash
# Build the Docker image
docker build -t sales-call-analytics .

# Run the container
docker run -p 8000:8000 sales-call-analytics
```

### Docker Compose (with PostgreSQL)

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/sales_analytics
      - SECRET_KEY=your-secret-key
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=sales_analytics
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

The project includes a comprehensive CI/CD pipeline that:

1. **Installs Dependencies** - Sets up Python 3.11 and installs requirements
2. **Runs Database Migrations** - Sets up PostgreSQL schema with Alembic
3. **Executes Tests** - Runs all 30+ test cases with pytest
4. **Performs Type Checking** - Validates code with mypy
5. **Builds Docker Image** - Creates production-ready container
6. **Pushes to Registry** - Deploys to Docker Hub (on main branch only)

### Workflow Triggers
- **Push to main branch** - Full pipeline with deployment
- **Pull requests** - Testing and validation only

### Required Secrets
For full CI/CD pipeline, add these GitHub secrets:
- `DOCKER_USERNAME` - Your Docker Hub username
- `DOCKER_PASSWORD` - Your Docker Hub password/token
- `OPENAI_API_KEY` - (Optional) For enhanced coaching features

### Pipeline Status
The CI pipeline ensures:
- ✅ Code formatting (black, isort)
- ✅ Type safety (mypy)
- ✅ Test coverage (pytest)
- ✅ Container builds successfully
- ✅ Production-ready deployments

## 🚀 Production Deployment

### Environment Variables

Set these environment variables for production:

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Security
SECRET_KEY=your-super-secret-key-here

# Optional: OpenAI API for enhanced coaching
OPENAI_API_KEY=your-openai-api-key

# Optional: Redis for background tasks
REDIS_URL=redis://redis:6379
```

### Production Checklist

1. **Database**: Migrate to PostgreSQL with proper connection pooling
2. **Security**: Add authentication, HTTPS, and API rate limiting
3. **Monitoring**: Implement logging, metrics, and health checks
4. **Scaling**: Use multiple instances behind a load balancer
5. **Background Jobs**: Add Celery for async processing of large datasets
6. **Backup**: Set up automated database backups
7. **SSL/TLS**: Enable HTTPS with proper certificates
8. **Resource Limits**: Configure memory and CPU limits

### Health Checks

Use the health endpoint for load balancer and monitoring:

```bash
# Health check endpoint
GET /api/v1/health

# Expected response (200 OK)
{
  "status": "healthy",
  "service": "sales-call-analytics",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Ensure all tests pass (`pytest tests/ -v`)
5. Run code formatting (`black . && isort .`)
6. Submit a pull request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write comprehensive tests for new features
- Update documentation for API changes
- Ensure backward compatibility when possible

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses
- Hugging Face Transformers: Apache 2.0
- Sentence Transformers: Apache 2.0
- FastAPI: MIT License
- SQLAlchemy: MIT License

## 📞 Support

- **Documentation**: Visit `/docs` endpoint when running locally
- **Issues**: Report bugs and feature requests via GitHub Issues
- **API Reference**: Auto-generated OpenAPI documentation at `/redoc`

---

**Built with ❤️ using FastAPI, Transformers, and modern Python practices.**

