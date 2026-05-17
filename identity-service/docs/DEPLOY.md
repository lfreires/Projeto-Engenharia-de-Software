# Deploy

Provision this repo first.

## Terraform

```bash
export TF_VAR_sql_admin_password="..."
scripts/terraform-bootstrap.sh
RUN_TERRAFORM_PLAN=true scripts/terraform-bootstrap.sh
```

The Terraform module creates shared infrastructure and the identity SQL
database. Remote state can be configured through:

- `TF_BACKEND_RESOURCE_GROUP`
- `TF_BACKEND_STORAGE_ACCOUNT`
- `TF_BACKEND_CONTAINER`
- `TF_BACKEND_KEY`

## CI/CD

CI runs lint, typecheck, tests, Docker build, and Terraform validation.

CD expects:

- secret `AZURE_CREDENTIALS`
- vars `ACR_NAME`, `ACR_LOGIN_SERVER`, `CONTAINER_APP_NAME`, `RESOURCE_GROUP`, `HEALTH_URL`
