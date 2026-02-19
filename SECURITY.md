# Security Policy and Operations Guide

## Scope
This document defines security controls for Capstone Sales Analysis, including secret handling, dependency hygiene, runtime safety, and incident response.

## 1) Secret Management

### Required Secret
- `OPENAI_API_KEY`

### Rules
- Store secrets only in `.env` (local) or platform secret manager (production).
- Never commit `.env` or real keys to source control.
- Never print or log secret values.
- Rotate keys periodically and immediately after suspected exposure.

### Validation Command
```powershell
python -c "from src.config import validate_configuration; validate_configuration()"
```

## 2) Data Protection

### Data at Rest
- Raw data: `data/raw/`
- Processed data: `data/processed/`
- Vector indexes: `vector_db/`
- Backups: `backups/`

### Handling Standards
- Do not include customer-identifying data in test fixtures unless required.
- Prefer anonymized/sampled datasets for debugging.
- Restrict filesystem permissions for project and backup folders.

## 3) Application Security Controls

### Prompt and Output Safety
- Chat prompts should avoid exposing secrets or internal diagnostics.
- Error messages displayed in UI should be informative but sanitized.

### Dependency and Supply Chain
- Keep dependencies in `requirements.txt` reviewed and minimal.
- Pin minimum versions and periodically patch known vulnerable libraries.
- Review transitive dependencies with security scans (`pip-audit` recommended).

## 4) Access Control

### Local/Shared Environments
- Limit who can access the machine/user profile running Streamlit.
- Do not share `.env` files in chat, email, or ticket comments.

### Production Environments
- Use managed secrets (AWS Secrets Manager / Azure Key Vault / GCP Secret Manager).
- Apply least privilege for runtime identities.

## 5) Logging and Monitoring

### Log Requirements
- Log operational state, not credentials.
- Capture failures for startup, vector loading, API calls, and evaluation jobs.

### Suggested Alerts
- App not reachable on configured port
- Repeated OpenAI authentication failures
- Missing/invalid configuration at startup
- Unexpected spikes in API usage or cost

## 6) Incident Response

### If a Secret Is Exposed
1. Revoke and rotate the key immediately.
2. Replace key in secret store / `.env`.
3. Restart the app.
4. Review logs for misuse window.
5. Document incident and prevention action.

### If Dependency Risk Is Detected
1. Identify impacted package and version.
2. Upgrade to patched version.
3. Run smoke tests (`streamlit run app/main.py` and key app paths).
4. Update `requirements.txt` and release notes.

## 7) Secure Development Checklist
- [ ] No hardcoded secrets in code or docs
- [ ] `.env` excluded by `.gitignore`
- [ ] Configuration validation passes
- [ ] Dependencies reviewed and updated
- [ ] Error output does not reveal internals or secrets
- [ ] Backups are present and access-controlled

## 8) References
- `env/README.md`
- `src/config.py`
- `PRODUCTION_SUPPORT_GUIDE.md`
- `README.md`
