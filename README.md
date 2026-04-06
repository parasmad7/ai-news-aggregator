# AI News Aggregator

A modular, automated pipeline to aggregate latest news from top AI sources (YouTube, OpenAI, Anthropic), with full content extraction and Markdown conversion.

## 🚀 Key Features

-   **Multi-Source Tracking**: 
    -   📺 **YouTube**: Fetches latest videos from specified channels and extracts full transcripts.
    -   🤖 **OpenAI Blog**: Scrapes the official RSS feed and converts HTML posts to Markdown.
    -   🌩️ **Anthropic Blog**: Scrapes News, Engineering, and Research feeds with HTML-to-Markdown conversion.
-   **Agentic Intelligence (Vertex AI)**:
    -   📝 **Summarizer Agent**: Generates 2-3 line summaries for every video and post using **Gemini 2.5 Flash**.
    -   ⚖️ **Curator Agent**: Ranks news items (0.0 to 1.0) based on personalized user interests.
    -   📧 **Email Agent**: Tailors a premium HTML email digest with professional styling.
-   **Content Extraction**: Uses `docling` to convert blog URLs into structured Markdown, allowing for deep analysis and LLM processing.
-   **Structured Storage**: Uses **PostgreSQL** with **SQLAlchemy** to maintain a history of all discovered news.
-   **Modern Auth**: Uses Google Cloud **Application Default Credentials (ADC)** for secure, keyless access to Vertex AI.

## 🛠️ Tech Stack

-   **LLM Platform**: **Google Cloud Vertex AI** (Gemini 2.5 Flash)
-   **Core**: Python 3.11+
-   **News Sources**: `feedparser`, `requests`, `re`
-   **Extraction**: `docling`, `youtube-transcript-api`
-   **Database**: PostgreSQL, SQLAlchemy, psycopg2
-   **Validation**: Pydantic v2
-   **Environment**: `uv`, `python-dotenv`, `gcloud`

## 📁 Project Structure

```text
├── app/
│   ├── scrapers/          # Scraper implementations for YouTube, OpenAI, Anthropic
│   ├── database/          # SQLAlchemy models and repository
│   ├── schemas/           # Pydantic data models
│   ├── runner.py          # Unified entry point for aggregation logic
│   └── config.py          # Configuration (Channels, Time windows)
├── main.py                # Main script to run the aggregator
├── pyproject.toml         # Dependency management (uv)
└── docker/
    └── docker-compose.yml # PostgreSQL setup
```

## ⚙️ Setup & Installation

### 1. Prerequisite
Ensure you have [uv](https://github.com/astral-sh/uv) and [Docker](https://www.docker.com/) installed.

### 2. Database Setup
Spin up the PostgreSQL database using Docker Compose:
```bash
docker compose -f docker/docker-compose.yml up -d
```

### 3. Environment Configuration
Create a `.env` file in the `app/` directory with your database and Vertex AI details:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_news_aggregator
VERTEX_PROJECT_ID=your-project-id
VERTEX_LOCATION=us-central1
VERTEX_MODEL=gemini-2.5-flash
```

### 4. Vertex AI Authentication
Since the project uses Google Cloud Application Default Credentials (ADC), you must authenticate locally:
```bash
gcloud auth application-default login
```

### 5. Run the Aggregator
Sync dependencies and run the full pipeline:
```bash
uv run python main.py
```

## 🔄 How it Works

1.  **Unified Runner**: `main.py` calls the unified `run_all()` function in `app/runner.py`.
2.  **Scraping**: Each source (YouTube, OpenAI, Anthropic) is queried for new content within a configurable time window (default: 240 hours).
3.  **Extraction**:
    *   YouTube transcripts are fetched via `youtube-transcript-api`.
    *   Blog posts are converted to Markdown via `docling`.
4.  **Upsert**: The `NewsRepository` ensures that only new records are added, or existing records are updated if their content has changed.

---
Built with ❤️ for the AI community.
