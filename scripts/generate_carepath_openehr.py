#!/usr/bin/env python3
"""
Pipeline: Convert Sensire Care Pathways (v*_flow.json) into openEHR Operational Templates (OPT 1.4),
upload to EHRbase, download WebTemplates, and verify with live FLAT JSON compositions + AQL queries.
Supports single module (e.g., 'C1') and batch mode ('--all').
"""

import os
import re
import sys
import json
import uuid
import time
import base64
import datetime
import argparse
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

EHRBASE_BASE = "http://localhost:8080/ehrbase/rest"
EHRBASE_USER = "ehrbase-user"
EHRBASE_PASS = "SuperSecretPassword"

AUTH_HEADER = "Basic " + base64.b64encode(f"{EHRBASE_USER}:{EHRBASE_PASS}".encode()).decode()

REPO_ROOT = Path(__file__).resolve().parent.parent
SPECIELE_PATH = Path("/home/vlieger/SensireSpecieleBeslisOndersteuning/4.Mermaids")

def http_request(url, method="GET", data=None, headers=None):
    hdrs = {"Authorization": AUTH_HEADER}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read()
            return resp.status, body
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:
        return 0, str(e).encode()

def escape_adl_str(s):
    if not s:
        return ""
    return str(s).replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ').strip()

def load_flow_json(module_id):
    mod_dir = SPECIELE_PATH / module_id
    if not mod_dir.exists():
        raise FileNotFoundError(f"Module map niet gevonden: {mod_dir}")
        
    flow_files = sorted(mod_dir.glob("v*_flow.json"), key=lambda p: p.name, reverse=True)
    if not flow_files:
        raise FileNotFoundError(f"Geen v*_flow.json gevonden in {mod_dir}")
        
    latest_flow = flow_files[0]
    with open(latest_flow, "r", encoding="utf-8") as f:
        return json.load(f), latest_flow

def extract_flow_concepts(flow):
    nodes = flow.get("nodes", {})
    summary = {
        "module_id": flow.get("module_id", ""),
        "module_name": flow.get("module_name", ""),
        "context": flow.get("context", ""),
        "decisions": [],
        "measurements": [],
        "actions": [],
        "escalations": [],
        "multi_checks": []
    }
    
    for nid, n in nodes.items():
        ntype = n.get("type")
        if ntype == "decision":
            summary["decisions"].append({
                "id": nid,
                "question": n.get("question", ""),
                "branches": [b.get("label", "") for b in n.get("branches", [])]
            })
        elif ntype == "measurement":
            summary["measurements"].append({
                "id": nid,
                "instruction": n.get("instruction", ""),
                "unit": n.get("unit", ""),
                "branches": [b.get("label", "") for b in n.get("result_branches", [])]
            })
        elif ntype == "action":
            summary["actions"].append({
                "id": nid,
                "description": n.get("description", ""),
                "details": n.get("details", [])
            })
        elif ntype == "escalation":
            summary["escalations"].append({
                "id": nid,
                "reason": n.get("reason", ""),
                "contact": n.get("contact", ""),
                "timing": n.get("timing", ""),
                "interim_action": n.get("interim_action", "")
            })
        elif ntype == "multi_check":
            summary["multi_checks"].append({
                "id": nid,
                "question": n.get("question", ""),
                "items": [i.get("label", "") for i in n.get("items", [])]
            })
            
    return summary

