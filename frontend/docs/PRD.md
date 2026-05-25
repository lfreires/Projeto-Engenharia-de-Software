# PRD

## Responsibility

Provide the DocAI chat interface and project material browsing experience.

## API Contract

The browser calls the consolidated backend configured by `VITE_API_BASE_URL`:

- `GET /api/v1/projects/{id}`
- `GET /api/v1/projects/{id}/materials`
- `POST /api/v1/query/chat`
- `DELETE /api/v1/query/history/{session_id}`
- `POST /api/v1/query/feedback`
