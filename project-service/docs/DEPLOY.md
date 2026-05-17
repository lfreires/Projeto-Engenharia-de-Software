# Deploy

Provision after identity-service outputs are available.

Required Terraform variables:

- `container_app_environment_id`
- `api_management_name`
- `postgres_admin_password`
- `container_image`

CI runs lint, typecheck, tests, Docker build, and Terraform validation. CD pushes
the image to the shared ACR, updates the Container App, then smokes `/health`.
