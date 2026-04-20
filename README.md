# AI News Aggregator

A modular, automated pipeline to aggregate latest news from top AI sources (YouTube, OpenAI, Anthropic), with full content extraction and Markdown conversion.

## 🚀 Key Features

-   **Autonomous Agentic Mode (Supervisor-Worker)**: 
    -   🧠 **Supervisor Agent**: A central manager that uses formal **Function Calling (Tool-Use)** to orchestrate the pipeline. It autonomously decides when to scrape, summarize, curate, or email.
    -   🔍 **Web Search Tool**: Integrated DuckDuckGo search that allows the agent to find external context for vague news items or deep-dive into breaking topics.
    -   🛡️ **Policy Throttling**: Implements a soft 24-hour email rule with an autonomous "Breaking News" override for high-relevance updates (Score > 0.9).
-   **Multi-Source Tracking**: 
    -   📺 **YouTube**: Fetches latest videos from specified channels and extracts full transcripts.
    -   🤖 **OpenAI Blog**: Scrapes the official RSS feed and converts HTML posts to Markdown.
    -   🌩️ **Anthropic Blog**: Scrapes News, Engineering, and Research feeds with HTML-to-Markdown conversion.
-   **Content Extraction**: Uses `html-to-markdown` for lightweight, high-speed conversion of blog URLs into structured Markdown.
-   **Structured Storage**: Uses **PostgreSQL** (Neon Serverless in Prod) with **SQLAlchemy** to maintain a content-aware history of all news.
-   **Modern Auth**: Uses Google Cloud **Application Default Credentials (ADC)** for secure, keyless access to Vertex AI.

## 🛠️ Tech Stack

-   **LLM Platform**: **Google Cloud Vertex AI** (Gemini 2.5 Flash)
-   **Core**: Python 3.11+
-   **Extraction**: `html-to-markdown`, `youtube-transcript-api`
-   **Database**: PostgreSQL, SQLAlchemy, psycopg2
-   **Validation**: Pydantic v2
-   **Environment**: `uv`, `python-dotenv`, `gcloud`

## 📁 Project Structure

```text
├── app/
│   ├── agent/             # Supervisor Agent and Tool definitions
│   ├── scrapers/          # Scraper implementations (YouTube, OpenAI, Anthropic)
│   ├── database/          # SQLAlchemy models and NewsRepository
│   ├── services/          # Worker services (Summarizer, Curator, Email, Scrapers)
│   ├── runner.py          # Entry point for the Agentic Loop
│   └── config.py          # Configuration (Channels, Interests, 24h Rules)
├── main.py                # Main script (Run everything)
└── pyproject.toml         # Dependency management (uv)
```

## ⚙️ Setup & Installation

### 1. Prerequisite
Ensure you have [uv](https://github.com/astral-sh/uv) installed.

### 2. Vertex AI Authentication
The project uses Google Cloud Application Default Credentials (ADC):
```bash
gcloud auth application-default login
```

### 3. Run the Aggregator
Sync dependencies and run the agent:
```bash
uv run python main.py
```

## 🔄 How it Works (Agentic Loop)

1.  **State Observation**: The `SupervisorAgent` fetches a detailed snapshot of the database (actual headlines, not just counts).
2.  **Autonomous Decision**: Based on the state and the 24-hour rule, Gemini decides the next best action (Scrape, Summarize, Curate, Search, or Email).
3.  **Tool Execution**: The agent calls formal Python functions to execute the work. If no new items are found after a scrape, the agent intelligently terminates the session to save resources.
4.  **Verification**: The system uses Pydantic schemas to ensure all agent outputs are structured and reliable.

---
Built with ❤️ for the AI community.
