"""Synchronize generated version consumers from pyproject.toml."""

from __future__ import annotations

from pathlib import Path
import re
import tomllib

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT_PATH = ROOT / "pyproject.toml"
INNO_SCRIPT_PATH = ROOT / "installer" / "FloatNotes.iss"
VERSION_PATTERN = re.compile(r'(#define\s+MyAppVersion\s+")([^"]+)(")')


def get_project_version() -> str:
    """Read the single project version from pyproject.toml."""
    with PYPROJECT_PATH.open("rb") as pyproject_file:
        pyproject = tomllib.load(pyproject_file)
    version = pyproject.get("project", {}).get("version")
    if not isinstance(version, str) or not version.strip():
        raise RuntimeError("Missing [project].version in pyproject.toml.")
    return version.strip()


def sync_inno_script(version: str) -> bool:
    """Update the Inno Setup script version define when needed."""
    script = INNO_SCRIPT_PATH.read_text(encoding="utf-8")
    updated, replacements = VERSION_PATTERN.subn(rf"\g<1>{version}\g<3>", script, count=1)
    if replacements != 1:
        raise RuntimeError(f"Could not find MyAppVersion in {INNO_SCRIPT_PATH}.")
    if updated == script:
        return False
    INNO_SCRIPT_PATH.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    version = get_project_version()
    changed = sync_inno_script(version)
    status = "updated" if changed else "already current"
    print(f"FloatNotes version {version}: installer script {status}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
