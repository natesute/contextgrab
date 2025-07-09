import argparse
import os
from pathlib import Path
from typing import List

import nbformat
import pyperclip
from nbformat import NotebookNode
from pathspec import PathSpec


def load_gitignore(start: Path) -> PathSpec:
    """Load `.gitignore` patterns by searching upwards from ``start``."""
    patterns: list[str] = []
    current = start
    while True:
        gitignore = current / ".gitignore"
        if gitignore.exists():
            patterns.extend(gitignore.read_text().splitlines())
        if current.parent == current:
            break
        current = current.parent
    return PathSpec.from_lines("gitwildmatch", patterns)


def should_ignore(path: Path, spec: PathSpec, base: Path) -> bool:
    try:
        rel = path.relative_to(base)
    except ValueError:
        return False
    return spec.match_file(str(rel))


def read_file(path: Path) -> str:
    return path.read_text()


def read_notebook(path: Path, include_outputs: bool = False) -> str:
    nb = nbformat.read(path, as_version=4)
    parts: List[str] = []
    for cell in nb.cells:
        if cell.cell_type == 'markdown':
            parts.append(cell.source)
        elif cell.cell_type == 'code':
            parts.append(cell.source)
            if include_outputs:
                for out in cell.get('outputs', []):
                    text = extract_output_text(out)
                    if text:
                        parts.append(text)
    return '\n'.join(parts)


def extract_output_text(output: NotebookNode) -> str:
    if output.output_type == 'stream':
        return output.get('text', '')
    if output.output_type in {'execute_result', 'display_data'}:
        data = output.get('data', {})
        if 'text/plain' in data:
            return data['text/plain']
    if output.output_type == 'error':
        return '\n'.join(output.get('traceback', []))
    return ''


def walk_directory(path: Path, include_outputs: bool = False) -> str:
    spec = load_gitignore(path)
    lines = [f"FOLDER: {path.name}"]
    for root, _, files in os.walk(path):
        root_path = Path(root)
        for fname in sorted(files):
            file_path = root_path / fname
            if should_ignore(file_path, spec, path):
                continue
            rel = file_path.relative_to(path)
            lines.append(f"=== {rel} ===")
            if file_path.suffix == '.ipynb':
                lines.append(read_notebook(file_path, include_outputs))
            else:
                try:
                    lines.append(read_file(file_path))
                except UnicodeDecodeError:
                    # skip binary files
                    continue
    return '\n'.join(lines)


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description='Copy file or folder contents')
    parser.add_argument('path', help='File or directory to copy')
    parser.add_argument('--include-outputs', action='store_true', help='Include notebook outputs')
    parser.add_argument('--stdout', action='store_true', help='Print to stdout instead of copying')
    args = parser.parse_args(argv)

    target = Path(args.path).resolve()
    if target.is_dir():
        text = walk_directory(target, args.include_outputs)
    elif target.is_file():
        header = f"FILE: {target.name}"
        if target.suffix == '.ipynb':
            body = read_notebook(target, args.include_outputs)
        else:
            body = read_file(target)
        text = f"{header}\n{body}"
    else:
        raise SystemExit(f"Path not found: {target}")

    if args.stdout:
        print(text)
        return
    try:
        pyperclip.copy(text)
        print('Copied to clipboard.')
    except pyperclip.PyperclipException:
        print(text)

if __name__ == '__main__':
    main()
