# Testing

```bash
ruff check app tests
mypy app
python -m pytest
```

Test layers:

- Unit tests for schemas, prompt builder, LLM fallback, and RAG pipeline.
- HTTP tests for chat, history, feedback, auth failures, and error mapping.
- Contract tests for ingestion-service search payload normalization.
