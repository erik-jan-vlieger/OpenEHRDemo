#!/usr/bin/env python3
"""
Index all ADL 1.4 archetypes in the repository into a searchable JSON catalog.
Parses CKM mirror, international, and custom Sensire archetypes.
"""

import os
import re
import json
from pathlib import Path

# Common Dutch-English medical/nursing keyword mappings for seamless search
NL_EN_MAP = {
    "blaas": "bladder",
    "katheter": "catheter",
    "urineretentie": "retention",
    "urinelozing": "urination",
    "bloeddruk": "blood pressure",
    "hartslag": "pulse",
    "pols": "pulse",
    "ademhaling": "respiration",
    "temperatuur": "temperature",
    "koorts": "fever",
    "pijn": "pain",
    "pijnscore": "pain score",
    "wond": "wound",
    "wondzorg": "wound care",
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

def parse_adl_header(content):
    archetype_id_match = re.search(r'archetype\s*\([^)]*\)\s*([a-zA-Z0-9_\-\.]+)', content)
    archetype_id = archetype_id_match.group(1).strip() if archetype_id_match else None
    
    concept_match = re.search(r'concept\s*\[(at\d+)\]', content)
    concept_code = concept_match.group(1) if concept_match else 'at0000'
    
    # Extract language section
    lang_match = re.search(r'original_language\s*=\s*<\["ISO_639-1"\s*=\s*<"([^"]+)">\]', content)
    original_language = lang_match.group(1) if lang_match else 'en'
    
    # Extract purpose / description / use / misuse / keywords
    purpose_match = re.search(r'purpose\s*=\s*<"([^"]+)">', content)
    purpose = purpose_match.group(1).strip() if purpose_match else ""
    
    use_match = re.search(r'use\s*=\s*<"([^"]+)">', content)
    use_text = use_match.group(1).strip() if use_match else ""
    
    keywords = re.findall(r'"([^"]+)"', content[content.find("keywords"):content.find("use")] if "keywords" in content else "")
    
    # Extract terms in ontology
    term_defs = {}
    term_blocks = re.findall(r'\["([a-z]{2}(?:-[a-z]{2})?)"\]\s*=\s*<\s*items\s*=\s*<([\s\S]*?)>\s*>', content)
    for lang, items_block in term_blocks:
        term_defs[lang] = {}
        for item_match in re.finditer(r'\["(at\d+)"\]\s*=\s*<\s*text\s*=\s*<"([^"]*)">(?:[\s\S]*?description\s*=\s*<"([^"]*)">)?', items_block):
            code = item_match.group(1)
            text = item_match.group(2)
            desc = item_match.group(3) or ""
            term_defs[lang][code] = {"text": text, "description": desc}

    # Concept names
    concept_name_en = ""
    concept_name_nl = ""
    
    if "en" in term_defs and concept_code in term_defs["en"]:
        concept_name_en = term_defs["en"][concept_code]["text"]
    elif original_language in term_defs and concept_code in term_defs[original_language]:
        concept_name_en = term_defs[original_language][concept_code]["text"]
        
    if "nl" in term_defs and concept_code in term_defs["nl"]:
        concept_name_nl = term_defs["nl"][concept_code]["text"]

    # RM type
    rm_type = "UNKNOWN"
    if archetype_id:
        parts = archetype_id.split('-')
        if len(parts) >= 3:
            rm_type = parts[2].split('.')[0]

    return {
        "archetype_id": archetype_id,
        "rm_type": rm_type,
        "concept_code": concept_code,
        "concept_name_en": concept_name_en or (archetype_id.split('.')[-2] if archetype_id else ""),
        "concept_name_nl": concept_name_nl,
        "original_language": original_language,
        "available_languages": list(term_defs.keys()),
        "purpose": purpose,
        "use": use_text,
        "keywords": keywords,
        "terms": {lang: {k: v["text"] for k, v in codes.items()} for lang, codes in term_defs.items()}
    }

def main():
    repo_root = Path(__file__).resolve().parent.parent
    archetype_dirs = [
        ("custom", repo_root / "archetypes" / "custom"),
        ("international", repo_root / "archetypes" / "international"),
        ("ckm", repo_root / "archetypes" / "ckm-mirror" / "local" / "archetypes")
    ]
    
    catalog = {}
    
    for source_name, arch_dir in archetype_dirs:
        if not arch_dir.exists():
            continue
        for adl_file in arch_dir.rglob("*.adl"):
            try:
                content = adl_file.read_text(encoding="utf-8", errors="replace")
                info = parse_adl_header(content)
                arch_id = info["archetype_id"]
                if not arch_id:
                    continue
                info["source"] = source_name
                info["file_path"] = str(adl_file.relative_to(repo_root))
                catalog[arch_id] = info
            except Exception as e:
                print(f"Error parsing {adl_file}: {e}")
                
    out_file = repo_root / "archetypes" / "archetype_catalog.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Catalogus gegenereerd: {len(catalog)} unieke archetypes geïndexeerd in {out_file}")

if __name__ == "__main__":
    main()
