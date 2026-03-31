from lxml import etree

tree = etree.parse('sensireopenehr/sensire-openehr/opts/Diabetic_Foot_Assessment_Sensire.v1.opt.bak')
root = tree.getroot()
root.tag = '{http://schemas.openehr.org/v1}template'

for attr in ['is_generated', 'is_differential', 'adl_version']:
    if attr in root.attrib:
        del root.attrib[attr]

nsmap = {'ns2': 'http://schemas.openehr.org/v1'}
arch_id = root.find('ns2:archetype_id', namespaces=nsmap)
if arch_id is not None:
    concept_val = arch_id.get('concept_id')
    concept_el = etree.Element('concept')
    concept_el.text = concept_val
    root.insert(root.index(arch_id) + 1, concept_el)
    
    tid_el = etree.Element('template_id')
    tid_val = etree.SubElement(tid_el, 'value')
    tid_val.text = concept_val
    root.insert(root.index(arch_id) + 1, tid_el)
    
    uid_el = etree.Element('uid')
    uid_val = etree.SubElement(uid_el, 'value')
    uid_val.text = concept_val
    root.insert(root.index(arch_id) + 1, uid_el)

with open('test_post.xml', 'wb') as f:
    f.write(etree.tostring(root, xml_declaration=True, encoding='UTF-8'))
