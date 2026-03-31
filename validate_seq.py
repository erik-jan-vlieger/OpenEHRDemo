import xml.etree.ElementTree as ET

tree = ET.parse('test.opt')
ns = {'ns': 'http://schemas.openehr.org/v1', 'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}
roots = tree.findall('.//*[@xsi:type="C_ARCHETYPE_ROOT"]', ns) + tree.findall('.//ns:definition', ns)

valid_seq = ['rm_type_name', 'occurrences', 'node_id', 'attributes', 'archetype_id', 'template_id', 'term_definitions']

for r in roots:
    # Just literal tag names (strip namespace)
    child_tags = [c.tag.split('}')[-1] for c in r]
    
    # Check if they are in the expected order
    idx = -1
    for tag in child_tags:
        if tag in valid_seq:
            expected_idx = valid_seq.index(tag)
            if expected_idx < idx:
                print(f"Sequence ERROR in {r.tag}: {tag} appeared after a later element. Found seq: {child_tags}")
                break
            idx = expected_idx
        else:
            print(f"UNKNOWN tag in {r.tag}: {tag}")
