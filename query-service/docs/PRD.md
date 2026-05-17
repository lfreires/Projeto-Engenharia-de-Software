# PRD

## Responsibility

Run the chat workflow: validate token, load history, call ingestion-service
search, build prompt, call Groq, persist history, accept feedback.

## Data

Target database: Azure Cosmos DB NoSQL.

Owned collections:

- `sessions`
- `messages`
- `feedback`

The current implementation keeps session and feedback stores in memory behind
service classes.

## Important Boundary

Query-service must not import Azure AI Search, embedder, or retriever code.
Search is only:

`POST /api/v1/ingestion/search`
