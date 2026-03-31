import xml.etree.ElementTree as ET

tree = ET.parse('test.opt')
ns = {'ns': 'http://schemas.openehr.org/v1', 'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}

# Find all elements with xsi:type="C_ARCHETYPE_ROOT" AND <definition>
roots = tree.findall('.//*[@xsi:type="C_ARCHETYPE_ROOT"]', ns)
defs = tree.findall('.//ns:definition', ns)

for r in (roots + defs):
    tag = r.tag
    nid = r.find('ns:node_id', ns)
    nid_text = nid.text if nid is not None else '?'
    aid = r.find('ns:archetype_id', ns)
    if aid is None:
        print(f"MISSING archetype_id in {tag} node_id={nid_text}")
    else:
        val = aid.find('ns:value', ns)
        if val is None or not val.text:
            print(f"MISSING value in archetype_id in {tag} node_id={nid_text}")
            
print(f"Total roots checked: {len(roots) + len(defs)}")
