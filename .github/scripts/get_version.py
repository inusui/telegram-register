import re

with open("info.py") as f:
    content = f.read()

match = re.search(r'VERSION\s*=\s*["\']([^"\']+)["\']', content)
if not match:
    raise SystemExit("ERROR: No se encontró VERSION en info.py")

print(match.group(1))
