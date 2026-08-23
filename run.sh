#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

for python_bin in "$project_dir/.venv/bin/python" "$project_dir/venv/bin/python" python3 python; do
    if [[ "$python_bin" == */* && ! -x "$python_bin" ]]; then
        continue
    fi
    if "$python_bin" -c 'import PySide6' >/dev/null 2>&1; then
        exec "$python_bin" "$project_dir/AyoSort.py" "$@"
    fi
done

echo "AyoSORT requires Python with PySide6. Run: python3 -m pip install -r requirements.txt" >&2
exit 1
