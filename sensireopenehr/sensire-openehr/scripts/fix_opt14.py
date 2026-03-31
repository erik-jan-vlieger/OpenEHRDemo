import sys
import re
import os
from lxml import etree

def get_node_id_mapping(adlt_content):
    node_map = {}
    for m in re.finditer(r'\[(id\d+),\s*(openEHR-[^\]]+)\]', adlt_content):
        node_map[m.group(1)] = m.group(2)
    return node_map

def convert_aom2_to_opt14(input_opt_bak, output_opt, adlt_path):
    print(f"Processing {os.path.basename(input_opt_bak)}...")
    
    with open(adlt_path, 'r', encoding='utf-8') as f:
        mapping = get_node_id_mapping(f.read())
        
    tree = etree.parse(input_opt_bak)
    root = tree.getroot()
    
    # STRIP ALL NAMESPACES FOR EASY PROCESSING
    for el in root.iter():
        el.tag = el.tag.split('}')[-1]
        
    ns2 = 'http://schemas.openehr.org/v1'
    
    # 1. Extract Concept and Parent Arch ID first
    arch_id_el = root.find('archetype_id')
    concept_id = arch_id_el.get('concept_id') if arch_id_el is not None else os.path.basename(input_opt_bak).replace('.opt.bak','').replace('.opt','')
    
    parent_arch_id_el = root.find('parent_archetype_id')
    parent_arch_id = parent_arch_id_el.text if parent_arch_id_el is not None else concept_id

    # --- BUILD TERMINOLOGY DICTIONARY ---
    lang_el = root.find('.//original_language/code_string')
    default_lang = lang_el.text if lang_el is not None else 'nl'
    
    term_dict = {}
    id_dict = {}
    import copy
    for term in root.findall('terminology') + root.findall('component_terminologies'):
        arch_id = term.get('archetype_id')
        if not arch_id:
            arch_id = parent_arch_id
        base_id = re.sub(r'\.v\d+.*$', '', arch_id)
        
        tdefs_for_arch = []
        lang_block = term.find(f'term_definitions[@language="{default_lang}"]')
        if lang_block is None:
            lang_block = term.find('term_definitions')
            
        if lang_block is not None:
            for item in lang_block.findall('items'):
                code = item.get('id')
                new_tdef = etree.Element('term_definitions')
                new_tdef.set('code', code)
                for child in item:
                    new_item = etree.SubElement(new_tdef, 'items')
                    new_item.set('id', child.tag)
                    new_item.text = child.text
                tdefs_for_arch.append(new_tdef)
                if code.startswith('id'):
                    id_dict[code] = new_tdef
                
        term_dict[base_id] = tdefs_for_arch

    def fix_term_id(parent):
        for term in parent.xpath('.//terminology_id'):
            if len(term) == 0 and term.text and term.text.strip():
                val = term.text.strip()
                if '<value>' not in val:
                    term.text = ''
                    vel = etree.Element('value')
                    vel.text = val
                    term.append(vel)

    # 1. ROOT
    new_root = etree.Element(f'{{{ns2}}}template', nsmap={
        None: ns2, 
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xs': 'http://www.w3.org/2001/XMLSchema'
    })
    
    # 2. LANGUAGE
    old_lang = root.find('original_language')
    if old_lang is not None:
        lang_el = etree.Element('language')
        for c in list(old_lang): lang_el.append(c)
        fix_term_id(lang_el)
        new_root.append(lang_el)
        
    # 3. DESCRIPTION
    desc_el = root.find('description')
    if desc_el is not None:
        # Check lifecycle_state
        if desc_el.find('lifecycle_state') is None:
            ls = etree.Element('lifecycle_state')
            ls.text = 'published'
            det = desc_el.find('details')
            if det is not None:
                desc_el.insert(desc_el.index(det), ls)
            else:
                desc_el.append(ls)
        fix_term_id(desc_el)
        new_root.append(desc_el)
        
    # 4. UID
    uid_el = etree.Element('uid')
    vel1 = etree.SubElement(uid_el, 'value')
    vel1.text = concept_id
    new_root.append(uid_el)
    
    # 5. TEMPLATE_ID
    tid_el = etree.Element('template_id')
    vel2 = etree.SubElement(tid_el, 'value')
    vel2.text = concept_id
    new_root.append(tid_el)
    
    # 6. CONCEPT
    con_el = etree.Element('concept')
    con_el.text = concept_id
    new_root.append(con_el)

    # 7. ADD ALL OTHERS
    # Only append definition, annotations, and component_ontologies (SNOMED, etc)
    # terminology and component_terminologies are now exploded into C_ARCHETYPE_ROOT
    for c in list(root):
        if c.tag in ['definition', 'annotations', 'component_ontologies']:
            new_root.append(c)

    # RECURSIVE FIXES
    
    # A. occurrences format
    for occ in new_root.xpath('//occurrences'):
        # convert attrs to elements
        for k in ['lower_included', 'upper_included', 'lower_unbounded', 'upper_unbounded']:
            if k in occ.attrib:
                nel = etree.Element(k)
                nel.text = occ.attrib[k]
                occ.insert(0, nel)
                del occ.attrib[k]
        # Reorder
        children = {c.tag: c for c in occ}
        for c in list(occ): occ.remove(c)
        for k in ['lower_included', 'upper_included', 'lower_unbounded', 'upper_unbounded', 'lower', 'upper']:
            if k in children: occ.append(children[k])
            
    # B. rm_type_name, node_id, rm_attribute_name to child elements
    for c in new_root.xpath('//*'):
        if c.tag in ['definition', 'children', 'attributes', 'term_definitions']:
            if c.tag == 'attributes':
                rm_val = c.get('rm_attribute_name')
                if rm_val:
                    rm_el = etree.Element('rm_attribute_name')
                    rm_el.text = rm_val
                    c.insert(0, rm_el)
                    del c.attrib['rm_attribute_name']

                # Inject existence (required by OPT 1.4)
                ext_el = etree.Element('existence')
                for k, v in [('lower_included','true'), ('upper_included','true'), 
                             ('lower_unbounded','false'), ('upper_unbounded','false')]:
                    el2 = etree.SubElement(ext_el, k)
                    el2.text = v
                lel = etree.SubElement(ext_el, 'lower')
                lel.set('{http://www.w3.org/2001/XMLSchema-instance}type', 'xs:int')
                lel.text = '0'
                uel = etree.SubElement(ext_el, 'upper')
                uel.set('{http://www.w3.org/2001/XMLSchema-instance}type', 'xs:int')
                uel.text = '1'
                c.insert(1, ext_el)

                is_mult = c.find('is_multiple')
                if is_mult is not None:
                    if is_mult.text and is_mult.text.strip().lower() == 'true':
                        c.set('{http://www.w3.org/2001/XMLSchema-instance}type', 'C_MULTIPLE_ATTRIBUTE')
                    else:
                        c.set('{http://www.w3.org/2001/XMLSchema-instance}type', 'C_SINGLE_ATTRIBUTE')
                    c.remove(is_mult)
                
                # OPT 1.4 schema strictly requires cardinality to be AFTER children
                card_el = c.find('cardinality')
                if card_el is not None:
                    c.remove(card_el)
                    c.append(card_el)
            else:
                rm_val = c.get('rm_type_name')
                nid_val = c.get('node_id')

                # Inject defaults for primitives missing AOM2 attributes
                if c.tag == 'children':
                    t = c.get('{http://www.w3.org/2001/XMLSchema-instance}type')
                    if not rm_val:
                        if t == 'C_STRING': rm_val = 'STRING'
                        elif t == 'C_INTEGER': rm_val = 'INTEGER'
                        elif t == 'C_BOOLEAN': rm_val = 'BOOLEAN'
                        elif t == 'C_TERMINOLOGY_CODE': rm_val = 'CODE_PHRASE'
                        elif t == 'C_DATE_TIME': rm_val = 'DATE_TIME'
                        elif t == 'C_DATE': rm_val = 'DATE'
                        elif t == 'C_TIME': rm_val = 'TIME'
                        elif t == 'C_DURATION': rm_val = 'DURATION'
                        elif t == 'C_REAL': rm_val = 'REAL'
                    
                    if nid_val is None:
                        nid_val = ''

                # MUST PUT THESE AS FIRST CHILDREN in exact C_OBJECT sequence
                pos = 0
                if rm_val is not None:
                    rm_el = etree.Element('rm_type_name')
                    rm_el.text = rm_val
                    c.insert(pos, rm_el)
                    pos += 1
                    if 'rm_type_name' in c.attrib: del c.attrib['rm_type_name']
                
                occ = c.find('occurrences')
                if occ is None and c.tag in ['children', 'definition']:
                    occ = etree.Element('occurrences')
                    for k, v in [('lower_included','true'), ('upper_included','true'), 
                                 ('lower_unbounded','false'), ('upper_unbounded','false')]:
                        el2 = etree.SubElement(occ, k)
                        el2.text = v
                    lel = etree.SubElement(occ, 'lower')
                    lel.set('{http://www.w3.org/2001/XMLSchema-instance}type', 'xs:int')
                    lel.text = '1'
                    uel = etree.SubElement(occ, 'upper')
                    uel.set('{http://www.w3.org/2001/XMLSchema-instance}type', 'xs:int')
                    uel.text = '1'
                    c.insert(pos, occ)
                    pos += 1
                elif occ is not None:
                    c.remove(occ)
                    c.insert(pos, occ)
                    pos += 1

                if nid_val is not None:
                    nid_el = etree.Element('node_id')
                    nid_el.text = nid_val
                    c.insert(pos, nid_el)
                    pos += 1
                    if 'node_id' in c.attrib: del c.attrib['node_id']
                    
                if c.tag == 'children':
                    t = c.get('{http://www.w3.org/2001/XMLSchema-instance}type')
                    if t == 'C_TERMINOLOGY_CODE':
                        constraint_tag = c.find('constraint')
                        if constraint_tag is not None:
                            val = constraint_tag.text or ""
                            if val.startswith('ac'):
                                c.set('{http://www.w3.org/2001/XMLSchema-instance}type', 'CONSTRAINT_REF')
                                constraint_tag.tag = 'reference'
                            elif val.startswith('[') and '::' in val:
                                # DO NOT CONVERT TO C_CODE_PHRASE! EHRbase 2 uses Archie which supports C_TERMINOLOGY_CODE.
                                pass
                            else:
                                c.set('{http://www.w3.org/2001/XMLSchema-instance}type', 'C_CODE_PHRASE')
                                c.remove(constraint_tag)
                                tid = etree.Element('terminology_id')
                                tval = etree.SubElement(tid, 'value')
                                tval.text = 'local'
                                c.append(tid)
                                clist = etree.Element('code_list')
                                clist.text = val
                                c.append(clist)
                    if not t:
                        c.set('{http://www.w3.org/2001/XMLSchema-instance}type', 'C_COMPLEX_OBJECT')

    # C. C_ARCHETYPE_ROOT precise structure
    parent_arch_id_el = tree.getroot().find('parent_archetype_id')
    parent_arch_id = parent_arch_id_el.text if parent_arch_id_el is not None else concept_id
    
    for el in new_root.xpath('//children[@xsi:type="C_ARCHETYPE_ROOT"] | //definition', namespaces={'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}):
        is_def = (el.tag == 'definition')
        
        nid_el = el.find('node_id')
        nid_val = nid_el.text if nid_el is not None else ""
        aref = el.find('archetype_ref')
        arch_val = None
        if aref is not None:
            arch_val = aref.text
            el.remove(aref)
        
        if is_def:
            arch_val = parent_arch_id
            
        if not arch_val and nid_val in mapping:
            arch_val = mapping[nid_val]
            
        rm_el = el.find('rm_type_name')
        occs = el.findall('occurrences')
        attrs = el.findall('attributes')
        # Tdefs from original node (if any)
        tdefs = el.findall('term_definitions')
        
        others = [c for c in el if c not in occs and c not in attrs and c not in tdefs and c.tag != 'node_id' and c.tag != 'rm_type_name']
        
        for c in list(el): el.remove(c)
        
        if rm_el is not None: el.append(rm_el)
        for o in occs: el.append(o)
        if nid_el is not None:
            xsi_type = el.get('{http://www.w3.org/2001/XMLSchema-instance}type')
            if xsi_type == 'C_ARCHETYPE_ROOT' or xsi_type == 'ns2:C_ARCHETYPE_ROOT' or is_def:
                nid_el.text = 'at0000'
            el.append(nid_el)
        for a in attrs: el.append(a)
        
        if arch_val:
            ael = etree.Element('archetype_id')
            vel = etree.SubElement(ael, 'value')
            vel.text = arch_val
            el.append(ael)
            
        if is_def:
            tel = etree.Element('template_id')
            tvel = etree.SubElement(tel, 'value')
            tvel.text = concept_id
            el.append(tel)
            
        for t in tdefs: el.append(t)
        
        if arch_val:
            if is_def:
                # Include both the template terminology and the parent archetype terminology
                # The template overrides at0000, so we skip at0000 from the parent
                base_key = re.sub(r'\.v\d+.*$', '', parent_arch_id)
                if base_key in term_dict:
                    for t in term_dict[base_key]:
                        if t.get('code') != 'at0000':
                            el.append(copy.deepcopy(t))
                
                # Append the template terminology
                for k in term_dict.keys():
                    if concept_id in k or k.endswith(concept_id):
                        for t in term_dict[k]:
                            el.append(copy.deepcopy(t))
                        break
            else:
                base_id = re.sub(r'\.v\d+.*$', '', arch_val)
                if base_id and base_id in term_dict:
                    for t in term_dict[base_id]:
                        el.append(copy.deepcopy(t))
                    
            # Inject the specific idX term if node_id starts with id and missing!
            if nid_val and nid_val.startswith('id') and nid_val in id_dict:
                # check if we already appended it (from term_dict)
                found = False
                for existing in el.findall('term_definitions'):
                    if existing.get('code') == 'at0000':
                        found = True
                        break
                if not found:
                    new_tdef = copy.deepcopy(id_dict[nid_val])
                    new_tdef.set('code', 'at0000')
                    el.append(new_tdef)
                    
        for ot in others: el.append(ot)

    # D. StringExpression -> string_expression
    for el in new_root.xpath('//stringExpression'):
        el.tag = 'string_expression'
        
    # E. Remove AOM2 specific elements
    aom2_types = ['binaryOperator', 'modelReference', 'operatorDefBuiltin', 'constraint', 'expressionVariable', 'functionCall', 'unaryOperator', 'expressionLeaf']
    for t in aom2_types:
        for ex in new_root.xpath(f'//*[@xsi:type="{t}"]', namespaces={'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}):
            p = ex.getparent()
            if p is not None:
                p.remove(ex)
                
    for e in new_root.xpath('//terminology_extracts|//rm_overlay|//rmOverlay'):
        p = e.getparent()
        if p is not None: p.remove(e)
        
    # F. Map stringExpression attributes back
    # But string_expression has none?
    
    # CLEANUP: Remove empty attributes (which lacked children due to attributeTuples in AOM2)
    # as OPT 1.4 parser in EHRbase requires them to be omitted if unconstrained.
    for el in list(new_root.iter('attributes')):
        if len(list(el.iter('children'))) == 0:
            p = el.getparent()
            if p is not None:
                p.remove(el)

    # RE-APPLY NAMESPACES
    for el in new_root.iter():
        if '}' not in el.tag:
            el.tag = f'{{{ns2}}}{el.tag}'
        
    tree._setroot(new_root)

    # Assign correct nsmap at root so the output uses xmlns= instead of explicit prefixes
    etree.cleanup_namespaces(tree, top_nsmap={None: ns2, 'xsi': 'http://www.w3.org/2001/XMLSchema-instance'})
    
    with open(output_opt, 'wb') as f:
        tree.write(f, encoding='utf-8', xml_declaration=True, pretty_print=False)
    print("SUCCESS")

if __name__ == '__main__':
    import glob
    import shutil
    if len(sys.argv) == 3:
        input_dir = sys.argv[1]
        templates_dir = sys.argv[2]
        for opt_file in sorted(os.listdir(input_dir)):
            if opt_file.endswith('.opt') and not opt_file.endswith('.bak'):
                opt_path = os.path.join(input_dir, opt_file)
                bak_path = opt_path + '.bak'
                shutil.move(opt_path, bak_path)
                template_id = opt_file.replace('.opt', '')
                adlt_path = os.path.join(templates_dir, template_id + '.adlt')
                if os.path.exists(adlt_path):
                    try:
                        convert_aom2_to_opt14(bak_path, opt_path, adlt_path)
                    except Exception as e:
                        print(f"Error on {opt_file}: {e}")
                else:
                    print(f"No adlt template for {opt_file}")
    elif len(sys.argv) == 4:
        convert_aom2_to_opt14(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print("Usage: python3 fix_opt14.py <opts_dir> <templates_dir>")
        sys.exit(1)
