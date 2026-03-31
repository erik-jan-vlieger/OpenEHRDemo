#!/usr/bin/env python3
"""
Converteert archie JAXB OPT XML naar het EHRbase-compatibele formaat.

archie genereert:
  <operational_template xmlns:ns2="http://schemas.openehr.org/v1" ...>
  
EHRbase verwacht:
  <template xmlns="http://schemas.openehr.org/v1">

Gebruik: python3 fix_opt_namespace.py <input.opt> [output.opt]
Als output weggelaten wordt, wordt het inputbestand overschreven.
"""

import sys
import re

def fix_opt(content: str) -> str:
    # 1. Vervang root-element opening tag
    content = re.sub(
        r'<operational_template[^>]*>',
        '<template xmlns="http://schemas.openehr.org/v1">',
        content,
        count=1
    )

    # 2. Vervang sluitende root tag
    content = content.replace('</operational_template>', '</template>')

    # 3. Vervang alle ns2: prefixes op elementen en attributen
    content = content.replace(' ns2:', ' ').replace('<ns2:', '<').replace('</ns2:', '</')

    # 4. Verwijder overbodige xmlns:ns2 declaraties op child-elementen
    content = re.sub(r'\s+xmlns:ns2="[^"]*"', '', content)

    return content


def main():
    if len(sys.argv) < 2:
        print("Gebruik: python3 fix_opt_namespace.py <input.opt> [output.opt]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else input_path

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    fixed = fix_opt(content)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(fixed)

    print(f"✅ Geconverteerd: {output_path}")
    # Toon eerste 150 bytes als verificatie
    print(f"   Begin: {fixed[:150].strip()}")


if __name__ == '__main__':
    main()
