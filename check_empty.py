import sys
from lxml import etree
ns = {"ns": "http://schemas.openehr.org/v1", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
for f in sys.argv[1:]:
    tree = etree.parse(f)
    attrs = tree.xpath("//ns:attributes", namespaces=ns)
    for a in attrs:
        children = a.xpath("./ns:children", namespaces=ns)
        if len(children) == 0:
            print("Empty attributes found in", f)
            print("Line:", a.sourceline)
            print("Parent:", a.getparent().tag)
            rmel = a.find("./ns:rm_attribute_name", namespaces=ns)
            print("RM attr:", rmel.text if rmel is not None else "None")
