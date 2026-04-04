# AI News Aggregator

A modular, automated pipeline to aggregate latest news from top AI sources (YouTube, OpenAI, Anthropic), with full content extraction and Markdown conversion.

## 🚀 Key Features

-   **Multi-Source Tracking**: 
    -   📺 **YouTube**: Fetches latest videos from specified channels and extracts full transcripts.
    -   🤖 **OpenAI Blog**: Scrapes the official RSS feed and converts HTML posts to Markdown.
    -   🌩️ **Anthropic Blog**: Scrapes News, Engineering, and Research feeds with HTML-to-Markdown conversion.
-   **Content Extraction**: Uses `docling` to convert blog URLs into structured Markdown, allowing for deep analysis and LLM processing.
-   **Structured Storage**: Uses **PostgreSQL** with **SQLAlchemy** to maintain a history of all discovered news.
-   **Data Validation**: Leverages **Pydantic** schemas for robust data handling across different sources.
-   **Modern Stack**: Powered by **uv** for high-performance dependency management and **Docker** for local database management.

## 🛠️ Tech Stack

-   **Core**: Python 3.11+
-   **News Sources**: `feedparser`, `requests`, `re`
-   **Extraction**: `docling`, `youtube-transcript-api`
-   **Database**: PostgreSQL, SQLAlchemy, psycopg2
-   **Validation**: Pydantic
-   **Environment**: `uv`, `python-dotenv`

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
Create a `.env` file in the root directory (optional - defaults to PostgreSQL container):
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_news_aggregator
```

### 4. Run the Aggregator
Sync dependencies and run the aggregation pipeline:
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
