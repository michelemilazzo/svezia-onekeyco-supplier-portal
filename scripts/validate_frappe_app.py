import json
import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'supplier_portal_app'
INNER = APP / 'supplier_portal_app'

REQUIRED_FILES = [
    ROOT / 'pyproject.toml',
    ROOT / 'README.md',
    APP / '__init__.py',
    APP / 'hooks.py',
    APP / 'modules.txt',
]


def fail(message):
    raise SystemExit(f'VALIDATION FAILED: {message}')


def check_required_files():
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if not path.exists()]
    if missing:
        fail('Missing files: ' + ', '.join(missing))


def check_python_syntax():
    for path in APP.rglob('*.py'):
        py_compile.compile(str(path), doraise=True)


def check_doctype_json():
    doctype_dirs = [APP / 'doctype', INNER / 'doctype']
    files = []
    for folder in doctype_dirs:
        if folder.exists():
            files.extend(folder.rglob('*.json'))
    if not files:
        fail('No DocType JSON files found')
    for path in files:
        data = json.loads(path.read_text())
        if not data.get('doctype') and not data.get('name'):
            fail(f'{path.relative_to(ROOT)} missing doctype/name')
        module = data.get('module')
        if module and module != 'Supplier Portal App':
            fail(f'{path.relative_to(ROOT)} wrong module: {module}')


def main():
    check_required_files()
    check_python_syntax()
    check_doctype_json()
    print('Frappe app validation OK')


if __name__ == '__main__':
    main()