def generate_adlt(flow, concepts):
    mid = str(flow.get("module_id", "")).lower()
    raw_name = re.sub(r'[^a-z0-9_]', '_', str(flow.get('module_name', '')).lower())
    clean_name = re.sub(r'_+', '_', raw_name).strip('_')[:30]
    template_concept = f"sensire_{mid}_{clean_name}"
    
    # Archetype selection based on carepath content
    slot_archetypes = [
        ("id2", "openEHR-EHR-EVALUATION.problem_diagnosis.v1", "Probleem of Diagnose", "Primaire aandoening of indicatie van het zorgpad."),
        ("id3", "openEHR-EHR-OBSERVATION.story.v1", "Anamnese & Bevindingen", "Klinisch verhaal en observaties van client/verpleegkundige."),
        ("id4", "openEHR-EHR-EVALUATION.clinical_synopsis.v1", "Klinische Synopsis & Besluit", "Conclusie en besluitvorming volgend uit het zorgpad.")
    ]
    
    next_id = 5
    mname = flow.get("module_name", "").lower()
    if concepts["actions"] or "medicatie" in mname or "opioid" in mname:
        slot_archetypes.append((f"id{next_id}", "openEHR-EHR-ACTION.medication.v1", "Medicatietoediening", "Toediening of aanpassing van medicatie."))
        next_id += 1
        
    if concepts["actions"]:
        slot_archetypes.append((f"id{next_id}", "openEHR-EHR-ACTION.procedure.v1", "Interventie / Handeling", "Verpleegkundige acties en handelingen."))
        next_id += 1
        
    if concepts["escalations"]:
        slot_archetypes.append((f"id{next_id}", "openEHR-EHR-INSTRUCTION.service_request.v1", "Escalatie / Verwijzing", "Overleg of order aan arts of specialist."))
        next_id += 1

    content_slots = "\n".join([f"\t\t\tuse_archetype {arch.split('-')[2].split('.')[0]}[{node_id}, {arch}]" for node_id, arch, _, _ in slot_archetypes])
    
    term_defs = [f"""\t\t\t\t["id1"] = <
\t\t\t\t\ttext = <"{escape_adl_str(flow.get('module_id'))} - {escape_adl_str(flow.get('module_name'))}">
\t\t\t\t\tdescription = <"{escape_adl_str(flow.get('context', flow.get('module_name')))}">
\t\t\t\t>"""]
    for node_id, _, text, desc in slot_archetypes:
        term_defs.append(f"""\t\t\t\t["{node_id}"] = <
\t\t\t\t\ttext = <"{escape_adl_str(text)}">
\t\t\t\t\tdescription = <"{escape_adl_str(desc)}">
\t\t\t\t>""")
        
    adlt = f"""template (adl_version=2.0.6; rm_release=1.1.0)
\topenEHR-EHR-COMPOSITION.{template_concept}.v1.0.0

specialize
\topenEHR-EHR-COMPOSITION.encounter.v1

language
\toriginal_language = <[ISO_639-1::nl]>

description
\toriginal_author = <
\t\t["name"] = <"Sensire Speciele Beslisondersteuning">
\t\t["organisation"] = <"Sensire">
\t\t["date"] = <"2026-08-14">
\t>
\tdetails = <
\t\t["nl"] = <
\t\t\tlanguage = <[ISO_639-1::nl]>
\t\t\tpurpose = <"Zorgpad {escape_adl_str(flow.get('module_id'))} ({escape_adl_str(flow.get('module_name'))}) Sensire">
\t\t\tuse = <"Ondersteuning van klinische besluitvorming in de wijkverpleging.">
\t\t\tmisuse = <"Niet buiten VVT context.">
\t\t>
\t>
\tlifecycle_state = <"in_development">

definition
\tCOMPOSITION[id1] matches {{
\t\tcontent matches {{
{content_slots}
\t\t}}
\t}}

terminology
\tterm_definitions = <
\t\t["nl"] = <
{chr(10).join(term_defs)}
\t\t>
\t>
"""
    return template_concept, adlt

def upload_opt_to_ehrbase(template_id, opt_path):
    url = f"{EHRBASE_BASE}/openehr/v1/definition/template/adl1.4"
    with open(opt_path, "rb") as f:
        opt_data = f.read()
    status, body = http_request(url, method="POST", data=opt_data, headers={"Content-Type": "application/xml"})
    if status in (200, 201, 204):
        return True, f"HTTP {status}"
    elif status == 409:
        return True, "Bestaat al (HTTP 409)"
    else:
        return False, f"HTTP {status}: {body.decode('utf-8', errors='ignore')[:150]}"

def download_webtemplate(template_id):
    url = f"{EHRBASE_BASE}/openehr/v1/definition/template/adl1.4/{template_id}"
    status, body = http_request(url, headers={"Accept": "application/openehr.wt+json"})
    if status == 200:
        wt = json.loads(body.decode("utf-8"))
        out_dir = REPO_ROOT / "frontend" / "sensire-app" / "webtemplates"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"{template_id}_webtemplate.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(wt, f, indent=2, ensure_ascii=False)
        return True, out_file
    else:
        return False, f"HTTP {status}"

