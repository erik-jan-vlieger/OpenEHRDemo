#!/usr/bin/env python3
"""
Converteert archie 3.x AOM2 XML-output naar valide OPT 1.4 XML voor EHRbase.

Problemen die worden opgelost:
  1. Root element: <operational_template xmlns:ns2="..."> → <template xmlns="...">
  2. Taal: <original_language> → <language> als direct child van <template>
  3. Concept: voeg <concept> in vanuit archetype_id concept_id attribuut
  4. AOM2 expressies in ARCHETYPE_SLOT: strip <expression xsi:type="binaryOperator">
     blokken (OPT 1.4 kent dit type niet; slots blijven 'gesloten')
  5. ns2: prefix verwijderen van alle elementen

Gebruik:
  python3 convert_to_opt14.py input.opt [output.opt]
  python3 convert_to_opt14.py --dir opts/  --out fixed_opts/
"""

import sys
import re
import os
import argparse
from xml.etree import ElementTree as ET


# ---------------------------------------------------------------------------
# Stap 1-3: string-level transformaties (snel en betrouwbaar op grote files)
# ---------------------------------------------------------------------------

def fix_string_level(content: str, template_id: str) -> str:
    """Voert root-element, namespace en language fixes uit via regex."""

    # 1. Haal concept_id op uit archetype_id attribuut
    m = re.search(r'concept_id="([^"]+)"', content)
    concept_id = m.group(1) if m else template_id

    # 2. Haal <original_language>...</original_language> op
    m_lang = re.search(r'<original_language>(.*?)</original_language>', content, re.DOTALL)
    if m_lang:
        lang_inner = m_lang.group(1).strip()
    else:
        lang_inner = """<terminology_id>
        <value>ISO_639-1</value>
    </terminology_id>
    <code_string>nl</code_string>"""

    # 3. Bouw nieuwe root header
    new_root = (
        f'<template xmlns="http://schemas.openehr.org/v1"\n'
        f'          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n'
        f'    <language>\n        {lang_inner}\n    </language>\n'
        f'    <concept>{concept_id}</concept>'
    )

    # 4. Vervang root opening tag
    content = re.sub(r'<operational_template[^>]*>', new_root, content, count=1)

    # 5. Vervang root sluitende tag
    content = content.replace('</operational_template>', '</template>')

    # 6. Verwijder <original_language>...</original_language> (nu al als <language> ingevoegd)
    content = re.sub(r'\s*<original_language>.*?</original_language>', '',
                     content, flags=re.DOTALL)

    # 7. Verwijder ns2: prefix
    content = content.replace(' ns2:', ' ')
    content = content.replace('<ns2:', '<')
    content = content.replace('</ns2:', '</')
    content = re.sub(r'\s+xmlns:ns2="[^"]*"', '', content)

    return content


# ---------------------------------------------------------------------------
# Stap 4: verwijder AOM 2-specifieke expression blokken uit ARCHETYPE_SLOTs
# ---------------------------------------------------------------------------

def strip_aom2_expressions(content: str) -> str:
    """
    Verwijdert <expression xsi:type="binaryOperator|..."> blokken die
    AOM 2-specifiek zijn en niet in het OPT 1.4 XSD voorkomen.

    Deze expressies komen voor als include/exclude constraints op ARCHETYPE_SLOTs.
    In OPT 1.4 worden deze weggelaten (slot wordt 'gesloten').
    """
    aom2_types = [
        'binaryOperator', 'modelReference', 'operatorDefBuiltin',
        'constraint', 'expressionVariable', 'functionCall', 'unaryOperator',
        'expressionLeaf'
    ]

    for t in aom2_types:
        # Verwijder elementen met dit xsi:type (geneste blokken inclusief)
        # Gebruik een eenvoudige teller-aanpak voor genesting
        tag_open = f'xsi:type="{t}"'
        while tag_open in content:
            idx = content.find(tag_open)
            if idx == -1:
                break
            # Ga terug naar het '<' van dit element
            start = content.rfind('<', 0, idx)
            if start == -1:
                break
            # Bepaal element-naam
            m = re.match(r'<([a-zA-Z_][a-zA-Z0-9_:.-]*)', content[start:])
            if not m:
                break
            elem_name = m.group(1)
            # Verwijder volledig element (inclusief geneste content)
            close_tag = f'</{elem_name}>'
            end = content.find(close_tag, start)
            if end == -1:
                # Self-closing? probeer />
                end = content.find('/>', start)
                if end == -1:
                    break
                end += 2
            else:
                end += len(close_tag)
            content = content[:start] + content[end:]

    return content


