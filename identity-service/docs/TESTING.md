# Testing

```bash
ruff check app tests
mypy app
python -m pytest
```

Test layers:

- Unit tests for token validation and membership rules.
- HTTP integration tests with FastAPI/HTTPX.
- Smoke test is `GET /api/v1/identity/health`.
