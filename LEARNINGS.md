# Project Learnings & Insights

This document captures key technical decisions, architectural shifts, and daily learnings from the development of the AI News Aggregator.

## 🚀 Technical Milestones

### 2026-04-06: Migration to Vertex AI (Gemini 2.5 Flash)
- **Decision:** Shifted from the standalone Gemini API to **Vertex AI** via Google Cloud.
- **Why:** Vertex AI offers better enterprise reliability, easier project management on Google Cloud, and access to the latest frontier models like **Gemini 2.5 Flash**.
- **SDK Choice:** Leveraged the unified `google-genai` SDK. Even though the legacy `vertexai` library exists, the modern GenAI SDK is now the recommended path for both Gemini API and Vertex AI, providing a consistent interface for multimodal inputs and structured outputs.
- **Authentication Shift:** Moved away from static `GOOGLE_API_KEY` in favor of **Application Default Credentials (ADC)**. Running `gcloud auth application-default login` creates a more secure, local-agent-based environment.

### 2026-04-04: Deep Content Extraction with Docling
- **Decision:** Integrated IBM's `docling` for blog post extraction.
- **Insight:** Traditional HTML-to-Markdown libraries often fail on complex JS-heavy blogs. `docling` provides much more robust structured output, which significantly improves the quality of LLM-generated summaries.

## 🧠 Architectural Insights

### Multi-Agent vs. Single-Pipeline
The project uses a dedicated agentic structure (`SummarizerAgent`, `CuratorAgent`, `EmailAgent`):
- **Isolation:** Each agent has a single responsibility (summarization, ranking, or email tailoring).
- **Structured Output:** Using Pydantic schemas with `response_mime_type="application/json"` is critical for reliability. It virtually eliminates "hallucinated JSON" or parsing errors that common prompting techniques often suffer from.

### Local vs. Cloud LLMs
- **Experiment:** Briefly explored using **Qwen 3.5 0.8B** via Ollama for a purely local setup.
- **Learning:** While 0.8B models are incredibly fast on M1 Mac Silicon, frontier models like Gemini 2.5 Flash on Vertex AI provide significantly better reasoning for curation tasks and HTML styling for emails.
