# Capstone Sales Analysis

Capstone Sales Analysis is a Streamlit-based sales intelligence assistant that combines:
- FAISS vector retrieval
- OpenAI-powered RAG responses
- KPI dashboards and visual analytics
- LLMOps evaluation workflows

## Features
- Upload/process CSV and PDF sources
- Build and manage FAISS vector stores
- Chat with your data using retrieved context + metrics
- Sales KPI dashboards (overall, regional, product, customer)
- LLMOps with model evaluation and LangGraph flow visualization

## Current Navigation
1. Home
2. Sales Metrics
3. Vector Store
4. Upload & Process
5. LLMOps

## Quick Start

### 1) Install dependencies
```powershell
pip install -r requirements.txt
```

### 2) Configure environment
Create `.env` in project root with:

```env
OPENAI_API_KEY=your_openai_key
```

### 3) Validate configuration
```powershell
python -c "from src.config import validate_configuration; validate_configuration()"
```

### 4) Run app
```powershell
streamlit run app/main.py
```

## Data Locations
- Raw CSV: `data/raw/`
- Raw PDF: `data/raw/PDF_Folder/`
- Processed artifacts: `data/processed/`
- Vector DB: `vector_db/`
- Backups: `backups/`

## Evaluation

### UI Evaluation
Use `LLMOps -> Model Evaluation` tab.

### CLI Evaluation
```powershell
.\.venv\Scripts\python.exe .\scripts\qa_eval.py
```

## Core Files
- `app/main.py` - Streamlit entry and routing
- `src/database.py` - FAISS index operations
- `src/loaders.py` - CSV/PDF loading and chunking
- `src/llm.py` - LLM setup and RAG chain creation
- `src/summary_metrics.py` - KPI generation and prompt metrics context

## Notes
- `QAEvalChain` compatibility is handled across legacy/new LangChain module paths.
- Evaluation now uses normalized grade labels for cleaner summary counts.

## Security
Read `SECURITY.md` for key handling and secure operation guidance.
