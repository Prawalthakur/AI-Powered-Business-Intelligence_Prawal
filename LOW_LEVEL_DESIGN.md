# Low Level Design (LLD)
## Capstone Sales Analysis

**Version:** 2.0  
**Last Updated:** February 18, 2026

## 1. Scope
This document defines implementation-level design for:
- Streamlit application pages and routing
- FAISS vector store lifecycle
- RAG chat flow
- sales metrics generation
- LLMOps evaluation and visualization components

## 2. Runtime Architecture

```text
UI Layer (Streamlit)
  app/main.py
    ├─ Home
    ├─ Sales Metrics
    ├─ Vector Store
    ├─ Upload & Process
    └─ LLMOps

Service Layer (src/*)
  ├─ database.py (FAISS operations)
  ├─ loaders.py (CSV/PDF ingestion)
  ├─ llm.py (LLM + RAG composition)
  ├─ summary_metrics.py (KPIs)
  └─ metrics_tool.py (aggregated metrics build)

Storage Layer
  ├─ data/raw
  ├─ data/processed
  ├─ vector_db
  └─ backups
```

## 3. Page-Level Design

### 3.1 Home
- Presents onboarding summary and chat interface
- Uses `render_chat_interface()`
- Includes database aggregated metrics tab

### 3.2 Sales Metrics
- Calls `load_sales_metrics()`
- Shows KPI cards and Plotly charts via `render_visualizations()`

### 3.3 Vector Store
- Lists indexes, details, backup options, rename/delete actions
- Reads and updates FAISS metadata/state from `vector_db/`

### 3.4 Upload & Process
- Batch creation of vector stores for all CSV/PDF files
- File-by-file processing from `data/raw/`

### 3.5 LLMOps
- **Model Evaluation:** QA dataset grading via `QAEvalChain`
- **Visualizations:** KPI dashboards and aggregated metric build
- **AI Assistant:** reuses chat interface
- **LangGraph Flow:** graph rendering for logical pipeline view

## 4. Core Function Design

### 4.1 `render_chat_interface()`
Input:
- available indexes from `list_indexes()`
- user question text

Flow:
1. Load/merge all vector stores
2. Optionally add aggregated metric docs
3. Build retriever and RAG chain
4. Invoke chain with question
5. Store answer in `st.session_state.chat_history`

Output:
- formatted answer in UI

### 4.2 `create_rag_chain()` (`src/llm.py`)
Composition:
- retriever context
- metrics provider output
- history provider output
- prompt template
- `ChatOpenAI` model

Design note:
- evaluation mode uses deterministic settings (`temperature=0`) and concise answer template.

### 4.3 Evaluation Grading
- Resolver supports both:
  - `langchain_classic.evaluation.*`
  - `langchain.evaluation.*`
- Grades are normalized through `normalize_grade_label()` before summary aggregation.

## 5. Data Contracts

### 5.1 QA Example
```json
{
  "query": "Which region has the highest total sales?",
  "answer": "West"
}
```

### 5.2 Prediction Row
```json
{
  "result": "West has the highest total sales."
}
```

### 5.3 Evaluation Display Row
```json
{
  "query": "...",
  "answer": "...",
  "prediction": "...",
  "grade": "CORRECT"
}
```

## 6. Error Handling Strategy
- Guard clauses for missing indexes and empty datasets
- User-safe error rendering via `st.error()` / `st.warning()`
- Fallback return values for optional dependencies

## 7. Performance Considerations
- Streamlit caching:
  - `@st.cache_resource` for computed metrics
  - `@st.cache_data` for QA dataset file loading
- Retrieval depth tunable (`k`) depending on latency/quality tradeoff

## 8. Security Considerations
- OpenAI key loaded from environment (.env)
- No secrets hardcoded in source
- See `SECURITY.md` for policy and handling details

## 9. Deployment Notes
- Runtime command:

```powershell
streamlit run app/main.py
```

- Default local endpoint: `http://localhost:8501`

## 10. Future Enhancements
- Replace static LangGraph flow tab with executable graph-backed state machine
- Add evaluation confusion matrix and per-question rationale scoring
- Add response caching for repeated QA evaluation runs
