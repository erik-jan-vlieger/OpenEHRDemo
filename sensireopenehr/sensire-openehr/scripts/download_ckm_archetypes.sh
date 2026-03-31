#!/bin/bash
# =============================================================================
# download_ckm_archetypes.sh
# Download benodigde internationale archetypes uit de openEHR CKM GitHub-repo
# Paden geverifieerd tegen CKM-mirror master branch (maart 2026)
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
INTL_DIR="$PROJECT_DIR/archetypes/international"

CKM_BASE="https://raw.githubusercontent.com/openEHR/CKM-mirror/master/local/archetypes"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

mkdir -p "$INTL_DIR"

echo "=============================================="
echo "  Sensire OpenEHR — Download CKM Archetypes"
echo "=============================================="
echo ""
echo "Doel: $INTL_DIR"
echo ""

DOWNLOADED=0
SKIPPED=0
FAILED=0

download() {
    local path="$1"
    local description="$2"
    local filename
    filename=$(basename "$path")
    local dest="$INTL_DIR/$filename"

    if [[ -f "$dest" ]]; then
        echo -e "  ${YELLOW}⊘${NC} $filename — al aanwezig"
        SKIPPED=$((SKIPPED + 1))
        return
    fi

    local url="$CKM_BASE/$path"
    if curl -sfL -o "$dest" "$url"; then
        echo -e "  ${GREEN}✓${NC} $filename — ${description}"
        DOWNLOADED=$((DOWNLOADED + 1))
    else
        echo -e "  ${RED}✗${NC} $filename — NIET GEVONDEN"
        echo "    URL: $url"
        FAILED=$((FAILED + 1))
    fi
}

echo "--- COMPOSITION ---"
download "composition/openEHR-EHR-COMPOSITION.encounter.v1.adl" \
         "Contactmoment (container)"

echo ""
echo "--- EVALUATION ---"
download "entry/evaluation/openEHR-EHR-EVALUATION.problem_diagnosis.v1.adl" \
         "Probleemdiagnose"
download "entry/evaluation/openEHR-EHR-EVALUATION.health_risk.v1.adl" \
         "Gezondheidsrisico"
download "entry/evaluation/openEHR-EHR-EVALUATION.clinical_synopsis.v1.adl" \
         "Klinische samenvatting"
download "entry/evaluation/openEHR-EHR-EVALUATION.contraindication.v1.adl" \
         "Contra-indicatie"

echo ""
echo "--- OBSERVATION ---"
download "entry/observation/openEHR-EHR-OBSERVATION.exam.v1.adl" \
         "Lichamelijk onderzoek"
download "entry/observation/openEHR-EHR-OBSERVATION.body_temperature.v2.adl" \
         "Lichaamstemperatuur"
download "entry/observation/openEHR-EHR-OBSERVATION.blood_pressure.v2.adl" \
         "Bloeddruk"
download "entry/observation/openEHR-EHR-OBSERVATION.laboratory_test_result.v1.adl" \
         "Laboratoriumuitslag"
download "entry/observation/openEHR-EHR-OBSERVATION.story.v1.adl" \
         "Anamnese"
download "entry/observation/openEHR-EHR-OBSERVATION.diabetic_wound_wagner.v0.adl" \
         "Wagner-classificatie DM voet"

echo ""
echo "--- ACTION ---"
download "entry/action/openEHR-EHR-ACTION.procedure.v1.adl" \
         "Procedure"
download "entry/action/openEHR-EHR-ACTION.medication.v1.adl" \
         "Medicatietoediening"
download "entry/action/openEHR-EHR-ACTION.health_education.v1.adl" \
         "Gezondheidsvoorlichting"
download "entry/action/openEHR-EHR-ACTION.care_plan.v0.adl" \
         "Zorgplan (actie)"

echo ""
echo "--- INSTRUCTION ---"
download "entry/instruction/openEHR-EHR-INSTRUCTION.medication_order.v3.adl" \
         "Medicatieorder (v3)"
download "entry/instruction/openEHR-EHR-INSTRUCTION.service_request.v1.adl" \
         "Verwijzing"
download "entry/instruction/openEHR-EHR-INSTRUCTION.care_plan_request.v0.adl" \
         "Zorgplanverzoek"
download "entry/instruction/openEHR-EHR-INSTRUCTION.therapeutic_item_order.v1.adl" \
         "Therapeutisch item order"

echo ""
echo "--- CLUSTER ---"
download "cluster/openEHR-EHR-CLUSTER.anatomical_location.v1.adl" \
         "Anatomische locatie"
download "cluster/openEHR-EHR-CLUSTER.media_file.v1.adl" \
         "Mediabestand (foto)"
download "cluster/openEHR-EHR-CLUSTER.device.v1.adl" \
         "Hulpmiddel"
download "cluster/openEHR-EHR-CLUSTER.symptom_sign.v2.adl" \
         "Symptoom/teken"
download "cluster/openEHR-EHR-CLUSTER.exam.v2.adl" \
         "Onderzoeksbevinding (generiek, v2)"
download "cluster/openEHR-EHR-CLUSTER.exam_wound.v0.adl" \
         "Wondonderzoek"
download "cluster/openEHR-EHR-CLUSTER.physical_dimensions.v1.adl" \
         "Fysieke afmetingen"

echo ""
echo "=============================================="
echo "  Resultaat"
echo "=============================================="
echo -e "  ${GREEN}Gedownload:${NC}   $DOWNLOADED"
echo -e "  ${YELLOW}Overgeslagen:${NC} $SKIPPED"
echo -e "  ${RED}Mislukt:${NC}      $FAILED"
echo ""

echo "=============================================="
echo "  Handmatig te downloaden"
echo "=============================================="
echo ""
echo "De volgende archetypes staan NIET in de CKM GitHub-mirror."
echo "Download ze handmatig en plaats ze in:"
echo "  $INTL_DIR/"
echo ""
echo "  1. OBSERVATION.ankle_brachial_pressure_index.v0"
echo "     → Noorse CKM: https://arketyper.no/ckm/"
echo "     → Zoek: 'ankle brachial' of 'ABPI'"
echo "     → Download als ADL 1.4"
echo ""
echo "Na het plaatsen, valideer met:  ./gradlew validateArchetypes"
echo ""
