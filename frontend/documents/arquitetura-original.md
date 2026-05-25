# Arquitetura original planejada do DocAI

## Objetivo

O DocAI foi planejado como um sistema RAG baseado em microservicos. O usuario
seleciona um projeto, consulta os materiais indexados e recebe respostas
fundamentadas em documentos recuperados.

## Servicos independentes

- `frontend`: SPA React/Vite para catalogo de projeto, materiais e chat,
  publicada no Azure Static Web Apps.
- `identity-service`: validacao de tokens bearer e memberships de projeto,
  com Azure SQL Database como armazenamento planejado.
- `project-service`: catalogo de projetos, materiais e versoes, com Azure
  Database for PostgreSQL Flexible Server como destino de persistencia.
- `ingestion-service`: recebe documentos, divide o texto em chunks e indexa
  conteudo para recuperacao, usando Azure Blob Storage e Azure AI Search.
- `query-service`: orquestra a consulta RAG, busca trechos pelo
  `ingestion-service`, constroi o prompt e usa Groq via LangChain para gerar
  respostas; historico e feedback seriam persistidos no Azure Cosmos DB.

## Comunicacao e infraestrutura Azure

O frontend acessaria as rotas publicas pelo Azure API Management. Os quatro
backends seriam implantados separadamente no Azure Container Apps, com imagens
no Azure Container Registry. O Azure Key Vault armazenaria segredos. Cada
repositorio teria CI/CD proprio no GitHub Actions, autenticando no Azure por
OIDC com Managed Identity.

## Fluxo de consulta

1. O frontend envia o token bearer e a pergunta pelo API Management.
2. O servico responsavel valida acesso junto ao `identity-service`.
3. O `query-service` solicita ao `ingestion-service` os documentos relevantes.
4. O `ingestion-service` recupera trechos indexados no Azure AI Search.
5. O `query-service` envia o contexto ao Groq e devolve resposta com fontes.

## Observacao sobre a demonstracao

O deploy gratuito atual em Render e Supabase e um fallback operacional para
demonstrar o produto. Ele preserva as rotas da API, mas nao substitui a
arquitetura Azure distribuida originalmente planejada.
