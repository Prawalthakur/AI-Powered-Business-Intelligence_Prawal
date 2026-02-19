# Production Support Guide
## Capstone Sales Analysis

**Version:** 2.0  
**Last Updated:** February 18, 2026

## 1. Support Scope
This guide covers daily operations and incident support for:
- Streamlit application (`app/main.py`)
- FAISS vector store operations (`vector_db/`)
- sales metrics generation and dashboards
- LLMOps evaluation and assistant workflows

## 2. Quick Operations Commands

### Start Application
```powershell
streamlit run app/main.py
```

### Install Dependencies
```powershell
pip install -r requirements.txt
```

### Validate Config
```powershell
python -c "from src.config import validate_configuration; validate_configuration()"
```

### Run QA Evaluation Script
```powershell
.\.venv\Scripts\python.exe .\scripts\qa_eval.py
```

## 3. Health Checklist (Daily)
1. App accessible at `http://localhost:8501`
2. `OPENAI_API_KEY` available and valid
3. At least one FAISS index present in `vector_db/`
4. `data/raw/sales_data.csv` exists for metrics
5. No startup exception in terminal logs

## 4. Incident Triage

### P1 (Critical)
- App unavailable
- OpenAI auth failure across all features
- Data corruption in vector store

### P2 (High)
- Chat answers failing intermittently
- Upload/processing broken for common files
- LLMOps evaluation non-functional

### P3/P4 (Medium/Low)
- UI formatting issues
- non-blocking chart/rendering defects

## 5. Runbooks

### 5.1 App Not Loading
```powershell
Get-Process streamlit
netstat -ano | findstr 8501
```
If process missing, restart:
```powershell
streamlit run app/main.py
```

### 5.2 OpenAI Key / API Errors
Checks:
- `.env` contains valid `OPENAI_API_KEY`
- network egress is available
- no API quota/rate limit exhaustion

Recovery:
1. rotate/replace key
2. restart app process
3. validate with a small assistant query

### 5.3 No Vector Stores Found
Symptoms:
- Home chat says no vector stores available

Fix:
1. Go to `Upload & Process`
2. Run `Create All Vector Stores`
3. Verify indexes in `Vector Store` page

### 5.4 LLMOps Evaluation Shows Unexpected Grades
Checklist:
1. Verify QA dataset quality (clear short answers)
2. Confirm `QAEvalChain` resolver works for installed LangChain flavor
3. Re-run evaluation with deterministic settings (already enabled)

## 6. Backup and Recovery

### Backup
- Use `Vector Store` page -> Backup tab
- Backup path defaults to `backups/`

### Restore (Manual)
1. Stop app
2. Replace `vector_db/` with backup snapshot
3. Restart app and verify index list

## 7. Change Management
- Validate after each release:
  - navigation routes
  - chat response generation
  - metrics rendering
  - LLMOps evaluation output
- Keep `README.md`, `APP_DOCUMENTATION.md`, and this guide in sync

## 8. Escalation Data to Capture
Before escalation, collect:
1. timestamp and environment
2. failing page and user action
3. full traceback/error text
4. sample input file(s) if relevant
5. whether issue reproduces after restart

## 9. Known Operational Notes
- Current UI includes LLMOps tab with a LangGraph flow visual tab.
- Data Analysis page was removed; do not route incidents to that page.
- Evaluation grade summary uses normalized labels.

## 10. Reference Files
- `app/main.py`
- `src/database.py`
- `src/llm.py`
- `src/summary_metrics.py`
- `SECURITY.md`
