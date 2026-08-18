#!/usr/bin/env python3
"""
scripts/export_sensii_contract.py
---------------------------------
Exporteert het gevalideerde openEHR-contract voor Sensii.
Koppelt de 58 surveys, de 4 fasen/hoofdstukken, en de Omaha-systematiek aan de 5 openEHR templates
en 7 custom archetypes.

Uitvoer:
- /home/vlieger/OpenEHRDemo/dist/sensii_openehr_contract.json
- /home/vlieger/Sensii/contract/sensii_openehr_contract.json (indien aanwezig)
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parent.parent
SENSII_PATH = Path("/home/vlieger/Sensii")
DIST_DIR = REPO_ROOT / "dist"
DIST_DIR.mkdir(parents=True, exist_ok=True)

def generate_sensii_contract():
    print("🚀 Genereren van Sensii openEHR Data-Contract...")
    
    # 1. Lees bronbestanden van Sensii
    sections_file = SENSII_PATH / "contract" / "sections_sensii.json"
    omaha_file = SENSII_PATH / "contract" / "omaha_v1.json"
    
    if not sections_file.exists():
        print(f"⚠ Waarschuwing: {sections_file} niet gevonden. Gebruik fallback definities.")
        sections_data = {}
    else:
        with open(sections_file, "r", encoding="utf-8") as f:
            sections_data = json.load(f)
            
    if not omaha_file.exists():
        print(f"⚠ Waarschuwing: {omaha_file} niet gevonden.")
        omaha_data = {}
    else:
        with open(omaha_file, "r", encoding="utf-8") as f:
            omaha_data = json.load(f)

    # 2. Definieer de 5 openEHR Templates
    templates = {
        "sensire_sensii_h1_intake_triage_vag.v1": {
            "template_id": "sensire_sensii_h1_intake_triage_vag.v1",
            "name_nl": "Sensii Hoofdstuk 1: Wie deze cliënt is",
            "description": "Intake, triage, verpleegkundig adviesgesprek (VAG), levensverhaal en start eigen regie.",
            "hoofdstuk": 1,
            "opt_file": "opts/sensire_sensii_h1_intake_triage_vag.v1.opt",
            "rm_type": "COMPOSITION",
            "archetypes": [
                "openEHR-EHR-EVALUATION.triage_nursing_nl.v0",
                "openEHR-EHR-EVALUATION.nursing_vag_nl.v0",
                "openEHR-EHR-OBSERVATION.self_management_regietrede_nl.v0",
                "openEHR-EHR-OBSERVATION.story.v1",
                "openEHR-EHR-EVALUATION.goal.v1",
                "openEHR-EHR-EVALUATION.clinical_synopsis.v1"
            ]
        },
        "sensire_sensii_h2_anamnese_diagnostiek.v1": {
            "template_id": "sensire_sensii_h2_anamnese_diagnostiek.v1",
            "name_nl": "Sensii Hoofdstuk 2: Wat er speelt",
            "description": "Systematische anamnese volgens de 11 gezondheidspatronen van Gordon, GFI kwetsbaarheid en Omaha probleemclassificatie.",
            "hoofdstuk": 2,
            "opt_file": "opts/sensire_sensii_h2_anamnese_diagnostiek.v1.opt",
            "rm_type": "COMPOSITION",
            "archetypes": [
                "openEHR-EHR-OBSERVATION.nursing_gordon_patterns_nl.v0",
                "openEHR-EHR-OBSERVATION.groningen_frailty_indicator_nl.v0",
                "openEHR-EHR-OBSERVATION.self_management_regietrede_nl.v0",
                "openEHR-EHR-EVALUATION.omaha_assessment_nl.v0",
                "openEHR-EHR-EVALUATION.clinical_synopsis.v1"
            ]
        },
        "sensire_sensii_h3_zorgplan_inzet.v1": {
            "template_id": "sensire_sensii_h3_zorgplan_inzet.v1",
            "name_nl": "Sensii Hoofdstuk 3: Wat we gaan doen & Zorgplan",
            "description": "Omaha actievlakken, interventies, KBS streefscores, financiering (Zvw/Wlz/Wmo) en leveringsvormen.",
            "hoofdstuk": 3,
            "opt_file": "opts/sensire_sensii_h3_zorgplan_inzet.v1.opt",
            "rm_type": "COMPOSITION",
            "archetypes": [
                "openEHR-EHR-EVALUATION.omaha_assessment_nl.v0",
                "openEHR-EHR-INSTRUCTION.care_plan_request.v0",
                "openEHR-EHR-ACTION.care_plan.v0",
                "openEHR-EHR-ADMIN_ENTRY.care_funding_delivery_nl.v0",
                "openEHR-EHR-ACTION.health_education.v1",
                "openEHR-EHR-EVALUATION.clinical_synopsis.v1"
            ]
        },
        "sensire_sensii_h4_evaluatie.v1": {
            "template_id": "sensire_sensii_h4_evaluatie.v1",
            "name_nl": "Sensii Hoofdstuk 4: Evaluatie van zorg",
            "description": "Periodieke herbeoordeling van Omaha aandachtsgebieden, KBS scores, regietrede en hermeting GFI kwetsbaarheid.",
            "hoofdstuk": 4,
            "opt_file": "opts/sensire_sensii_h4_evaluatie.v1.opt",
            "rm_type": "COMPOSITION",
            "archetypes": [
                "openEHR-EHR-EVALUATION.omaha_assessment_nl.v0",
                "openEHR-EHR-OBSERVATION.self_management_regietrede_nl.v0",
                "openEHR-EHR-OBSERVATION.groningen_frailty_indicator_nl.v0",
                "openEHR-EHR-EVALUATION.goal.v1",
                "openEHR-EHR-EVALUATION.clinical_synopsis.v1"
            ]
        },
        "sensire_sensii_verpleegkundig_proces_integraal.v1": {
            "template_id": "sensire_sensii_verpleegkundig_proces_integraal.v1",
            "name_nl": "Sensii Integraal Verpleegkundig Proces",
            "description": "Het complete overkoepelende wijkverpleegkundige dossierportret van intake tot evaluatie.",
            "hoofdstuk": "all",
            "opt_file": "opts/sensire_sensii_verpleegkundig_proces_integraal.v1.opt",
            "rm_type": "COMPOSITION",
            "archetypes": [
                "openEHR-EHR-EVALUATION.triage_nursing_nl.v0",
                "openEHR-EHR-EVALUATION.nursing_vag_nl.v0",
                "openEHR-EHR-OBSERVATION.nursing_gordon_patterns_nl.v0",
                "openEHR-EHR-OBSERVATION.groningen_frailty_indicator_nl.v0",
                "openEHR-EHR-OBSERVATION.self_management_regietrede_nl.v0",
                "openEHR-EHR-EVALUATION.omaha_assessment_nl.v0",
                "openEHR-EHR-INSTRUCTION.care_plan_request.v0",
                "openEHR-EHR-ACTION.care_plan.v0",
                "openEHR-EHR-ADMIN_ENTRY.care_funding_delivery_nl.v0",
                "openEHR-EHR-ACTION.health_education.v1",
                "openEHR-EHR-EVALUATION.goal.v1",
                "openEHR-EHR-EVALUATION.clinical_synopsis.v1"
            ]
        }
    }

    # 3. Definieer de 7 Custom Archetypes
    archetypes = {
        "openEHR-EHR-OBSERVATION.groningen_frailty_indicator_nl.v0": {
            "name": "Groningen Frailty Indicator (GFI)",
            "rm_type": "OBSERVATION",
            "description": "Screening van kwetsbaarheid over 4 domeinen (15 items) met somscore 0-15 en cutoff >= 4.",
            "snomed_concept": "225544003",
            "nodes": {
                "fysiek_score": "data[at0001]/events[at0002]/data[at0003]/items[at0004]",
                "cognitief_score": "data[at0001]/events[at0002]/data[at0003]/items[at0009]",
                "sociaal_score": "data[at0001]/events[at0002]/data[at0003]/items[at0011]",
                "psychisch_score": "data[at0001]/events[at0002]/data[at0003]/items[at0014]",
                "totaalscore": "data[at0001]/events[at0002]/data[at0003]/items[at0017]",
                "is_kwetsbaar": "data[at0001]/events[at0002]/data[at0003]/items[at0018]"
            }
        },
        "openEHR-EHR-OBSERVATION.self_management_regietrede_nl.v0": {
            "name": "Regietrede en Zelfredzaamheid",
            "rm_type": "OBSERVATION",
            "description": "Inschaling van de 5 eigen regietreden en vergelijking tussen motoradvies, professional en cliënt.",
            "nodes": {
                "beoordeelde_trede": "data[at0001]/events[at0002]/data[at0003]/items[at0004]",
                "motor_advies_trede": "data[at0001]/events[at0002]/data[at0003]/items[at0010]",
                "draagkracht_balans": "data[at0001]/events[at0002]/data[at0003]/items[at0012]",
                "start_kennis_score": "data[at0001]/events[at0002]/data[at0003]/items[at0016]",
                "start_gedrag_score": "data[at0001]/events[at0002]/data[at0003]/items[at0017]"
            }
        },
        "openEHR-EHR-EVALUATION.omaha_assessment_nl.v0": {
            "name": "Omaha System Probleem en Zorgplan",
            "rm_type": "EVALUATION",
            "description": "Omaha 4 domeinen, 42 gebieden, prioriteitsslots (1-4), KBS scores en 4 actiesoorten.",
            "nodes": {
                "aandachtsgebied": "data[at0001]/items[at0002]",
                "domein": "data[at0001]/items[at0003]",
                "prioriteit": "data[at0001]/items[at0008]",
                "kbs_baseline": "data[at0001]/items[at0015]",
                "kbs_target": "data[at0001]/items[at0019]",
                "kbs_evaluatie": "data[at0001]/items[at0023]",
                "actiesoort": "data[at0001]/items[at0027]",
                "actievlak": "data[at0001]/items[at0032]"
            }
        },
        "openEHR-EHR-OBSERVATION.nursing_gordon_patterns_nl.v0": {
            "name": "11 Gezondheidspatronen van Gordon",
            "rm_type": "OBSERVATION",
            "description": "Systematische functionele verpleegkundige anamnese.",
            "patterns": [
                "Gezondheidsbeleving en -instandhouding", "Voedings- en stofwisselingspatroon",
                "Uitscheidingspatroon", "Activiteitenpatroon", "Slaap- en rustpatroon",
                "Cognitie- en waarnemingspatroon", "Zelfbelevingspatroon", "Rollen- en relatiepatroon",
                "Seksualiteits- en voortplantingspatroon", "Coping- en stresstolerantiepatroon",
                "Waarden- en overtuigingenpatroon"
            ]
        },
        "openEHR-EHR-EVALUATION.triage_nursing_nl.v0": {
            "name": "Wijkverpleegkundige Triage",
            "rm_type": "EVALUATION",
            "description": "Triagebesluit wijkverpleging, urgentiecategorie en relatietype (Langer Thuis).",
            "nodes": {
                "passendheid": "data[at0001]/items[at0002]",
                "urgentiecategorie": "data[at0001]/items[at0007]",
                "zorgrelatie_type": "data[at0001]/items[at0011]"
            }
        },
        "openEHR-EHR-EVALUATION.nursing_vag_nl.v0": {
            "name": "Verpleegkundig Adviesgesprek (VAG)",
            "rm_type": "EVALUATION",
            "description": "Hulpvraag, persoonlijke kracht, netwerkkracht en ordening van lasten.",
            "nodes": {
                "hulpvraag": "data[at0001]/items[at0002]",
                "wenselijke_situatie": "data[at0001]/items[at0003]",
                "persoonlijke_kracht": "data[at0001]/items[at0004]",
                "netwerkkracht": "data[at0001]/items[at0005]",
                "mantelzorgbelasting": "data[at0001]/items[at0006]"
            }
        },
        "openEHR-EHR-ADMIN_ENTRY.care_funding_delivery_nl.v0": {
            "name": "Zorgfinanciering en Leveringsvorm",
            "rm_type": "ADMIN_ENTRY",
            "description": "Financieringskader (Zvw/Wlz/Wmo), leveringsvorm (ZIN/PGB/VPT/MPT) en inzet in minuten.",
            "nodes": {
                "financieringsvorm": "data[at0001]/items[at0002]",
                "leveringsvorm": "data[at0001]/items[at0008]",
                "zorgminuten_per_week": "data[at0001]/items[at0013]",
                "inzet_beeldschermzorg": "data[at0001]/items[at0014]"
            }
        }
    }

    # 4. Breid de survey-mapping uit voor alle 58 formulieren
    surveys_map = {}
    if sections_data and "sections" in sections_data:
        for sec in sections_data["sections"]:
            sec_title = sec.get("title", "")
            hfd = sec.get("hoofdstuk", 2)
            
            # Bepaal template op basis van hoofdstuk
            t_id = f"sensire_sensii_h{hfd}_"
            if hfd == 1:
                t_id = "sensire_sensii_h1_intake_triage_vag.v1"
            elif hfd == 2:
                t_id = "sensire_sensii_h2_anamnese_diagnostiek.v1"
            elif hfd == 3:
                t_id = "sensire_sensii_h3_zorgplan_inzet.v1"
            elif hfd == 4:
                t_id = "sensire_sensii_h4_evaluatie.v1"

            for s_name in sec.get("surveys", []):
                arch_id = "openEHR-EHR-EVALUATION.clinical_synopsis.v1"
                rm_t = "EVALUATION"
                aql = f"SELECT c/name/value FROM EHR e CONTAINS COMPOSITION c[{t_id}]"

                if "Triage" in s_name:
                    arch_id = "openEHR-EHR-EVALUATION.triage_nursing_nl.v0"
                    rm_t = "EVALUATION"
                    aql = f"SELECT t/data[at0001]/items[at0002]/value/value as passendheid FROM EHR e CONTAINS COMPOSITION c CONTAINS EVALUATION t[{arch_id}]"
                elif any(k in s_name for k in ["Hulpvraag", "kracht", "lasten", "Adviesgesprek", "VAG"]):
                    arch_id = "openEHR-EHR-EVALUATION.nursing_vag_nl.v0"
                    rm_t = "EVALUATION"
                    aql = f"SELECT v/data[at0001]/items[at0002]/value/value as hulpvraag FROM EHR e CONTAINS COMPOSITION c CONTAINS EVALUATION v[{arch_id}]"
                elif "regietrede" in s_name.lower() or "kennis score" in s_name.lower() or "gedrag score" in s_name.lower():
                    arch_id = "openEHR-EHR-OBSERVATION.self_management_regietrede_nl.v0"
                    rm_t = "OBSERVATION"
                    aql = f"SELECT r/data[at0001]/events[at0002]/data[at0003]/items[at0004]/value/value as regietrede FROM EHR e CONTAINS COMPOSITION c CONTAINS OBSERVATION r[{arch_id}]"
                elif "GFI" in s_name:
                    arch_id = "openEHR-EHR-OBSERVATION.groningen_frailty_indicator_nl.v0"
                    rm_t = "OBSERVATION"
                    aql = f"SELECT g/data[at0001]/events[at0002]/data[at0003]/items[at0017]/value/magnitude as gfi_score FROM EHR e CONTAINS COMPOSITION c CONTAINS OBSERVATION g[{arch_id}]"
                elif any(str(i) in s_name for i in range(1, 12)) and ("Gezondheidsbeleving" in s_name or "Voedings" in s_name or "Uitscheiding" in s_name or "Coping" in s_name):
                    arch_id = "openEHR-EHR-OBSERVATION.nursing_gordon_patterns_nl.v0"
                    rm_t = "OBSERVATION"
                    aql = f"SELECT gp/data[at0001]/events[at0002]/data[at0003] FROM EHR e CONTAINS COMPOSITION c CONTAINS OBSERVATION gp[{arch_id}]"
                elif "Levensverhaal" in s_name or "kennen" in s_name or "Jezelf" in s_name or "Wonen" in s_name:
                    arch_id = "openEHR-EHR-OBSERVATION.story.v1"
                    rm_t = "OBSERVATION"
                    aql = f"SELECT s/data[at0001]/events[at0002]/data[at0003]/items[at0004]/value/value as verhaal FROM EHR e CONTAINS COMPOSITION c CONTAINS OBSERVATION s[{arch_id}]"
                elif "Behoeften" in s_name or "wensen" in s_name:
                    arch_id = "openEHR-EHR-EVALUATION.goal.v1"
                    rm_t = "EVALUATION"
                    aql = f"SELECT g/data[at0001]/items[at0002]/value/value as doel FROM EHR e CONTAINS COMPOSITION c CONTAINS EVALUATION g[{arch_id}]"
                elif "Omaha" in s_name or "Aandachtsgebied" in s_name:
                    arch_id = "openEHR-EHR-EVALUATION.omaha_assessment_nl.v0"
                    rm_t = "EVALUATION"
                    aql = f"SELECT o/data[at0001]/items[at0002]/value/value as gebied, o/data[at0001]/items[at0019]/value/value as kbs_doel FROM EHR e CONTAINS COMPOSITION c CONTAINS EVALUATION o[{arch_id}]"
                elif "Financiering" in s_name or "Leveringsvorm" in s_name or "Ondersteuningsbehoefte" in s_name:
                    arch_id = "openEHR-EHR-ADMIN_ENTRY.care_funding_delivery_nl.v0"
                    rm_t = "ADMIN_ENTRY"
                    aql = f"SELECT f/data[at0001]/items[at0002]/value/value as wet, f/data[at0001]/items[at0008]/value/value as leveringsvorm FROM EHR e CONTAINS COMPOSITION c CONTAINS ADMIN_ENTRY f[{arch_id}]"

                surveys_map[s_name] = {
                    "survey_name": s_name,
                    "section_title": sec_title,
                    "hoofdstuk": hfd,
                    "template_id": t_id,
                    "archetype_id": arch_id,
                    "rm_type": rm_t,
                    "aql_sample": aql
                }

    # 5. Bouw de overkoepelende JSON contract payload
    contract_data = {
        "_meta": {
            "schema_version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "producer": "OpenEHRDemo/scripts/export_sensii_contract.py",
            "description": "openEHR Semantisch Data-Contract voor Sensii Wijkverpleegkundig EPD",
            "total_surveys": len(surveys_map),
            "total_templates": len(templates),
            "total_custom_archetypes": len(archetypes)
        },
        "templates": templates,
        "archetypes": archetypes,
        "surveys": surveys_map,
        "omaha_domains": omaha_data.get("domeinen", {}),
        "specialized_pathways_integration": {
            "description": "Koppeling van Omaha aandachtsgebieden aan de 164 speciële zorgpaden (regulier & ReAble)",
            "triggers": {
                "Huid": ["sensire_w5_diabetische_voet_triage_o.v1", "sensire_w20_decubitus.v1", "sensire_w21_ulcus_cruris.v1"],
                "Medicatie": ["sensire_n26_medicatie_management_stri.v1", "sensire_n26_medicatie_management_stri_reable.v1"],
                "Uitscheiding": ["sensire_s6_verblijfskatheter_cad_ver.v1", "sensire_s11_urine_incontinentie_typen.v1"],
                "Ademhaling": ["sensire_c5_copd_longaanval_exacerbat.v1", "sensire_c8_astma_dagelijks_beheer_ex.v1"],
                "Mobiliteit": ["sensire_n14_valpreventie_multifactori.v1", "sensire_n14_valpreventie_multifactori_reable.v1"]
            }
        }
    }

    # Bepaal sha256 checksum van contract data
    json_bytes = json.dumps(contract_data, indent=2, sort_keys=True, ensure_ascii=False).encode("utf-8")
    sha256 = hashlib.sha256(json_bytes).hexdigest()
    contract_data["_meta"]["sha256_checksum"] = sha256

    # Schrijf naar dist/ in deze repository
    out_file = DIST_DIR / "sensii_openehr_contract.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(contract_data, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Contract succesvol geschreven naar {out_file.relative_to(REPO_ROOT)} ({len(json_bytes)} bytes)")

    # Exporteer direct naar Sensii als die map bestaat
    sensii_target = SENSII_PATH / "contract" / "sensii_openehr_contract.json"
    if SENSII_PATH.exists():
        sensii_target.parent.mkdir(parents=True, exist_ok=True)
        with open(sensii_target, "w", encoding="utf-8") as f:
            json.dump(contract_data, f, indent=2, ensure_ascii=False)
        print(f"  ✓ Gekopieerd naar Sensii: {sensii_target}")

    return contract_data

if __name__ == "__main__":
    generate_sensii_contract()
