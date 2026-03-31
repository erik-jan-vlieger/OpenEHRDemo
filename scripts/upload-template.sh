#!/usr/bin/env bash
# Upload sensire_wound_care template naar EHRbase
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

EHRBASE_URL="http://localhost:8080/ehrbase/rest/openehr/v1/definition/template/adl1.4"
EHRBASE_USER="ehrbase-user"
EHRBASE_PASS="SuperSecretPassword"
OPT_DIR="$PROJECT_DIR/opts"

if [ ! -d "$OPT_DIR" ]; then
    echo "❌ Template map niet gevonden: $OPT_DIR"
    exit 1
fi

for TEMPLATE_FILE in "$OPT_DIR"/*.opt; do
    [ -e "$TEMPLATE_FILE" ] || continue
    FILENAME=$(basename "$TEMPLATE_FILE")
    echo "📤 Template uploaden: $FILENAME"

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
done

# Verificatie: toon alle templates
echo ""
echo "📋 Geïnstalleerde templates:"
curl -s -u "$EHRBASE_USER:$EHRBASE_PASS" \
    "http://localhost:8080/ehrbase/rest/openehr/v1/definition/template/adl1.4" | \
    python3 -m json.tool 2>/dev/null || \
    curl -s -u "$EHRBASE_USER:$EHRBASE_PASS" \
    "http://localhost:8080/ehrbase/rest/openehr/v1/definition/template/adl1.4"
