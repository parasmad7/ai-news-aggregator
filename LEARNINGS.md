# Project Learnings & Insights

This document captures key technical decisions, architectural shifts, and daily progress from the development of the AI News Aggregator.

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
