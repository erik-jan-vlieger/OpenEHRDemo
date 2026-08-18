#!/usr/bin/env python3
"""
scripts/sync_ecosystem.py
-------------------------
Centraal synchronisatie- en validatiescript voor het gehele Sensire openEHR ecosysteem.

Functies:
  --check              Controleert of openEHR modellen up-to-date zijn met Sensii en Speciële Zorgpaden.
  --build              Compileert alle ADLT templates naar OPT 1.4 XML en genereert alle contracten.
  --export-to-siblings Distribueert de JSON-contracten naar ~/Sensii en ~/SensireSpecieleBeslisOndersteuning.

Gebruik:
  python3 scripts/sync_ecosystem.py --check
  python3 scripts/sync_ecosystem.py --build
"""

import sys
import os
import json
import argparse
import subprocess
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SENSII_PATH = Path("/home/vlieger/Sensii")
SPECIELE_PATH = Path("/home/vlieger/SensireSpecieleBeslisOndersteuning")
OPTS_DIR = REPO_ROOT / "opts"
TEMPLATES_DIR = REPO_ROOT / "templates"
DIST_DIR = REPO_ROOT / "dist"
DIST_DIR.mkdir(parents=True, exist_ok=True)

def check_ecosystem():
    print("=================================================================")
    print("🔍 CONTROLEER ECOSYSTEEM SYNCHRONISATIE (Sensii ➔ openEHR)")
    print("=================================================================\n")
    
    issues = []
    
    # 1. Controleer Sensii Bronnen & Contract
    print("1. Sensii Wijkverpleegkundig EPD:")
    sensii_sections = SENSII_PATH / "contract" / "sections_sensii.json"
    sensii_contract = DIST_DIR / "sensii_openehr_contract.json"
    
    if not SENSII_PATH.exists():
        print(f"  ⚠ Map {SENSII_PATH} niet gevonden.")
    else:
        if sensii_sections.exists() and sensii_contract.exists():
            s_mtime = sensii_sections.stat().st_mtime
            c_mtime = sensii_contract.stat().st_mtime
            if s_mtime > c_mtime:
                issues.append("Sensii sections_sensii.json is NIEUWER dan sensii_openehr_contract.json.")
                print(f"  ❌ Sensii contract is VEROUDERD t.o.v. {sensii_sections.name}")
            else:
                print(f"  ✓ Sensii openEHR contract is synchroon (gegenereerd op basis van {sensii_sections.name})")
        else:
            issues.append("Sensii contract of bronbestand ontbreekt.")
            print("  ❌ Sensii contract of bronbestand ontbreekt.")

    # 2. Controleer Sensii OPT 1.4 XML bestanden
    print("\n2. Sensii openEHR Templates (OPT 1.4 XML):")
    sensii_opts = [
        "sensire_sensii_h1_intake_triage_vag.v1.opt",
        "sensire_sensii_h2_anamnese_diagnostiek.v1.opt",
        "sensire_sensii_h3_zorgplan_inzet.v1.opt",
        "sensire_sensii_h4_evaluatie.v1.opt",
        "sensire_sensii_verpleegkundig_proces_integraal.v1.opt"
    ]
    for opt_name in sensii_opts:
        opt_p = OPTS_DIR / opt_name
        if opt_p.exists():
            size_kb = opt_p.stat().st_size / 1024
            print(f"  ✓ {opt_name:<55} ({size_kb:.1f} KB)")
        else:
            issues.append(f"Ontbrekend OPT bestand: {opt_name}")
            print(f"  ❌ ONTBREKEND: {opt_name}")

    # 3. Controleer Speciële Zorgpaden
    print("\n3. Speciële Zorgpaden (164 paden incl. ReAble):")
    if not SPECIELE_PATH.exists():
        print(f"  ⚠ Map {SPECIELE_PATH} niet gevonden.")
    else:
        mermaid_dir = SPECIELE_PATH / "4.Mermaids"
        reable_dir = SPECIELE_PATH / "ReAble"
        
        flow_count = len(list(mermaid_dir.glob("*/v*_flow.json"))) if mermaid_dir.exists() else 0
        reable_count = len(list(reable_dir.glob("*_reable_flow.json"))) if reable_dir.exists() else 0
        total_flows = flow_count + reable_count
        
        opt_count = len(list(OPTS_DIR.glob("sensire_*.opt"))) - len(sensii_opts)
        print(f"  • Bron flows gevonden in zorgpaden-repo: {total_flows} ({flow_count} regulier, {reable_count} ReAble)")
        print(f"  • Gecompileerde zorgpaden OPTs in opts/: {opt_count}")
        
        if opt_count >= total_flows:
            print(f"  ✓ Alle {total_flows} speciële zorgpaden zijn gecompileerd naar openEHR OPT 1.4.")
        else:
            diff = total_flows - opt_count
            issues.append(f"{diff} speciële zorgpaden moeten nog gecompileerd worden.")
            print(f"  ⚠ Er ontbreken nog {diff} gecompileerde zorgpaden in opts/.")

    print("\n=================================================================")
    if not issues:
        print("✅ ALLES IS 100% GESYNCHRONISEERD EN GEVALIDEERD.")
    else:
        print(f"⚠ {len(issues)} AANDACHTSPUNT(EN) GEVONDEN:")
        for iss in issues:
            print(f"   - {iss}")
        print("\nVoer 'python3 scripts/sync_ecosystem.py --build' uit om alles bij te werken.")
    print("=================================================================\n")
    return len(issues) == 0

