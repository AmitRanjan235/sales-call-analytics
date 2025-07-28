# Sales Call Analytics Project

## Setup Steps
1. **Clone the repository**
   ```
   git clone <repo-link>
   ```

2. **Environment Variables**
   - Set up environment variables, particularly `OPENAI_API_KEY` for API access if using OpenAI.

3. **Database Initialization**
   - Ensure PostgreSQL is running.
   - Run Alembic migrations:
   ```
   alembic upgrade head
   ```

4. **Run Services**
   - Start the FastAPI server:
   ```
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
  - **Database**: Used PostgreSQL with SQLAlchemy for ORM and structured query capabilities.
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

