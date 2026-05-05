#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# health-check.sh — Testa conexão backend + frontend e dispara um query RAG
# Uso local:  bash scripts/health-check.sh
# Uso prod:   BACKEND_URL=https://... FRONTEND_URL=https://... bash scripts/health-check.sh
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

BACKEND="${BACKEND_URL:-http://localhost:8000}"
FRONTEND="${FRONTEND_URL:-http://localhost:3000}"
TOKEN="${BEARER_TOKEN:-dev-token}"
PROJECT_ID="${VITE_PROJECT_ID:-ecommerce-api}"
SESSION_ID="health-check-$(date +%s)"

PASS=0
FAIL=0

check() {
  local label="$1"
  local cmd="$2"
  printf "  %-45s" "$label"
  if eval "$cmd" &>/dev/null; then
    echo "✓ OK"
    ((PASS++))
  else
    echo "✗ FAIL"
    ((FAIL++))
  fi
}

echo ""
echo "═══════════════════════════════════════════════════"
echo "  DocAI — Health Check"
echo "  Backend:  $BACKEND"
echo "  Frontend: $FRONTEND"
echo "═══════════════════════════════════════════════════"
echo ""

echo "── Backend ──────────────────────────────────────"
check "GET /api/v1/query/health → 200" \
  "curl -sf $BACKEND/api/v1/query/health | grep -q 'ok'"

check "POST /chat sem token → 401" \
  "[ \$(curl -s -o /dev/null -w '%{http_code}' -X POST $BACKEND/api/v1/query/chat -H 'Content-Type: application/json' -d '{\"project_id\":\"x\",\"session_id\":\"s\",\"message\":\"hi\"}') = '401' ]"

check "GET /history (autenticado) → 200" \
  "curl -sf -H 'Authorization: Bearer $TOKEN' $BACKEND/api/v1/query/history/$SESSION_ID | grep -q 'session_id'"

echo ""
echo "── Frontend ─────────────────────────────────────"
check "GET / → 200 (nginx serving app)" \
  "curl -sf $FRONTEND | grep -qi 'docai\|root\|html'"

echo ""
echo "── RAG Query (requer Azure Search + Groq) ───────"
echo "  (este teste falha se o Azure Search não tiver documentos indexados)"
HTTP_STATUS=$(curl -s -o /tmp/rag_response.json -w "%{http_code}" \
  -X POST "$BACKEND/api/v1/query/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"project_id\":\"$PROJECT_ID\",\"session_id\":\"$SESSION_ID\",\"message\":\"Resuma o projeto\"}")

printf "  %-45s" "POST /chat → 200 com answer"
if [ "$HTTP_STATUS" = "200" ] && grep -q '"answer"' /tmp/rag_response.json; then
  echo "✓ OK"
  echo ""
  echo "  Resposta:"
  python3 -c "import json,sys; d=json.load(open('/tmp/rag_response.json')); print('  model:', d.get('model_used','?')); print('  answer:', d.get('answer','')[:120],'...')" 2>/dev/null || true
  ((PASS++))
elif [ "$HTTP_STATUS" = "404" ]; then
  echo "⚠ 404 (sem documentos indexados para project_id='$PROJECT_ID' — esperado em ambiente fresh)"
else
  echo "✗ FAIL (HTTP $HTTP_STATUS)"
  cat /tmp/rag_response.json 2>/dev/null || true
  ((FAIL++))
fi

echo ""
echo "═══════════════════════════════════════════════════"
echo "  Resultado: $PASS passaram, $FAIL falharam"
echo "═══════════════════════════════════════════════════"
echo ""

[ "$FAIL" -eq 0 ] && exit 0 || exit 1
