# Environment-Based OpenAI Key Tracking

This document provides comprehensive guidance on configuring and using RAGFlow's environment-based OpenAI API key tracking system.

## Overview

RAGFlow's environment-based OpenAI key tracking allows you to automatically use different OpenAI API keys based on the deployment environment. This enables:

- **Separated API Quotas**: Each environment can have its own OpenAI usage limits
- **Environment Isolation**: Development work doesn't impact production API usage  
- **Cost Management**: Track and control OpenAI costs per environment
- **Team Organization**: Different teams can use different environments with appropriate keys

## Supported Environments

The system supports four environments:

| Environment | Description | Typical Use Case |
|-------------|-------------|------------------|
| `dev` | Development | Local development and testing |
| `staging` | Staging | Pre-production testing and validation |
| `prod` | Production | Live production deployment |
| `kafi` | Kafi | Custom kafi environment |

## Configuration

### 1. Server Configuration

#### Method 1: YAML Configuration
Edit `docker/service_conf.yaml` to add environment-specific keys:

```yaml
environment_openai_keys:
  dev: 'sk-proj-dev-key-here'
  staging: 'sk-proj-staging-key-here'
  prod: 'sk-proj-prod-key-here'
  kafi: 'sk-proj-kafi-key-here'
```

#### Method 2: Environment Variables
Set environment variables that will be automatically loaded:

```bash
# Development environment
export OPENAI_API_KEY_DEV='sk-proj-dev-key-here'

# Staging environment  
export OPENAI_API_KEY_STAGING='sk-proj-staging-key-here'

# Production environment
export OPENAI_API_KEY_PROD='sk-proj-prod-key-here'

# Kafi environment
export OPENAI_API_KEY_KAFI='sk-proj-kafi-key-here'
```

#### Method 3: Combined Approach
Use environment variables in YAML for flexibility:

```yaml
environment_openai_keys:
  dev: '${OPENAI_API_KEY_DEV:-sk-dev-fallback-key}'
  staging: '${OPENAI_API_KEY_STAGING:-sk-staging-fallback-key}'
  prod: '${OPENAI_API_KEY_PROD:-sk-prod-fallback-key}'
  kafi: '${OPENAI_API_KEY_KAFI:-sk-kafi-fallback-key}'
```

### 2. Server Restart
After configuration changes, restart the RAGFlow server:

```bash
# If using Docker Compose
cd docker
docker compose restart ragflow

# If running from source
bash docker/launch_backend_service.sh
```

## SDK Usage

### Python SDK

#### Basic Usage
```python
from ragflow_sdk import RAGFlow

# Initialize client
ragflow = RAGFlow("your-api-key", "http://localhost:9380")

# Set environment for all subsequent requests
ragflow.set_environment("dev")

# All OpenAI model requests will now use the dev key
dataset = ragflow.create_dataset(
    name="my-dev-dataset",
    embedding_model="text-embedding-3-small@OpenAI"
)
```

#### Environment Switching
```python
# Start with development
ragflow.set_environment("dev")
dev_dataset = ragflow.create_dataset("dev-data", embedding_model="text-embedding-ada-002@OpenAI")

# Switch to staging for testing
ragflow.set_environment("staging")
staging_chat = ragflow.create_chat("staging-chat")

# Switch to production for deployment
ragflow.set_environment("prod")
prod_results = ragflow.list_datasets()

# Disable environment tracking (use normal tenant keys)
ragflow.set_environment(None)
```

#### Error Handling
```python
try:
    ragflow.set_environment("invalid-env")
except ValueError as e:
    print(f"Invalid environment: {e}")
    # Error: Environment must be one of: 'dev', 'staging', 'prod', 'kafi', or None

# Check current environment
print(f"Current environment: {ragflow.environment}")
```

### HTTP API Usage

For direct HTTP API calls, include the `X-Environment` header:

```bash
# Using curl
curl -X POST "http://localhost:9380/api/v1/datasets" \
  -H "Authorization: Bearer your-api-key" \
  -H "X-Environment: dev" \
  -H "Content-Type: application/json" \
  -d '{"name": "test-dataset", "embedding_model": "text-embedding-3-small@OpenAI"}'
```

```python
# Using requests
import requests

headers = {
    "Authorization": "Bearer your-api-key",
    "X-Environment": "staging",
    "Content-Type": "application/json"
}

response = requests.post(
    "http://localhost:9380/api/v1/datasets",
    headers=headers,
    json={"name": "staging-dataset", "embedding_model": "text-embedding-3-small@OpenAI"}
)
```

## Implementation Details

### Request Flow

1. **Client Request**: SDK/HTTP client includes `X-Environment` header
2. **Header Extraction**: `api/utils/api_utils.py::get_request_environment()` extracts environment
3. **Model Detection**: `api/utils/api_utils.py::is_openai_request()` identifies OpenAI models
4. **Key Selection**: `api/db/services/llm_service.py::get_api_key()` returns environment-specific key
5. **Model Usage**: OpenAI models use environment key, others use normal tenant lookup

### Key Components

