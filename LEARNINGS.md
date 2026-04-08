# Project Learnings & Insights

This document captures key technical decisions, architectural shifts, and daily progress from the development of the AI News Aggregator.

---

### 2026-04-08

**What We Did**
- **Infrastructure Shift:** Replaced the Render-managed PostgreSQL database with a Neon Serverless Postgres DB by updating the `render.yaml` to accept a raw `DATABASE_URL` secret, unblocking Render free-tier friction.
- **Dependency Optimization:** Removed IBM's heavy `docling` (and its nested dependencies) and deployed the lightweight `html-to-markdown` library. This dramatically slims down the environment size for cloud deployments.
- **Graceful Scraper Fallbacks:** Maintained pipeline resilience against Cloudflare 403 Forbidden errors when scraping OpenAI from Render's datacenter IPs. The script successfully degrades to use RSS summaries instead of crashing.
- **SMTP Configuration Fixes:** Mapped custom UI environment variables (`MY_EMAIL`, `APP_PASSWORD`) directly to the `EmailService`, automatically configured Google SMTP defaults, and established self-routing delivery if no recipient is defined.

**Key Learnings**
- **Datacenter IPs & Cloudflare:** Deploying scrapers to loud datacenters (like AWS, Render) almost guarantees hitting 403 blocks from Cloudflare-protected sites (like OpenAI). 
- **Graceful Degradation:** A robust pipeline isn't one that never fails, it's one that handles failure cleanly. Because the scraper returned `None` instead of throwing an unhandled exception, our downstream AI summarizer effortlessly shifted to using the short RSS descriptions, ensuring the daily cron wasn't completely ruined by a single blocked request.
- **Dependency Weight Matters:** While `docling` is incredibly powerful for complex PDF/JS-heavy processing locally, deploying its 2-3GB footprint just to convert basic blog HTML is overkill, causing Docker build headaches on cloud platforms.

---

### 2026-04-06

**What We Did**
- **Hardware Audit:** Assessed M1 Mac (8GB RAM) capabilities for running local LLMs (Gemma 4 E2B vs Qwen 3.5 0.8B).
- **Vertex AI Migration:** Refactored the entire agentic pipeline (`SummarizerAgent`, `CuratorAgent`, `EmailAgent`) from the standard Gemini API to Google Cloud's **Vertex AI**.
- **Security & Auth:** Removed `GOOGLE_API_KEY` dependencies and implemented **Application Default Credentials (ADC)** via `gcloud`.
- **Model Upgrade:** Standardized on **Gemini 2.5 Flash** for all summarization and ranking tasks.
- **Documentation:** Updated `README.md` and created this learning log.

**Key Learnings**
- **Unified SDK:** The `google-genai` SDK v0.3.0+ is a "one-stop-shop" for both the developer API and Vertex AI. Switching between them is as simple as toggling a `vertexai=True` flag and providing project/location details.
- **Project IDs vs. Names:** In Vertex AI, the `project` argument in `vertexai.init()` or `genai.Client()` MUST be the **Project ID** (e.g., `playground-9192`), not the friendly Project Name (e.g., "Playground").
- **ADC over API Keys:** Static API keys are easier to start with, but ADC is more robust for local development as it ties directly to your `gcloud` identity and avoids "leaking" keys in environment files.

**Insights**
- **Model Scale vs. Task Complexity:** While a 0.8B model (Qwen 3.5) is perfect for local inference, tasks requiring complex HTML/CSS generation (like our Email Agent) or precise relevance ranking benefit significantly from the reasoning capabilities of a frontier model like Gemini 2.5 Flash.
- **Structured Output Reliability:** Pydantic integration in the GenAI SDK (via `response_mime_type="application/json"`) is the project's "secret sauce." It ensures that downstream services can always parse agent results without needing complex regex or manual string cleaning.

---

### 2026-04-04

**What We Did**
- **Content Extraction:** Integrated IBM's `docling` to handle blog-to-markdown conversion for OpenAI and Anthropic posts.
- **Database Refinement:** Truncated stale records and rebuilt the `posts` table with full markdown content.

**Key Learnings**
- **Docling Superiority:** For JS-heavy or complex AI research blogs (like Anthropic's), standard scrapers often return empty or messy text. `docling` handles these as first-class citizens, providing high-quality input for the LLM.

**Insights**
- **Garbage In, Garbage Out:** The quality of an AI summary is 90% dependent on the quality of the raw text extraction. Investing in a robust extraction layer like `docling` is a prerequisite for a reliable news aggregator.

---

## 🛠️ Best Practices & Architectural Patterns

### 1. Agent Isolation
Each agent (`Summarizer`, `Curator`, `Email`) should be entirely independent. If the Summarizer fails, the system should still be able to run scrapers. This "graceful degradation" is essential for long-running automated jobs.

### 2. Schema-Driven Design
Always define Pydantic models for LLM outputs. Never rely on the LLM to format raw text or manually parse JSON strings. This ensures that your agents act as reliable internal services.

### 3. Identity-Based Infrastructure
Favor **Application Default Credentials (ADC)** over static secrets like API keys. This is more secure and makes it easier to transition from local development to production on Google Cloud (Cloud Run, GKE, etc.).

---

## 🗺️ Future Roadmap (Next Steps to Try)

### 1. Hybrid Local/Cloud Inference
Use a lightweight local model (e.g., Qwen 3.5 0.8B) for "first-pass" filtering. If a detected news item is irrelevant (low score), discard it locally. Only call Vertex AI (Gemini 2.5 Flash) for high-value summarization and curation tasks.

### 2. Weekly Trend Analysis
Leverage the large context window of Gemini on Vertex AI. At the end of the week, feed all 100+ summaries into a single prompt to generate a "State of AI Weekly Report."

### 3. Multi-Modal Inputs
Instead of just summarizing text transcripts, feed the YouTube video frames themselves into Gemini (using GCS buckets) to capture visual-only information like charts, code snippets, or product demos.

### 4. Proactive Slack/Discord Alerts
Instead of waiting for a daily email, add a **SlackAgent** that pushes high-relevance (score > 0.9) news items to a dedicated channel in real-time.
