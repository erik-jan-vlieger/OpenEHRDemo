#!/usr/bin/env python3
"""
scripts/export_carepaths_contract.py
------------------------------------
Genereert en distribueert het verrijkte openEHR data-contract voor SensireSpecieleBeslisOndersteuning (Fase 2).
Bevat metadata voor de 164 zorgpaden (regulier & ReAble), de bijbehorende archetypes,
AQL queries, en de UI-specificatie voor de passieve 'openEHR Inspectie Badge' in de WebViewer.

Uitvoer:
- /home/vlieger/OpenEHRDemo/dist/carepaths_openehr_contract.json
- /home/vlieger/SensireSpecieleBeslisOndersteuning/contract/carepaths_openehr_contract.json
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parent.parent
SPECIELE_PATH = Path("/home/vlieger/SensireSpecieleBeslisOndersteuning")
OPTS_DIR = REPO_ROOT / "opts"
DIST_DIR = REPO_ROOT / "dist"
DIST_DIR.mkdir(parents=True, exist_ok=True)

def generate_carepaths_contract():
    print("🚀 Genereren van Speciële Zorgpaden openEHR Data-Contract (Fase 2)...")
    
    opts = list(OPTS_DIR.glob("sensire_*.opt"))
    carepaths_opts = [p for p in opts if not p.name.startswith("sensire_sensii_")]
    
    carepaths_dict = {}
    
    for p in sorted(carepaths_opts):
        stem = p.stem
        is_reable = "_reable" in stem
        
        # Bepaal categorie op basis van prefix
        cat = "Overig"
        if stem.startswith("sensire_w"): cat = "Wondzorg & Dermatologie"
        elif stem.startswith("sensire_s"): cat = "Stoma & Urologie"
        elif stem.startswith("sensire_c"): cat = "Cardiopulmonaal & Chronisch"
        elif stem.startswith("sensire_d"): cat = "Dementie & Psychogeriatrie"
        elif stem.startswith("sensire_n"): cat = "Neurologie & Mobiliteit"
        elif stem.startswith("sensire_m"): cat = "Medicatie & Zelfzorg"
        elif stem.startswith("sensire_p"): cat = "Palliatief & Psychosociaal"
        elif stem.startswith("sensire_t"): cat = "Technisch & Infuustherapie"
        elif stem.startswith("sensire_r"): cat = "Risicosignalering & Urgentie"

        # Archetypes
        archetypes = [
            "openEHR-EHR-EVALUATION.problem_diagnosis.v1",
            "openEHR-EHR-INSTRUCTION.care_plan_request.v0",
            "openEHR-EHR-ACTION.care_plan.v0",
            "openEHR-EHR-ADMIN_ENTRY.care_funding_delivery_nl.v0"
        ]
        if is_reable:
            archetypes.append("openEHR-EHR-ACTION.health_education.v1")
            archetypes.append("openEHR-EHR-OBSERVATION.self_management_regietrede_nl.v0")

        # AQL sample
        t_id = f"openEHR-EHR-COMPOSITION.{stem}.0.0"
        aql = f"SELECT c/name/value, c/context/start_time FROM EHR e CONTAINS COMPOSITION c[{t_id}]"

        carepaths_dict[stem] = {
            "module_id": stem,
            "category": cat,
            "is_reable": is_reable,
            "opt_filename": p.name,
            "template_id": t_id,
            "archetypes": archetypes,
            "aql_sample": aql,
            "size_bytes": p.stat().st_size
        }

    contract_data = {
        "_meta": {
            "schema_version": "2.0.0",
            "fase": "Fase 2: Passieve Schaduw-Adapter (Non-Invasive Info-Badge)",
            "generated_at": datetime.now().isoformat(),
            "producer": "OpenEHRDemo/scripts/export_carepaths_contract.py",
            "description": "openEHR Data-Contract voor SensireSpecieleBeslisOndersteuning WebViewer",
            "total_carepaths": len(carepaths_dict)
        },
        "ui_badge_specification": {
            "name": "openEHR Inspectie Badge",
            "render_mode": "passive_badge",
            "placement": "WebViewer header / module detail",
            "badge_label": "🧬 openEHR Ready",
            "badge_tooltip": "Klik om het gegenereerde openEHR OPT 1.4 XML template en AQL query te bekijken",
            "modal_fields": [
                "template_id",
                "category",
                "is_reable",
                "archetypes",
                "aql_sample",
                "opt_filename"
            ]
        },
        "carepaths": carepaths_dict
    }

    # Bereken SHA256
    json_bytes = json.dumps(contract_data, indent=2, sort_keys=True, ensure_ascii=False).encode("utf-8")
    sha256 = hashlib.sha256(json_bytes).hexdigest()
    contract_data["_meta"]["sha256_checksum"] = sha256

    # Schrijf naar dist/
    out_file = DIST_DIR / "carepaths_openehr_contract.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(contract_data, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Contract geschreven naar {out_file.relative_to(REPO_ROOT)} ({len(carepaths_dict)} zorgpaden)")

    # Exporteer naar SensireSpecieleBeslisOndersteuning
    if SPECIELE_PATH.exists():
        spec_target = SPECIELE_PATH / "contract" / "carepaths_openehr_contract.json"
        spec_target.parent.mkdir(parents=True, exist_ok=True)
        with open(spec_target, "w", encoding="utf-8") as f:
            json.dump(contract_data, f, indent=2, ensure_ascii=False)
        print(f"  ✓ Gekopieerd naar Speciële Beslisondersteuning: {spec_target}")

    return contract_data

if __name__ == "__main__":
    generate_carepaths_contract()