```
📁 docker/
├── service_conf.yaml.template     # Environment key configuration

📁 api/
├── settings.py                    # ENVIRONMENT_OPENAI_KEYS global variable
├── utils/
│   └── api_utils.py              # Environment detection functions
└── db/services/
    └── llm_service.py            # Environment-aware key selection

📁 sdk/python/
├── ragflow_sdk/
│   └── ragflow.py                # SDK environment support
└── environment_example.py        # Usage examples
```

### Model Filtering

The system only affects OpenAI models. Models are identified by:
- Factory identifier: `llm_factory == 'OpenAI'`
- Model naming: `model_name@OpenAI` format

Non-OpenAI models (Anthropic, local models, etc.) continue using normal tenant key lookup.

## Advanced Configuration

### Per-Environment Model Configuration

You can configure different default models per environment:

```python
# Development: Use cheaper models
ragflow.set_environment("dev")
dataset = ragflow.create_dataset(
    name="dev-dataset",
    embedding_model="text-embedding-ada-002@OpenAI"  # Cheaper model
)

# Production: Use latest models  
ragflow.set_environment("prod")
dataset = ragflow.create_dataset(
    name="prod-dataset", 
    embedding_model="text-embedding-3-large@OpenAI"  # Better model
)
```

### Environment-Specific Rate Limiting

Configure different rate limits per OpenAI key:

1. **Dev Environment**: High rate limit for fast development
2. **Staging Environment**: Medium rate limit for testing
3. **Production Environment**: Conservative rate limit for stability
4. **Kafi Environment**: Custom rate limit as needed

### Monitoring and Logging

The system logs environment key usage:

```python
# Backend logs will show:
# INFO: Using environment-specific OpenAI key for environment: dev
# INFO: Using environment-specific OpenAI key for environment: prod
```

Monitor these logs to track environment usage patterns.

## Troubleshooting

### Common Issues

#### 1. Environment Key Not Used
**Symptom**: Normal tenant key used instead of environment key

**Possible Causes**:
- Environment not set in client: `ragflow.set_environment("dev")`
- Model not identified as OpenAI: Ensure model uses `@OpenAI` suffix
- Environment key not configured in `service_conf.yaml`

**Solution**:
```python
# Verify environment is set
print(f"Current environment: {ragflow.environment}")

# Check model format
embedding_model = "text-embedding-3-small@OpenAI"  # Correct format
# NOT: embedding_model = "text-embedding-3-small"  # Missing @OpenAI
```

#### 2. Invalid Environment Error
**Symptom**: `ValueError: Environment must be one of: 'dev', 'staging', 'prod', 'kafi', or None`

**Solution**: Use only supported environments:
```python
# Correct
ragflow.set_environment("dev")
ragflow.set_environment("staging") 
ragflow.set_environment("prod")
ragflow.set_environment("kafi")
ragflow.set_environment(None)

# Incorrect
ragflow.set_environment("development")  # Not supported
ragflow.set_environment("production")   # Not supported
```

#### 3. Environment Key Not Found
**Symptom**: API calls fail with authentication errors

**Solution**: Verify environment key configuration:
```bash
# Check environment variable
echo $OPENAI_API_KEY_DEV

# Or check service_conf.yaml
grep -A 10 "environment_openai_keys:" docker/service_conf.yaml
```

### Debugging

Enable debug logging to trace environment key selection:

```python
import logging
logging.basicConfig(level=logging.INFO)

# Backend will log environment key usage
ragflow.set_environment("dev")
dataset = ragflow.create_dataset("debug-test", embedding_model="text-embedding-3-small@OpenAI")
```

### Testing Configuration

Test your environment configuration:

```python
def test_environment_config():
    ragflow = RAGFlow("your-api-key", "http://localhost:9380")
    
    environments = ["dev", "staging", "prod", "kafi"]
    
    for env in environments:
        print(f"Testing {env} environment...")
        ragflow.set_environment(env)
        
        try:
            # Simple API call to test key
            datasets = ragflow.list_datasets(page_size=1)
            print(f"  ✅ {env} environment working")
        except Exception as e:
            print(f"  ❌ {env} environment failed: {e}")

test_environment_config()
```

## Security Considerations

### Key Management
- **Rotation**: Rotate environment keys regularly
- **Access Control**: Limit access to production keys
- **Monitoring**: Monitor API usage per environment

### Environment Variables
- Use secure environment variable management
- Avoid committing keys to version control
- Consider using secret management systems

### Network Security
- Use HTTPS for all API communications
- Implement proper firewall rules
- Monitor for unusual API usage patterns

## Migration Guide

### Migrating Existing Deployments

1. **Add Configuration**: Add environment keys to existing `service_conf.yaml`
2. **Update SDK**: Update to latest RAGFlow SDK version
3. **Test Environment**: Test with non-production environment first
4. **Gradual Rollout**: Migrate environments one at a time

### Backward Compatibility

The feature is fully backward compatible:
- Existing code works without modification
- No environment header = normal tenant key lookup
- Only affects OpenAI models

## Examples

Complete examples are available in `sdk/python/environment_example.py`:

- Basic environment usage
- Environment switching
- Configuration setup
- Error handling
- Integration patterns

Run the examples:
```bash
cd sdk/python
python environment_example.py
```

## Support

For issues or questions:
1. Check this documentation
2. Review `environment_example.py` 
3. Check server logs for environment key usage
4. Verify configuration in `service_conf.yaml`
5. Test with simple API calls first