import sys, json

def extract_paths(node, current_path=""):
    paths = {}
    
    # If this node has a valid id and it's not the root, append it to the path
    node_id = node.get('id', '')
    if current_path == "":
        new_path = node_id
    else:
        new_path = current_path + "/" + node_id

    # If this is a data node, it has a type (like DV_CODE_PHRASE, DV_TEXT)
    rm_type = node.get('rmType', '')
    if rm_type.startswith('DV_'):
        paths[new_path] = rm_type
        
    # Recurse into children
    if 'children' in node:
        for child in node['children']:
            child_paths = extract_paths(child, new_path)
            paths.update(child_paths)
            
    return paths

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python dump_flat_paths.py <webtemplate.json>")
        sys.exit(1)
        
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
        
    paths = extract_paths(data.get('tree', {}))
    for p, t in paths.items():
        print(f"{p} : {t}")
