# PRD

## Responsibility

Validate simple dev/API tokens, represent demo users, internal service clients,
and basic project memberships. No login, password flow, JWT issuer, or refresh
token support exists in this MVP.

## Data

Target database: Azure SQL Database serverless.

Owned tables:

- `users`
- `api_tokens`
- `service_clients`
- `project_memberships`

Current implementation uses `InMemoryIdentityRepository` behind a repository
interface so the SQL-backed implementation can replace it without changing
routers or services.

## Acceptance

- Invalid tokens return `401`.
- Valid user tokens can be scoped to project membership.
- Internal service tokens validate without project membership.
- Health endpoint remains unauthenticated for smoke tests.
