#!/usr/bin/env bash
# Upload sensire_wound_care template naar EHRbase
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

EHRBASE_URL="http://localhost:8080/ehrbase/rest/openehr/v1/definition/template/adl1.4"
EHRBASE_USER="ehrbase-user"
EHRBASE_PASS="SuperSecretPassword"
TEMPLATE_FILE="$PROJECT_DIR/templates/sensire_wound_care.opt"

if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "❌ Template bestand niet gevonden: $TEMPLATE_FILE"
    exit 1
fi

echo "📤 Template uploaden: sensire_wound_care.opt"

HTTP_CODE=$(curl -s -o /tmp/upload_response.txt -w "%{http_code}" \
    -X POST "$EHRBASE_URL" \
    -u "$EHRBASE_USER:$EHRBASE_PASS" \
    -H "Content-Type: application/xml" \
    --data-binary "@$TEMPLATE_FILE")

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ] || [ "$HTTP_CODE" = "204" ]; then
    echo "✅ Template succesvol geüpload (HTTP $HTTP_CODE)"
elif [ "$HTTP_CODE" = "409" ]; then
    echo "ℹ️  Template bestaat al (HTTP 409 — Conflict). Dat is prima."
else
    echo "❌ Upload mislukt (HTTP $HTTP_CODE)"
    cat /tmp/upload_response.txt
    exit 1
fi

# Verificatie: toon alle templates
echo ""
echo "📋 Geïnstalleerde templates:"
curl -s -u "$EHRBASE_USER:$EHRBASE_PASS" \
    "http://localhost:8080/ehrbase/rest/openehr/v1/definition/template/adl1.4" | \
    python3 -m json.tool 2>/dev/null || \
    curl -s -u "$EHRBASE_USER:$EHRBASE_PASS" \
    "http://localhost:8080/ehrbase/rest/openehr/v1/definition/template/adl1.4"
