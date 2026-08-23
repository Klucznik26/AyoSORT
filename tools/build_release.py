#!/usr/bin/env python3
import argparse
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INCLUDED_FILES = {
    "AyoSort.py",
    "README.md",
    "requirements.txt",
    "pyproject.toml",
    "run.sh",
}
INCLUDED_DIRECTORIES = {"assets", "config", "core", "gui", "i18n", "screenshots"}
EXCLUDED_PARTS = {".git", ".pytest_cache", ".ruff_cache", "__pycache__", ".venv", "venv", "dist", "build"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".zip"}


def release_files():
    for path in sorted(PROJECT_ROOT.rglob("*")):
        relative = path.relative_to(PROJECT_ROOT)
        if not path.is_file() or any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        if path.suffix.lower() in EXCLUDED_SUFFIXES:
            continue
        if relative.as_posix() in INCLUDED_FILES or relative.parts[0] in INCLUDED_DIRECTORIES:
            yield path, relative


def build_archive(version: str) -> Path:
    output_dir = PROJECT_ROOT / "dist"
    output_dir.mkdir(parents=True, exist_ok=True)
    archive_path = output_dir / f"AyoSORT-{version}.zip"
    root_name = f"AyoSORT-{version}"
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for source, relative in release_files():
            archive.write(source, Path(root_name) / relative)
    return archive_path


def main():
    parser = argparse.ArgumentParser(description="Build a clean AyoSORT release archive")
    parser.add_argument("--version", default="1.8.1")
    args = parser.parse_args()
    archive = build_archive(args.version)
    print(archive)


if __name__ == "__main__":
    main()
