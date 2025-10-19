import os, sys, glob, yaml

def main():
    base = os.path.join(os.path.dirname(__file__), '..', 'crossbring-kafka-gitops-blueprints', 'argo', 'applications')
    files = glob.glob(os.path.join(base, '*.yaml'))
    missing = []
    for fn in files:
        with open(fn, 'r', encoding='utf-8') as f:
            app = yaml.safe_load(f)
        path = app.get('spec', {}).get('source', {}).get('path')
        if not path:
            continue
        if not os.path.isdir(path):
            missing.append((os.path.relpath(fn), path))
    if missing:
        print('Missing paths:')
        for app_fn, p in missing:
            print(f"- {app_fn} -> {p}")
        sys.exit(1)
    print('All Argo application source paths exist.')

if __name__ == '__main__':
    main()

