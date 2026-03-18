#!/usr/bin/env bash
# Maak een test-EHR aan voor de fictieve cliënt
set -euo pipefail

EHRBASE_URL="http://localhost:8080/ehrbase/rest/openehr/v1/ehr"
EHRBASE_USER="ehrbase-user"
EHRBASE_PASS="SuperSecretPassword"

echo "🏥 Test-EHR aanmaken voor fictieve cliënt..."

RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST "$EHRBASE_URL" \
    -u "$EHRBASE_USER:$EHRBASE_PASS" \
    -H "Content-Type: application/json" \
    -d '{
        "_type": "EHR_STATUS",
        "archetype_node_id": "openEHR-EHR-EHR_STATUS.generic.v1",
        "name": {"value": "EHR Status"},
        "subject": {"_type": "PARTY_SELF"},
        "is_queryable": true,
        "is_modifiable": true
    }')

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ] || [ "$HTTP_CODE" = "204" ]; then
    EHR_ID=$(echo "$BODY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('ehr_id',{}).get('value','onbekend'))" 2>/dev/null || echo "zie response")
    echo "✅ EHR aangemaakt!"
    echo "   EHR-ID: $EHR_ID"
    echo ""
    echo "   Bewaar dit ID — je hebt het nodig voor de demo."
    echo "   $EHR_ID" > /tmp/ehrbase_demo_ehr_id.txt
    echo "   (ook opgeslagen in /tmp/ehrbase_demo_ehr_id.txt)"
else
    echo "⚠️  EHR aanmaken gaf HTTP $HTTP_CODE"
    echo "   (Als er al een EHR bestaat is dit geen probleem)"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
fi
