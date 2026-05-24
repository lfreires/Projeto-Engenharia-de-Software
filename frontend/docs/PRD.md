# PRD

## Responsibility

Provide the DocAI chat interface and project material browsing experience.

## API Contract

The browser uses same-origin endpoints exposed by the consolidated backend:

- `GET /api/v1/projects/{id}`
- `GET /api/v1/projects/{id}/materials`
- `POST /api/v1/query/chat`
- `DELETE /api/v1/query/history/{session_id}`
- `POST /api/v1/query/feedback`
