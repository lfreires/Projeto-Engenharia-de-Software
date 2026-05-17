# PRD

## Responsibility

Provide the DocAI chat interface and project material browsing experience.

## Hosting

Target production hosting: Azure Static Web Apps.

## API Contract

The frontend calls only the API Management base URL:

- `GET /api/v1/projects/{id}`
- `GET /api/v1/projects/{id}/materials`
- `POST /api/v1/query/chat`
- `DELETE /api/v1/query/history/{session_id}`
- `POST /api/v1/query/feedback`
