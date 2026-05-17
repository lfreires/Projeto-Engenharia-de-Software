# Testing

```bash
ruff check app tests
mypy app
python -m pytest
```

Test layers:

- Unit tests for chunking and search ranking.
- HTTP tests for document ingestion, document status, project filtering, and search.
- Contract tests are consumed by query-service.
