# Deploy

Provision after identity-service and ingestion-service.

Required Terraform variables:

- `container_app_environment_id`
- `api_management_name`
- `container_image`
- `ingestion_service_url`

Runtime configuration:

- `GROQ_API_KEY`
- `INGESTION_SERVICE_URL`
- `IDENTITY_SERVICE_URL`
- `BEARER_TOKEN`
- `INTERNAL_SERVICE_TOKEN`

CI runs lint, typecheck, tests, Docker build, and Terraform validation. CD pushes
to shared ACR, updates the Container App, then smokes `/health`.