def reorder_multiplicity_intervals(content: str) -> str:
    """
    OPT 1.4 XSD schrijft voor dat elementen binnen een MULTIPLICITY_INTERVAL
    in volgorde: lower_included, upper_included, lower_unbounded, upper_unbounded, lower, upper.
    Archie genereert ze in een andere volgorde. We herordenen ze.
    """
    ORDER = ['lower_included', 'upper_included', 'lower_unbounded', 'upper_unbounded', 'lower', 'upper']

    def reorder_block(m):
        attrs = m.group(1)  # attributen van <occurrences ...>
        inner = m.group(2)  # inhoud van het element

        # Extraheer elk kind-element en zijn waarde
        elements = {}
        for name in ORDER:
            e = re.search(rf'<{name}(?:\s[^>]*)?>(.*?)</{name}>', inner, re.DOTALL)
            if e:
                elements[name] = e.group(0)

        if not elements:
            return m.group(0)  # Niets te herordenen

        new_inner = '\n'
        for name in ORDER:
            if name in elements:
                new_inner += '        ' + elements[name] + '\n'

        return f'<occurrences{attrs}>\n{new_inner}    </occurrences>'

    content = re.sub(
        r'<occurrences([^>]*)>(.*?)</occurrences>',
        reorder_block,
        content,
        flags=re.DOTALL
    )
    return content


def validate_xml(content: str, name: str) -> bool:
    try:
        ET.fromstring(content)
        return True
    except ET.ParseError as e:
        print(f"  ⚠ XML parse waarschuwing voor {name}: {e}", file=sys.stderr)
        return False


# ---------------------------------------------------------------------------
# Hoofdfunctie
# ---------------------------------------------------------------------------

def convert_file(input_path: str, output_path: str) -> bool:
    name = os.path.basename(input_path)
    template_id = re.sub(r'\.(opt|adlt)$', '', name)

    print(f"Converteren: {name}", end=' ... ', flush=True)

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Controleer of het al OPT 1.4 is
    if content.strip().startswith('<?xml') and '<template xmlns=' in content.split('\n', 5)[-1]:
        print("al OPT 1.4 formaat, geen conversie nodig")
        if input_path != output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
        return True

    # Stap 1-3: string-level fixes (namespace, root element, language, concept)
    content = fix_string_level(content, template_id)

    # Stap 4: AOM2 expressies strippen
    content = strip_aom2_expressions(content)

    # Stap 5: camelCase element namen → underscore (stringExpression → string_expression)
    content = content.replace('<stringExpression>', '<string_expression>')
    content = content.replace('</stringExpression>', '</string_expression>')

    # Stap 6: occurrences element-volgorde corrigeren (OPT 1.4 XSD vereiste)
    content = reorder_multiplicity_intervals(content)

    # Schrijf resultaat
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    valid = validate_xml(content, name)
    print(f"✅ ({len(content):,} bytes{', XML-valide' if valid else ', XML parse issues'})")
    return True


def main():
    parser = argparse.ArgumentParser(description='Converteer archie AOM2 XML naar OPT 1.4')
    parser.add_argument('input', nargs='?', help='Input .opt bestand')
    parser.add_argument('output', nargs='?', help='Output .opt bestand (default: overschrijf input)')
    parser.add_argument('--dir', help='Verwerk alle .opt bestanden in deze map')
    parser.add_argument('--out', help='Output map (bij gebruik van --dir)')
    args = parser.parse_args()

    if args.dir:
        src_dir = args.dir
        dst_dir = args.out or src_dir
        os.makedirs(dst_dir, exist_ok=True)
        count = 0
        for fname in sorted(os.listdir(src_dir)):
            if fname.endswith('.opt'):
                convert_file(
                    os.path.join(src_dir, fname),
                    os.path.join(dst_dir, fname)
                )
                count += 1
        print(f"\n{count} bestanden verwerkt → {dst_dir}")
    elif args.input:
        output = args.output or args.input
        convert_file(args.input, output)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
