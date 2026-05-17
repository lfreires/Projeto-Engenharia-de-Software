# PRD

## Responsibility

Own the catalog of projects and materials shown by the frontend. Other services
refer to this domain only by stable IDs such as `project_id` and `material_id`.

## Data

Target database: Azure Database for PostgreSQL Flexible Server.

Owned tables:

- `projects`
- `materials`
- `material_versions`

No foreign keys cross service database boundaries.
