# Misinfo Buster - WhatsApp Misinformation Fact-Checker

A production-ready, modular agent system that fact-checks WhatsApp forwards. Takes text, image screenshots, or URLs as input, extracts verifiable claims, and returns structured verdicts using web search and RAG.

Supports Hindi and English text, including text inside image screenshots.

## Architecture

```
Input (text/image/url)
        |
        v
  +------------+
  |  OCR Node  |  (EasyOCR for images, httpx for URLs, passthrough for text)
  +------------+
        |
        v
  +-------------------+
  | Claim Extractor   |  (LLM extracts verifiable factual claims)
  +-------------------+
        |
        v
  +--[Router]--+
  |            |
  v            v
+---------------+   +---------------+
| Fact Checker  |   | Verdict Node  |  (skip if no claims)
| (per-claim)   |   | (early exit)  |
+---------------+   +---------------+
  |
  v
+---------------+
| Verdict Node  |  (aggregate all claim verdicts)
+---------------+
        |
        v
  CheckResponse {verdict, confidence, explanation, sources}
```

## Tech Stack

| Purpose | Library |
|---|---|
| Agent orchestration | LangGraph |
| LLM | Groq (llama-3.3-70b-versatile) |
| OCR | EasyOCR (English + Hindi) |
| Web search | Tavily |
| Vector DB | ChromaDB |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| API | FastAPI + Uvicorn |
| Demo UI | Streamlit |

## Prerequisites

- Python 3.11+
- A Groq API key (free at https://console.groq.com)
- A Tavily API key (free at https://tavily.com)

## Local Setup

1. Clone the repository and navigate to the project directory:

```bash
cd misinfo_buster
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create your `.env` file from the template:

```bash
cp .env.example .env
```

5. Edit `.env` and add your API keys:

```
GROQ_API_KEY=your_actual_groq_key
TAVILY_API_KEY=your_actual_tavily_key
```

6. Run the API server:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

7. In a separate terminal, run the Streamlit UI:

```bash
streamlit run streamlit_app.py
```

## Getting Free API Keys

### Groq
1. Go to https://console.groq.com
2. Sign up / log in
3. Navigate to API Keys and create a new key

### Tavily
1. Go to https://tavily.com
2. Sign up for a free account
3. Your API key will be on the dashboard

## API Usage

### Health Check

```bash
curl http://localhost:8000/api/v1/health
```

### Check Text

```bash
curl -X POST http://localhost:8000/api/v1/check/text \
  -H "Content-Type: application/json" \
  -d '{"text": "Drinking hot water kills coronavirus"}'
```

### Check with Input Type

```bash
curl -X POST http://localhost:8000/api/v1/check \
  -H "Content-Type: application/json" \
  -d '{"input_type": "text", "content": "5G towers spread COVID-19"}'
```

### Check Image

```bash
curl -X POST http://localhost:8000/api/v1/check/image \
  -F "file=@screenshot.png"
```

## Running with Docker

```bash
docker-compose up --build
```

The API will be available at http://localhost:8000.

## Deployment

### Railway

1. Push the code to a GitHub repository
2. Connect the repository to Railway
3. Set the environment variables (GROQ_API_KEY, TAVILY_API_KEY)
4. Railway will auto-detect the Dockerfile and deploy

### Render

1. Push the code to a GitHub repository
2. Create a new Web Service on Render
3. Connect the repository
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables in the Render dashboard

## Project Structure

```
misinfo_buster/
  config/settings.py       - Pydantic settings from .env
  core/state.py            - LangGraph AgentState definition
  core/models.py           - API request/response models
  core/exceptions.py       - Custom exception types
  services/llm_service.py  - Groq LLM provider
  services/ocr_service.py  - EasyOCR text extraction
  services/chroma_service.py - ChromaDB client
  rag/embedder.py          - Sentence-transformer embeddings
  rag/retriever.py         - Similar fact-check retrieval
  rag/corpus_loader.py     - CSV to ChromaDB loader
  tools/search_tool.py     - Tavily web search wrapper
  tools/rag_tool.py        - LangChain RAG tool
  agents/ocr_node.py       - OCR pipeline node
  agents/claim_extractor_node.py - Claim extraction node
  agents/fact_checker_node.py    - Per-claim fact-checking node
  agents/verdict_node.py   - Final verdict aggregation node
  agents/router.py         - Conditional routing logic
  agents/graph.py          - LangGraph graph construction
  api/app.py               - FastAPI application factory
  api/router.py            - API endpoints
  api/middleware.py         - Logging and error handling
  api/dependencies.py      - Dependency injection
  data/fact_check_corpus.csv - Seed fact-check data
  streamlit_app.py         - Demo Streamlit UI
  main.py                  - Entry point
```
