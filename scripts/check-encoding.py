from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE_PARTS = {'node_modules', 'dist', 'backups', '.npm-cache', '__pycache__'}
TEXT_SUFFIXES = {
    '.js', '.vue', '.css', '.json', '.md', '.html', '.bat', '.py', '.txt', '.yml', '.yaml'
}
EXTRA_NAMES = {'.gitignore', '.editorconfig', '.gitattributes'}
UTF8_BOM = bytes.fromhex('efbbbf')


def iter_project_files() -> list[Path]:
    files = []
    for path in ROOT.rglob('*'):
        if not path.is_file():
            continue
        if any(part in EXCLUDE_PARTS for part in path.parts):
            continue
        if path.name in EXTRA_NAMES or path.suffix.lower() in TEXT_SUFFIXES:
            files.append(path)
    return sorted(files)


def main() -> int:
    parser = argparse.ArgumentParser(description='Check project text files for UTF-8 without BOM.')
    parser.add_argument('--fix-bom', action='store_true', help='Rewrite UTF-8 BOM files as UTF-8 without BOM.')
    args = parser.parse_args()

    issues: list[str] = []
    fixed: list[str] = []
    scanned = 0

    for path in iter_project_files():
        scanned += 1
        data = path.read_bytes()
        rel = path.relative_to(ROOT)

        if data.startswith(UTF8_BOM):
            if args.fix_bom:
                text = data.decode('utf-8-sig')
                path.write_bytes(text.encode('utf-8'))
                fixed.append(str(rel))
                data = path.read_bytes()
            else:
                issues.append(f'{rel}: contains UTF-8 BOM')

        try:
            data.decode('utf-8')
        except UnicodeDecodeError as exc:
            issues.append(f'{rel}: not valid UTF-8 (byte {exc.start})')

    print(f'Scanned {scanned} files.')
    if fixed:
        print('Removed BOM from:')
        for item in fixed:
            print(f'  {item}')

    if issues:
        print('Encoding issues found:')
        for item in issues:
            print(f'  {item}')
        return 1

    print('All scanned project files are UTF-8 without BOM.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
