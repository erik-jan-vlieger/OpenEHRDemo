#!/usr/bin/env bash
# Test AQL query tegen EHRbase — toon alle opgeslagen composities
set -euo pipefail

EHRBASE_URL="http://localhost:8080/ehrbase/rest/openehr/v1/query/aql"
EHRBASE_USER="ehrbase-user"
EHRBASE_PASS="SuperSecretPassword"

echo "🔍 AQL Query: alle composities opvragen..."
echo ""

RESPONSE=$(curl -s \
    -u "$EHRBASE_USER:$EHRBASE_PASS" \
    -H "Content-Type: application/json" \
    "$EHRBASE_URL" \
    --data-binary '{
        "q": "SELECT c/uid/value as compositie_id, c/name/value as naam, c/context/start_time/value as datum FROM EHR e CONTAINS COMPOSITION c ORDER BY c/context/start_time/value DESC LIMIT 20"
    }')

echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"

echo ""
echo "───────────────────────────────────────"

# Aantal composities tellen
COUNT=$(echo "$RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    rows = data.get('rows', [])
    print(f'{len(rows)} compositie(s) gevonden')
except:
    print('Kan resultaten niet tellen')
" 2>/dev/null || echo "")

echo "$COUNT"
