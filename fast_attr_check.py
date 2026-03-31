import sys

def check_empty_attrs(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all <attributes> ... </attributes>
    import re
    # .*? non greedy
    matches = re.finditer(r'<attributes\b[^>]*>(.*?)</attributes>', content, flags=re.DOTALL)
    for m in matches:
        inner = m.group(1)
        if '<children' not in inner:
            print(f"File {filepath} has attributes without children! Content inside:\n{inner[:200]}")
            return

    print(f"All good: {filepath}")

for path in sys.argv[1:]:
    check_empty_attrs(path)