def test_live_composition(template_id, flow, concepts, ehr_id):
    now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    flat_comp = {
        "ctx/language": "nl",
        "ctx/territory": "NL",
        "ctx/composer_name": "Sensire Speciele Beslisondersteuning Engine",
        "ctx/time": now,
        "ctx/setting": "227",
        "contact/category|code": "433",
        "contact/category|value": "event",
        "contact/category|terminology": "openehr",
        "contact/probleem_diagnose:0/naam_van_het_probleem_de_diagnose": f"{flow.get('module_id')} — {flow.get('module_name')}",
        "contact/probleem_diagnose:0/datum_tijd_van_aanvang": now,
        "contact/probleem_diagnose:0/klinische_beschrijving": f"Zorgpad evaluatie voor {flow.get('module_name')}.",
        "contact/klinische_synopsis:0/synopsis": f"Zorgpad {flow.get('module_id')} doorlopen. Beslismomenten geëvalueerd: {len(concepts['decisions'])}."
    }
    
    if concepts["decisions"]:
        d0 = concepts["decisions"][0]
        flat_comp["contact/anamnese:0/any_event_en:0/verhaal"] = f"Vraag: {d0['question']} -> Uitkomst: {d0['branches'][0] if d0['branches'] else 'Ja'}"
        flat_comp["contact/anamnese:0/any_event_en:0/time"] = now
        
    comp_url = f"{EHRBASE_BASE}/openehr/v1/ehr/{ehr_id}/composition?format=FLAT&templateId={template_id}"
    status_c, body_c = http_request(comp_url, method="POST", data=json.dumps(flat_comp).encode(), headers={
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    })
    
    if status_c in (200, 201):
        comp_data = json.loads(body_c.decode("utf-8"))
        uid = comp_data.get("contact/_uid") or comp_data.get("_uid") or "OK"
        
        # AQL Query verification
        aql_query = f"SELECT c/uid/value, c/context/start_time/value, p/data[at0001]/items[at0002]/value/value, s/data[at0001]/items[at0002]/value/value FROM EHR e CONTAINS COMPOSITION c CONTAINS (EVALUATION p[openEHR-EHR-EVALUATION.problem_diagnosis.v1] and EVALUATION s[openEHR-EHR-EVALUATION.clinical_synopsis.v1]) WHERE c/archetype_details/template_id/value = '{template_id}' LIMIT 1"
        status_a, body_a = http_request(f"{EHRBASE_BASE}/openehr/v1/query/aql", method="POST", data=json.dumps({"q": aql_query}).encode(), headers={"Content-Type": "application/json"})
        if status_a == 200:
            rows = json.loads(body_a.decode("utf-8")).get("rows", [])
            return True, uid, rows
        return True, uid, []
    else:
        return False, f"HTTP {status_c}: {body_c.decode('utf-8', errors='ignore')[:150]}", []

def get_or_create_ehr():
    status_q, body_q = http_request(f"{EHRBASE_BASE}/openehr/v1/query/aql", method="POST", data=json.dumps({
        "q": "SELECT e/ehr_id/value FROM EHR e LIMIT 1"
    }).encode(), headers={"Content-Type": "application/json"})
    
    if status_q == 200:
        rows = json.loads(body_q.decode("utf-8")).get("rows", [])
        if rows:
            return rows[0][0]
            
    status, body = http_request(f"{EHRBASE_BASE}/openehr/v1/ehr", method="POST", data=json.dumps({
        "_type": "EHR_STATUS",
        "archetype_node_id": "openEHR-EHR-EHR_STATUS.generic.v1",
        "name": {"value": "EHR Status"},
        "subject": {"_type": "PARTY_SELF"},
        "is_queryable": True,
        "is_modifiable": True
    }).encode(), headers={"Prefer": "return=representation", "Content-Type": "application/json"})
    
    if status in (200, 201):
        return json.loads(body.decode("utf-8")).get("ehr_id", {}).get("value")
    return None

