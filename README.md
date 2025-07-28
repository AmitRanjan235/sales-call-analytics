# Sales Call Analytics Project

## Setup Steps

### Quick Setup (Recommended)
1. **Clone the repository**
   ```bash
   git clone <repo-link>
   cd sales-call-analytics
   ```

2. **Run the development setup script**
   ```bash
   python setup_dev.py
   ```
   This will:
   - Create the SQLite database directory
   - Install Python dependencies
   - Run database migrations
   - Set up the development environment

3. **Configure Environment Variables**
   - Copy `.env` file and update `OPENAI_API_KEY` if using OpenAI features

4. **Start the Development Server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Manual Setup
1. **Environment Variables**
   - Set up environment variables, particularly `OPENAI_API_KEY` for API access if using OpenAI.

2. **Database Initialization**
   - Create data directory: `mkdir data`
   - Install dependencies: `pip install -r requirements.txt`
   - Run Alembic migrations: `alembic upgrade head`

3. **Run Services**
   - Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Execute Ingestion Script**
   - Run the data ingestion script:
   ```
   python scripts/ingest_data.py
   ```

6. **Example Endpoints**
   - Use `curl` to test API endpoints:
     ```
     curl -X GET "http://localhost:8000/api/v1/calls"
     ```

## Design Notes
- **Tech Choices:**
  - **Async I/O**: Utilized `aiohttp` and `asyncio` for non-blocking ingestion.
  - **Database**: Uses SQLite for development (easily switchable to PostgreSQL for production) with SQLAlchemy for ORM and structured query capabilities.
  - **Embedding and Sentiment Analysis**: Leveraged `sentence-transformers` and Hugging Face for NLP tasks.

- **Index Rationale:**
  - **agent_id, start_time**: Added indexes to speed up querying by agents and time range.

- **Error Handling Strategy:**
  - Comprehensive exception handling throughout the pipeline to manage and log ingestion errors.

- **Scaling Strategy:**
  - Consider using Celery with a message broker like RabbitMQ for scaling ingestion tasks.

## Trade-offs or Assumptions
- Assumed availability of internet for all necessary API calls.

## Licenses
Include the license file for any downloaded datasets in the `/data` folder.

