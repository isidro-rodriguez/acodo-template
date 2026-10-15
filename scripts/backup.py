"""Copia de seguridad manual.

Limpia cachés `__pycache__` y comprime el código fuente en un zip
ubicado en `.local/backup.zip`.

Uso:
    uv run python scripts/backup.py
"""

import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKUP_DIR = ROOT / ".local"
BACKUP_PATH = BACKUP_DIR / "backup.zip"
"""Ruta de salida del backup comprimido."""

DIRS = [
    ".github",
    "scripts",
    "src",
    "tests",
]
"""Directorios cuya estructura se incluye completa."""

ROOT_PATTERNS = [
    "*.toml",
    "*.md",
    "*.lock",
    "*.py",
    "*.yaml",
    "LICENSE",
    ".gitignore",
    ".gitattributes",
    ".python-version",
]
"""Ficheros en raíz a incluir."""


def _clean_pycache() -> int:
    """Borra los `__pycache__` de `DIRS` (sin tocar `.venv`). Devuelve el total."""
    removed = 0
    for dir_name in DIRS:
        for cache_dir in (ROOT / dir_name).rglob("__pycache__"):
            if cache_dir.is_dir():
                shutil.rmtree(cache_dir)
                removed += 1
    return removed


def _zip() -> None:
    """Crea el zip con los directorios y los ficheros de raíz seleccionados."""
    with zipfile.ZipFile(BACKUP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for dir_name in DIRS:
            for file in (ROOT / dir_name).rglob("*"):
                if file.is_file():
                    zf.write(file, file.relative_to(ROOT))

        for pattern in ROOT_PATTERNS:
            for file in ROOT.glob(pattern):
                if file.is_file():
                    zf.write(file, file.relative_to(ROOT))


def main() -> None:
    """Limpia las cachés, crea la copia de seguridad e informa del resultado."""
    print("Limpiando cachés __pycache__...")
    print(f"  {_clean_pycache()} directorios __pycache__ eliminados")

    print("Creando copia de seguridad...")
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    _zip()

    size = BACKUP_PATH.stat().st_size
    print(f"  {BACKUP_PATH} ({size:,} bytes)")


if __name__ == "__main__":
    main()
