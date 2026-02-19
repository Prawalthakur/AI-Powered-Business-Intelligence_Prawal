# Secure Environment Setup Guide

This directory contains secure configuration management for your LLM application.

## Overview

The security system consists of:
- **`secrets.py`** - SecretManager class for loading and validating API keys
- **`config.py`** - Configuration module that imports from env module
- **`.env.example`** - Template for environment variables
- **`.env`** - Actual secrets (NOT tracked in git)

## Setup Instructions

### 1. Create Your `.env` File

Copy the template and fill in your actual API keys:

```bash
# From project root
copy env\.env.example .env
```

### 2. Add Your API Keys

Edit the `.env` file in the project root:

```
OPENAI_API_KEY=sk-...your-actual-key...
```

### 3. Secure the .env File

Make sure `.env` is in `.gitignore` (it already is):

```bash
# Verify .env is NOT tracked
git status
# .env should NOT appear in the list
```

### 4. Set File Permissions (Unix/Linux/Mac)

If on Unix-like system, restrict access:

```bash
chmod 600 .env
```

## Usage in Your Code

### Loading Secrets Automatically

Configuration is loaded when importing:

```python
from src.config import OPENAI_API_KEY
# API key is already validated and loaded
```

### Accessing Specific Secrets

Using the SecretManager class:

```python
from env.secrets import SecretManager

# Get required secret
openai_key = SecretManager.get_openai_api_key()

# Get optional secret
hf_key = SecretManager.get_huggingface_api_key()

# Get any secret
custom_key = SecretManager.get_secret("CUSTOM_KEY", required=False)
```

### Validating Configuration

Check if all required secrets are available:

```python
from env import validate_configuration

if validate_configuration():
    print("✓ All configuration valid")
else:
    print("✗ Missing required configuration")
```

### Audit Secrets Status

Check what secrets are available:

```python
from env.secrets import SecretManager

validation = SecretManager.validate_secrets()
print(f"Found: {validation['found']}")
print(f"Missing: {validation['missing']}")
print(f"Optional: {validation['optional']}")
```

## Available Secrets

### Required Secrets
- **OPENAI_API_KEY** - OpenAI API key from https://platform.openai.com/api-keys

### Optional Secrets
- **ANTHROPIC_API_KEY** - Claude API from https://console.anthropic.com/
- **HUGGINGFACE_API_KEY** - HF token from https://huggingface.co/settings/tokens
- **SERPAPI_API_KEY** - Web search from https://serpapi.com/

## Security Best Practices

✅ **DO:**
- Keep `.env` file locally only
- Use strong, unique API keys
- Rotate keys periodically
- Use environment-specific keys (dev/prod)
- Monitor API usage and spending

❌ **DON'T:**
- Commit `.env` to git
- Share API keys via email/chat
- Hardcode secret values in code
- Use the same key for dev and production
- Leave keys in logs or console output

## Troubleshooting

### Missing .env File
```
Error: .env file not found
Fix: Create .env from env/.env.example
```

### Required Secret Missing
```
Error: Required secret 'OPENAI_API_KEY' not found
Fix: Add OPENAI_API_KEY to .env
```

### API Key Not Working
```
Error: Invalid API key
Fix: 
1. Verify key format (should start with appropriate prefix)
2. Check key hasn't been revoked
3. Verify API account has active subscription
```

## Production Deployment

For production environments:

1. **Use Environment Variables** - Don't use .env files
   ```bash
   export OPENAI_API_KEY="your-production-key"
   ```

2. **Use Secrets Management** - Use cloud provider's secrets manager:
   - AWS Secrets Manager
   - Azure Key Vault
   - Google Cloud Secret Manager
   - HashiCorp Vault

3. **Use Service Accounts** - Don't use personal keys

## File Structure

```
env/
├── __init__.py          # Module exports
├── secrets.py           # SecretManager class
├── config.py            # Configuration loader
└── .env.example         # Template (tracked in git)

.env                     # SECRETS (not tracked - create from template)
.gitignore              # Ignores .env file
```

## See Also

- [.env.example](env/.env.example) - Configuration template
- [secrets.py](secrets.py) - SecretManager implementation
- [config.py](config.py) - Configuration module
