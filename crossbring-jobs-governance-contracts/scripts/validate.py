import os, sys, yaml

REQUIRED_TOP_LEVEL = {"name", "version", "owner", "schema"}
REQUIRED_FIELDS = {"job_id", "title", "employer_name"}

def load(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def validate(contract):
    missing = REQUIRED_TOP_LEVEL - set(contract.keys())
    if missing:
        return False, f"missing top-level: {missing}"
    fields = {f["name"] for f in contract["schema"].get("fields", [])}
    mf = REQUIRED_FIELDS - fields
    if mf:
        return False, f"missing fields: {mf}"
    return True, "ok"

def main():
    base = os.path.join(os.path.dirname(__file__), "..", "contracts")
    ok = True
    for fn in os.listdir(base):
        if not fn.endswith(('.yaml', '.yml')):
            continue
        path = os.path.join(base, fn)
        c = load(path)
        valid, msg = validate(c)
        print(f"{fn}: {msg}")
        ok = ok and valid
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()

