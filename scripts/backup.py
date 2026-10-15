"""Copia de seguridad manual.

Limpia cachés `__pycache__` y comprime el código fuente en
`.local/backup.<extensión>` (zip por defecto; también tar.gz).

Uso:
    uv run python scripts/backup.py
    uv run python scripts/backup.py --archiver tar.gz
    uv run python scripts/backup.py -f ~/copias/pyplate.zip
"""

import shutil
import tarfile
import zipfile
from enum import StrEnum
from pathlib import Path
from typing import Annotated, NoReturn

import typer
from rich.console import Console
from rich.table import Table

ROOT = Path(__file__).resolve().parents[1]
BACKUP_DIR = ROOT / ".local"
"""Directorio de salida por defecto."""

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


class Archiver(StrEnum):
    """Formatos de compresión admitidos."""

    ZIP = "zip"
    TAR_GZ = "tar.gz"


app = typer.Typer(add_completion=False)
console = Console()
err_console = Console(stderr=True)


def _fail(message: str) -> NoReturn:
    """Imprime un error y aborta con código 1."""
    err_console.print(f"[bold red]Error:[/] {message}")
    raise typer.Exit(code=1)


def _clean_pycache() -> int:
    """Borra los `__pycache__` de `DIRS` (sin tocar `.venv`). Devuelve el total."""
    removed = 0
    for dir_name in DIRS:
        for cache_dir in (ROOT / dir_name).rglob("__pycache__"):
            if cache_dir.is_dir():
                shutil.rmtree(cache_dir)
                removed += 1
    return removed


def _collect_files() -> list[Path]:
    """Devuelve, ordenados y sin duplicados, los ficheros a incluir (relativos)."""
    found: set[Path] = set()
    for dir_name in DIRS:
        found.update(f for f in (ROOT / dir_name).rglob("*") if f.is_file())
    for pattern in ROOT_PATTERNS:
        found.update(f for f in ROOT.glob(pattern) if f.is_file())
    return sorted(f.relative_to(ROOT) for f in found)


def _write_zip(output: Path, files: list[Path]) -> None:
    """Crea un zip con `files` (rutas relativas a `ROOT`)."""
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in files:
            zf.write(ROOT / file, file)


def _write_tar_gz(output: Path, files: list[Path]) -> None:
    """Crea un tar.gz con `files` (rutas relativas a `ROOT`)."""
    with tarfile.open(output, "w:gz") as tf:
        for file in files:
            tf.add(ROOT / file, arcname=file.as_posix(), recursive=False)


def _write_archive(archiver: Archiver, output: Path, files: list[Path]) -> None:
    """Crea el archivo comprimido en el formato elegido."""
    match archiver:
        case Archiver.ZIP:
            _write_zip(output, files)
        case Archiver.TAR_GZ:
            _write_tar_gz(output, files)


# =============================================================================
#  Opciones de Typer
# =============================================================================


FileOption = Annotated[
    Path | None,
    typer.Option(
        "--file",
        "-f",
        dir_okay=False,
        resolve_path=True,
        help="Ruta del fichero de salida (por defecto .local/backup.<formato>).",
    ),
]

ArchiverOption = Annotated[
    Archiver,
    typer.Option(
        "--archiver",
        "-a",
        case_sensitive=False,
        help="Formato de compresión.",
    ),
]


# =============================================================================
#  Comandos de Typer
# =============================================================================


@app.command()
def main(
    file: FileOption = None,
    archiver: ArchiverOption = Archiver.ZIP,
) -> None:
    """Limpia las cachés, crea la copia de seguridad e informa del resultado.

    Args:
        file: Ruta del fichero de salida. Si se omite, `.local/backup.<formato>`.
        archiver: Formato de compresión. 7z requiere 7-Zip instalado.
    """
    output = (file or BACKUP_DIR / f"backup.{archiver.value}").resolve()

    with console.status("Limpiando cachés __pycache__..."):
        removed = _clean_pycache()
    console.print(f"[green]✓[/] {removed} directorios __pycache__ eliminados")

    files = _collect_files()
    if output in {(ROOT / f).resolve() for f in files}:
        _fail(f"La ruta de salida coincide con un fichero del proyecto: {output}")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.unlink(missing_ok=True)
    with console.status(f"Comprimiendo {len(files)} ficheros ({archiver.value})..."):
        _write_archive(archiver, output, files)

    table = Table(title="Copia de seguridad creada", show_header=False)
    table.add_column(style="bold")
    table.add_column(overflow="fold")
    table.add_row("Formato", archiver.value)
    table.add_row("Ficheros", str(len(files)))
    table.add_row("Tamaño", f"{output.stat().st_size:,} bytes")
    table.add_row("Ruta", str(output))
    console.print(table)


if __name__ == "__main__":
    app()