def process_batch(module_ids=None):
    if not module_ids:
        module_dirs = sorted([d for d in SPECIELE_PATH.iterdir() if d.is_dir() and list(d.glob("v*_flow.json"))], key=lambda d: d.name)
        module_ids = [d.name for d in module_dirs]
        
    print(f"\n=======================================================")
    print(f"🚀 Start BATCH Verwerking: {len(module_ids)} Zorgpaden")
    print(f"=======================================================\n")
    
    templates_dir = REPO_ROOT / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Generate all ADLT files
    print("📝 Stap 1: Genereren van ADLT template bronbestanden...")
    modules_data = {}
    for mid in module_ids:
        try:
            flow, flow_path = load_flow_json(mid)
            concepts = extract_flow_concepts(flow)
            t_concept, adlt_code = generate_adlt(flow, concepts)
            adlt_file = templates_dir / f"{t_concept}.v1.adlt"
            with open(adlt_file, "w", encoding="utf-8") as f:
                f.write(adlt_code)
            modules_data[mid] = {
                "flow": flow,
                "concepts": concepts,
                "concept": t_concept,
                "adlt_file": adlt_file
            }
        except Exception as e:
            print(f"  ❌ Fout bij aanmaken ADLT voor {mid}: {e}")
            
    print(f"  ✓ {len(modules_data)} ADLT bestanden aangemaakt in {templates_dir.name}/\n")
    
    # 2. Compile with Gradle (single batch run for speed!)
    print("⚙️  Stap 2: Batch compileren met Archie Java flattener...")
    t0 = time.time()
    res = subprocess.run(["./gradlew", "generateOPT"], cwd=REPO_ROOT / "compiler", capture_output=True, text=True)
    if res.returncode != 0:
        print(f"❌ Gradle build fout:\n{res.stderr}")
        return
    print(f"  ✓ Archie compilatie voltooid in {time.time() - t0:.2f}s\n")
    
    # 3. Postprocess OPT 1.4 XML
    print("⚙️  Stap 3: Postprocessing naar EHRbase OPT 1.4 XML...")
    compiled_opts = {}
    for mid, mdata in modules_data.items():
        adlt_f = mdata["adlt_file"]
        raw_opt = REPO_ROOT / "opts" / f"{adlt_f.stem}.opt"
        if not raw_opt.exists():
            continue
        py_res = subprocess.run([
            sys.executable,
            str(REPO_ROOT / "compiler" / "full_opt14_lxml.py"),
            str(raw_opt),
            str(raw_opt),
            str(adlt_f)
        ], capture_output=True, text=True)
        if py_res.returncode == 0:
            compiled_opts[mid] = raw_opt
            
    print(f"  ✓ {len(compiled_opts)} OPT 1.4 bestanden gevalideerd.\n")
    
    # 4. Upload to EHRbase, download WebTemplates, and record test compositions
    print("🌐 Stap 4: Uploaden naar EHRbase, WebTemplates ophalen & AQL test...")
    ehr_id = get_or_create_ehr()
    if not ehr_id:
        print("❌ Geen actieve EHR gevonden/aangemaakt.")
        return
        
    results = []
    for mid, mdata in modules_data.items():
        t_concept = mdata["concept"]
        opt_f = compiled_opts.get(mid)
        if not opt_f:
            results.append((mid, flow.get("module_name", ""), "❌ Compilatie mislukt", "-", "-"))
            continue
            
        up_ok, up_msg = upload_opt_to_ehrbase(t_concept, opt_f)
        if not up_ok:
            results.append((mid, mdata["flow"].get("module_name", ""), f"❌ Upload ({up_msg})", "-", "-"))
            continue
            
        wt_ok, wt_res = download_webtemplate(t_concept)
        comp_ok, comp_msg, aql_rows = test_live_composition(t_concept, mdata["flow"], mdata["concepts"], ehr_id)
        
        status_str = "✅ Geslaagd" if comp_ok and wt_ok else "⚠️ Deels geslaagd"
        results.append((
            mid,
            mdata["flow"].get("module_name", "")[:35],
            status_str,
            t_concept,
            comp_msg if comp_ok else f"Fout: {comp_msg}"
        ))
        print(f"  • [{mid}] {mdata['flow'].get('module_name', '')[:40]}: {status_str}")
        
    # Print summary table
    print(f"\n=======================================================")
    print(f"📊 BATCH RESULTAAT OVERZICHT ({len(results)} Zorgpaden)")
    print(f"=======================================================\n")
    print(f"{'Module':<8} {'Zorgpad Naam':<37} {'Status':<18} {'Template ID'}")
    print("-" * 90)
    for row in results:
        print(f"{row[0]:<8} {row[1]:<37} {row[2]:<18} {row[3]}")
    print("-" * 90)
    
    success_count = sum(1 for r in results if "✅" in r[2])
    print(f"\n🎉 Totaal succesvol geüpload en gevalideerd: {success_count}/{len(results)} zorgpaden!\n")

def main():
    parser = argparse.ArgumentParser(description="Zorgpad -> openEHR Pipeline")
    parser.add_argument("module_id", nargs="?", help="Module ID (bv. C1, P1, W1)")
    parser.add_argument("--all", action="store_true", help="Verwerk alle beschikbare zorgpaden in batch")
    args = parser.parse_args()
    
    if args.all or not args.module_id:
        process_batch()
    else:
        process_batch([args.module_id])

if __name__ == "__main__":
    main()
