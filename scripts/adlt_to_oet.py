#!/usr/bin/env python3
import os
import re
import uuid
import sys
from pathlib import Path

def convert_adlt_to_oet(adlt_file, output_file):
    with open(adlt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Extract Template Name
    match_name = re.search(r'openEHR-EHR-COMPOSITION\.([a-zA-Z0-9_]+)\.v\d+', content)
    if not match_name:
        print(f"Kon template naam niet vinden in {adlt_file}")
        return
    template_name = match_name.group(1).title().replace('_', '').replace('Sensire', '_Sensire')
    # Let's just use the filename prefix as template name to be safe
    template_name = Path(adlt_file).stem
    
    # 2. Extract Purpose
    match_purpose = re.search(r'purpose\s*=\s*<"([^"]+)">', content)
    purpose = match_purpose.group(1) if match_purpose else "Sensire Wondzorg template."
    
    # 3. Extract term_definitions to map id -> text
    term_dict = {}
    term_block = re.search(r'term_definitions\s*=\s*<(.+?)>', content, re.DOTALL)
    if term_block:
        lines = term_block.group(1).split('\n')
        for line in lines:
            m = re.search(r'\["(id\d+)"\]\s*=\s*<text\s*=\s*<"([^"]+)">', line)
            if m:
                term_dict[m.group(1)] = m.group(2)
                
    # 4. Extract use_archetype lines
    archetypes = []
    for line in content.split('\n'):
        m = re.search(r'use_archetype\s+(COMPOSITION|EVALUATION|OBSERVATION|INSTRUCTION|ACTION|CLUSTER)\[(id\d+),\s*([^\]]+)\]', line)
        if m:
            rm_type = m.group(1)
            node_id = m.group(2)
            arch_id = m.group(3).strip()
            concept_name = term_dict.get(node_id, rm_type.capitalize())
            archetypes.append({
                'rm_type': rm_type,
                'arch_id': arch_id,
                'concept_name': concept_name
            })
            
    # Compose OET XML
    oet_uuid = str(uuid.uuid4())
    
    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<template xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="openEHR/v1/Template">
  <id>{oet_uuid}</id>
  <name>{template_name}</name>
  <description>
    <lifecycle_state>Initial</lifecycle_state>
    <details>
      <purpose>{purpose}</purpose>
      <use />
      <misuse />
    </details>
    <other_details>
      <item>
        <key>MetaDataSet:Sample Set </key>
        <value>Template metadata sample set </value>
      </item>
      <item>
        <key>Acknowledgements</key>
        <value />
      </item>
      <item>
        <key>Business Process Level</key>
        <value />
      </item>
      <item>
        <key>Care setting</key>
        <value />
      </item>
      <item>
        <key>Client group</key>
        <value />
      </item>
      <item>
        <key>Clinical Record Element</key>
        <value />
      </item>
      <item>
        <key>Copyright</key>
        <value />
      </item>
      <item>
        <key>Issues</key>
        <value />
      </item>
      <item>
        <key>Owner</key>
        <value />
      </item>
      <item>
        <key>Sign off</key>
        <value />
      </item>
      <item>
        <key>Speciality</key>
        <value />
      </item>
      <item>
        <key>User roles</key>
        <value />
      </item>
    </other_details>
  </description>
  <definition xsi:type="COMPOSITION" archetype_id="openEHR-EHR-COMPOSITION.encounter.v1" concept_name="Encounter">
"""
    
    for arch in archetypes:
        # Note: path="/content" assumes all archetypes go into the COMPOSITION content attribute.
        xml += f'    <Item xsi:type="{arch["rm_type"]}" archetype_id="{arch["arch_id"]}" concept_name="{arch["concept_name"]}" path="/content" />\n'
        
    xml += """  </definition>
</template>"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml)
    print(f"Gegenereerd: {output_file}")


def main():
    adlt_dir = Path('/home/vlieger/OpenEHRDemo/sensireopenehr/sensire-openehr/templates')
    out_dir = Path('/home/vlieger/OpenEHRDemo/templates_oet')
    out_dir.mkdir(parents=True, exist_ok=True)
    
    for f in adlt_dir.glob('*.adlt'):
        out_file = out_dir / f.with_suffix('.oet').name
        convert_adlt_to_oet(str(f), str(out_file))

if __name__ == '__main__':
    main()
