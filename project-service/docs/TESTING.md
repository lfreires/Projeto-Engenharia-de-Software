# Testing

```bash
ruff check app tests
mypy app
python -m pytest
```

Test layers:

- Unit tests for catalog lookup rules.
- HTTP tests for project/material contracts and token-protected endpoints.
- Smoke test is `GET /api/v1/projects/health`.
