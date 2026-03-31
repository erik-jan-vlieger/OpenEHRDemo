import sys
from lxml import etree

def check(file):
    ns = {'ns': 'http://schemas.openehr.org/v1', 'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}
    tree = etree.parse(file)
    roots = tree.xpath('//ns:children[@xsi:type="C_ARCHETYPE_ROOT"] | //ns:definition', namespaces=ns)
    
    missing = []
    
    for root in roots:
        # Get all term code definitions in this root
        tdefs = root.xpath('./ns:term_definitions/@code', namespaces=ns)
        
        # Get all node_ids in this root, but NOT inside nested C_ARCHETYPE_ROOTs
        # We need to traverse manually to avoid nested roots
        def walk(el):
            nids = []
            for child in el:
                if child.tag == '{http://schemas.openehr.org/v1}node_id' and child.text:
                    nids.append(child.text)
                elif child.tag == '{http://schemas.openehr.org/v1}children' and child.get('{http://www.w3.org/2001/XMLSchema-instance}type') == 'C_ARCHETYPE_ROOT':
                    pass # Don't go inside nested roots
                else:
                    nids.extend(walk(child))
            return nids
            
        nids_found = walk(root)
        
        for nid in set(nids_found):
            if nid not in tdefs and nid != '':
                missing.append((root.find('./ns:archetype_id/ns:value', namespaces=ns).text if root.find('./ns:archetype_id/ns:value', namespaces=ns) is not None else "UNKNOWN", nid))
                
    if missing:
        print(f"Missing terms in {file}:")
        for m in missing:
            print(f"Arch: {m[0]}, Node: {m[1]}")
    else:
        print(f"All good for {file}")

if __name__ == '__main__':
    for f in sys.argv[1:]:
        check(f)
