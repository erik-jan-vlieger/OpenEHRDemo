#!/usr/bin/env python3
"""
Quick search utility to find matching openEHR archetypes from the catalog.
Usage: python3 scripts/search_archetypes.py "blaaskatheter"
       python3 scripts/search_archetypes.py "bloeddruk" --rm OBSERVATION
"""

import sys
import json
import argparse
from pathlib import Path

NL_EN_MAP = {
    "blaas": "bladder",
    "katheter": "catheter",
    "blaaskatheter": "urinary catheter",
    "urineretentie": "retention",
    "urinelozing": "urination",
    "urine": "urine",
    "bloeddruk": "blood pressure",
    "hartslag": "pulse",
    "pols": "pulse",
    "ademhaling": "respiration",
    "temperatuur": "temperature",
    "koorts": "fever",
    "pijn": "pain",
    "pijnscore": "pain",
    "wond": "wound",
    "wondzorg": "wound",
    "ulcus": "ulcer",
    "doorliggen": "pressure ulcer",
    "decubitus": "pressure ulcer",
    "stoma": "stoma",
    "delier": "delirium",
    "valincident": "fall",
    "vallen": "fall",
    "medicatie": "medication",
    "vocht": "fluid",
    "vochtbalans": "fluid balance",
    "infuus": "infusion",
    "sonde": "tube",
    "sondevoeding": "enteral nutrition",
    "zuurstof": "oxygen",
    "saturatie": "oxygen saturation",
    "diabetes": "diabetes",
    "suiker": "glucose",
    "bloedsuiker": "blood glucose",
    "sedatie": "sedation",
    "palliatief": "palliative",
    "wilsverklaring": "advance care",
    "behandelgrenzen": "resuscitation",
    "reanimatie": "resuscitation",
    "infectie": "infection",
    "ontlasting": "faeces",
    "obstipatie": "constipation",
    "diarree": "diarrhoea",
    "continentie": "continence",
    "incontinentie": "incontinence"
}

def search_catalog(query, rm_type=None, limit=10):
    repo_root = Path(__file__).resolve().parent.parent
    cat_file = repo_root / "archetypes" / "archetype_catalog.json"
    
    if not cat_file.exists():
        print("Catalogus niet gevonden. Draai eerst: python3 scripts/index_archetypes.py")
        return []
        
    with open(cat_file, "r", encoding="utf-8") as f:
        catalog = json.load(f)
        
    q_tokens = query.lower().split()
    # Add translated tokens
    expanded_tokens = list(q_tokens)
    for t in q_tokens:
        if t in NL_EN_MAP:
            expanded_tokens.extend(NL_EN_MAP[t].split())
            
    results = []
    
    for arch_id, item in catalog.items():
        if rm_type and item.get("rm_type") != rm_type:
            continue
            
        score = 0
        name_en = item.get("concept_name_en", "").lower()
        name_nl = item.get("concept_name_nl", "").lower()
        purpose = item.get("purpose", "").lower()
        use_text = item.get("use", "").lower()
        keywords = " ".join(item.get("keywords", [])).lower()
        
        # Terms text
        terms_text = ""
        for lang_dict in item.get("terms", {}).values():
            terms_text += " " + " ".join(lang_dict.values()).lower()
            
        arch_id_lower = arch_id.lower()
        
        for tok in expanded_tokens:
            if tok in arch_id_lower:
                score += 10
            if tok in name_nl:
                score += 8
            if tok in name_en:
                score += 6
            if tok in keywords:
                score += 4
            if tok in purpose:
                score += 3
            if tok in use_text:
                score += 2
            if tok in terms_text:
                score += 1
                
        if score > 0:
            results.append((score, item))
            
    results.sort(key=lambda x: x[0], reverse=True)
    return [r[1] for r in results[:limit]]

def main():
    parser = argparse.ArgumentParser(description="Zoek openEHR archetypes in lokale catalogus")
    parser.add_argument("query", help="Zoekterm (EN of NL)")
    parser.add_argument("--rm", help="Filter op RM type (OBSERVATION, EVALUATION, INSTRUCTION, ACTION, CLUSTER, COMPOSITION)")
    parser.add_argument("-n", "--limit", type=int, default=10, help="Max aantal resultaten")
    
    args = parser.parse_args()
    results = search_catalog(args.query, args.rm, args.limit)
    
    print(f"\n🔍 Zoekresultaten voor '{args.query}' (totaal {len(results)}):\n")
    for r in results:
        nl_text = f" (NL: {r['concept_name_nl']})" if r.get('concept_name_nl') else ""
        print(f"• [{r['rm_type']}] {r['archetype_id']}")
        print(f"  Concept: {r['concept_name_en']}{nl_text}")
        print(f"  Bestand: {r['file_path']}")
        if r.get('purpose'):
            p_snippet = r['purpose'][:140] + ('...' if len(r['purpose']) > 140 else '')
            print(f"  Doel: {p_snippet}")
        print()

if __name__ == "__main__":
    main()
