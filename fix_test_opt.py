import xml.etree.ElementTree as ET

tree = ET.parse('test.opt')
ns = {'xsi': 'http://www.w3.org/2001/XMLSchema-instance', 'ns': 'http://schemas.openehr.org/v1'}

for c in tree.findall('.//*[@xsi:type="C_TERMINOLOGY_CODE"]', ns):
    c.set('{http://www.w3.org/2001/XMLSchema-instance}type', 'C_CODE_PHRASE')
    rm_el = c.find('ns:rm_type_name', ns)
    if rm_el is not None:
        rm_el.text = 'CODE_PHRASE'
    
    constraint = c.find('ns:constraint', ns)
    if constraint is not None:
        val = constraint.text
        if val and '::' in val:
            term, code = val.strip('[]').split('::')
            tid = ET.Element('terminology_id')
            tval = ET.SubElement(tid, 'value')
            tval.text = term
            c.append(tid)
            clist = ET.Element('code_list')
            clist.text = code
            c.append(clist)
        else:
            tid = ET.Element('terminology_id')
            tval = ET.SubElement(tid, 'value')
            tval.text = 'local'
            c.append(tid)
            clist = ET.Element('code_list')
            clist.text = val
            c.append(clist)
        c.remove(constraint)

tree.write('test_fixed.opt', xml_declaration=True, encoding='UTF-8')