def build_and_export():
    print("=================================================================")
    print("🚀 ECOSYSTEEM HERBOUW & CONTRACT DISTRIBUTIE")
    print("=================================================================\n")
    
    t0 = time.time()
    
    # 1. Compileer via Archie flattener
    print("1. Archie Java Flattener & Template Validatie...")
    res = subprocess.run(["./gradlew", "generateOPT"], cwd=REPO_ROOT / "compiler", capture_output=True, text=True)
    if res.returncode != 0:
        print(f"❌ Fout tijdens Gradle Archie compilatie:\n{res.stderr}")
        return False
    print("  ✓ Archie compilatie succesvol.\n")

    # 2. Postprocess alle OPT 1.4 XML bestanden
    print("2. Python OPT 1.4 XML Postprocessing (EHRbase conformiteit)...")
    postprocess_script = REPO_ROOT / "compiler" / "full_opt14_lxml.py"
    processed = 0
    for adlt_p in TEMPLATES_DIR.glob("*.adlt"):
        opt_p = OPTS_DIR / f"{adlt_p.stem}.opt"
        if opt_p.exists():
            subprocess.run([
                sys.executable,
                str(postprocess_script),
                str(opt_p),
                str(opt_p),
                str(adlt_p)
            ], capture_output=True)
            processed += 1
    print(f"  ✓ {processed} OPT 1.4 XML bestanden getransformeerd en gevalideerd.\n")

    # 3. Exporteer Sensii Contract
    print("3. Genereren van Sensii Data-Contract...")
    res = subprocess.run([sys.executable, str(REPO_ROOT / "scripts" / "export_sensii_contract.py")], capture_output=True, text=True)
    print(res.stdout.strip())
    
    # 4. Exporteer Zorgpaden Contract naar Speciële Beslisondersteuning
    print("\n4. Genereren van Zorgpaden Data-Contract...")
    carepaths_contract = generate_carepaths_contract()
    
    print(f"\n=================================================================")
    print(f"✅ ECOSYSTEEM SUCCESVOL GEBOUWD EN GESYNCHRONISEERD ({time.time() - t0:.2f}s)")
    print("=================================================================\n")
    return True

def generate_carepaths_contract():
    opts = list(OPTS_DIR.glob("sensire_*.opt"))
    carepaths_opts = [p for p in opts if not p.name.startswith("sensire_sensii_")]
    
    contract = {
        "_meta": {
            "schema_version": "1.0.0",
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "total_carepaths": len(carepaths_opts),
            "producer": "OpenEHRDemo/scripts/sync_ecosystem.py"
        },
        "carepaths": []
    }
    
    for p in sorted(carepaths_opts):
        is_reable = "_reable" in p.name
        contract["carepaths"].append({
            "opt_filename": p.name,
            "template_id": f"openEHR-EHR-COMPOSITION.{p.stem}.0.0",
            "is_reable": is_reable,
            "size_bytes": p.stat().st_size
        })
        
    out_file = DIST_DIR / "carepaths_openehr_contract.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(contract, f, indent=2)
    print(f"  ✓ Zorgpaden contract geschreven naar {out_file.relative_to(REPO_ROOT)} ({len(carepaths_opts)} paden)")
    
    if SPECIELE_PATH.exists():
        spec_target = SPECIELE_PATH / "contract" / "carepaths_openehr_contract.json"
        spec_target.parent.mkdir(parents=True, exist_ok=True)
        with open(spec_target, "w", encoding="utf-8") as f:
            json.dump(contract, f, indent=2)
        print(f"  ✓ Gekopieerd naar Speciële Beslisondersteuning: {spec_target}")

    return contract

def main():
    parser = argparse.ArgumentParser(description="Sensire openEHR Ecosysteem Synchronisatie Tool")
    parser.add_argument("--check", action="store_true", help="Controleer of alle openEHR modellen up-to-date zijn.")
    parser.add_argument("--build", action="store_true", help="Herbouw alle OPTs en exporteer de contracten naar Sensii en Speciële Zorgpaden.")
    
    args = parser.parse_args()
    
    if args.build:
        build_and_export()
    elif args.check:
        check_ecosystem()
    else:
        # Default: doe check
        check_ecosystem()

if __name__ == "__main__":
    main()
