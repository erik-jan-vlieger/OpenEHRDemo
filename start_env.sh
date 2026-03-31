#!/usr/bin/env bash

set -e

echo "=========================================="
echo "    Sensire OpenEHR Demo Environment      "
echo "=========================================="

echo "1. Checking Dependencies..."
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is required but not installed."
    exit 1
fi
if ! command -v archie &> /dev/null; then
    echo "Warning: archie command not found. Assuming templates are pre-compiled or Archie is downloaded."
fi
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is required for OPT 1.4 compiling."
    exit 1
fi

echo ""
echo "2. Starting EHRbase Docker Compose..."
docker compose up -d
echo "Waiting for EHRbase to be ready..."
until curl -s http://localhost:8080/management/health | grep -q "UP"; do
    sleep 5
    echo -n "."
done
echo " EHRbase is ready!"

echo ""
echo "3. Uploading pre-compiled Fully Populated OPT 1.4s (V5)..."
opts_dir="opts"

for template in Diabetic_Foot_Assessment_Sensire.v1 Ulcus_Cruris_Assessment_Sensire.v1 Wound_Assessment_Sensire.v1; do
    if [ -f "${opts_dir}/${template}.opt" ]; then
        echo "Uploading $template to EHRbase..."
        curl -s -f -X PUT "http://localhost:8080/ehrbase/rest/openehr/v1/definition/template/adl1.4/${template}" \
             -u ehrbase-user:SuperSecretPassword \
             -H "accept: application/xml" -H "Content-Type: application/xml" \
             -d @"${opts_dir}/${template}.opt" >/dev/null || \
        curl -s -f -X POST "http://localhost:8080/ehrbase/rest/openehr/v1/definition/template/adl1.4" \
             -u ehrbase-user:SuperSecretPassword \
             -H "accept: application/xml" -H "Content-Type: application/xml" \
             -d @"${opts_dir}/${template}.opt" >/dev/null
        echo "✓ Uploaded $template"
    else
        echo "Error: ${opts_dir}/${template}.opt not found."
    fi
done

echo ""
echo "4. Downloading WebTemplates..."
mkdir -p frontend/sensire-app/webtemplates
for template_id in diabetic_foot_assessment_sensire ulcus_cruris_assessment_sensire wound_assessment_sensire; do
    echo "Fetching WebTemplate for $template_id..."
    curl -s -u ehrbase-user:SuperSecretPassword -X GET "http://localhost:8080/ehrbase/rest/openehr/v1/definition/template/adl1.4/${template_id}" \
         -H "Accept: application/openehr.wt+json" > "frontend/sensire-app/webtemplates/${template_id}_webtemplate.json"
done

echo ""
echo "=========================================="
echo " Environment is Ready!"
echo " Templates uploaded and WebTemplates downloaded."
echo " Start the frontend with: cd frontend/sensire-app && npm install && npm run dev"
echo "=========================================="
