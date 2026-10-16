"""Compila un binario mediante PyInstaller.

Uso:
    uv run --group build python scripts/build.py
    uv run --group build python scripts/build.py --onefile --output dist
    uv run --group build python scripts/build.py --no-icon

Genera:
    Windows: <output>/<paquete>.exe
    Linux/macOS: <output>/<paquete>

El nombre del paquete se toma del directorio ``src/<paquete>``. Incluye el
icono desde ``<paquete>/resources`` y valida que el nombre sea seguro como
nombre de fichero en Windows.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Annotated, NoReturn

import typer
from irg_utils import valid_filename
from rich.console import Console

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

app = typer.Typer(add_completion=False)
console = Console()
err_console = Console(stderr=True)


def _fail(message: str) -> NoReturn:
    """Imprime un error y aborta con código 1."""
    err_console.print(f"[bold red]Error:[/] {message}")
    raise typer.Exit(code=1)


def discover_package_name(src: Path) -> str:
    """Obtiene el nombre del único paquete Python situado en `src`."""
    packages = sorted(
        path.name for path in src.iterdir() if (path / "__init__.py").is_file()
    )

    if len(packages) != 1:
        found = ", ".join(packages) or "ninguno"
        raise SystemExit(
            f"Se esperaba exactamente un paquete en {src} (encontrados: {found})."
        )

    return packages[0]


PACKAGE_NAME = discover_package_name(SRC)
"""Nombre del paquete, tomado del directorio ``src/<paquete>``."""


def get_icon(resources: Path) -> Path:
    """Devuelve la ruta del icono apropiado para la plataforma actual."""
    filename = "icon.ico" if sys.platform == "win32" else "icon.png"
    return resources / filename


def get_executable_name(package_name: str) -> str:
    """Devuelve el nombre del ejecutable generado para la plataforma actual."""
    if sys.platform == "win32":
        return f"{package_name}.exe"

    return package_name


# =============================================================================
#  Opciones de Typer
# =============================================================================

OutputOption = Annotated[
    Path,
    typer.Option(
        "--output",
        "-o",
        file_okay=False,
        resolve_path=True,
        help="Directorio de salida del compilado (por defecto build).",
    ),
]

OneFileOption = Annotated[
    bool,
    typer.Option(
        "--onefile",
        help="Empaquetar en un único fichero ejecutable.",
    ),
]

NoIconOption = Annotated[
    bool,
    typer.Option(
        "--no-icon",
        help="Empaquetar sin icono.",
    ),
]


# =============================================================================
#  Comandos de Typer
# =============================================================================


@app.command()
def main(
    output: OutputOption = Path("build"),
    onefile: OneFileOption = False,
    no_icon: NoIconOption = False,
) -> None:
    """Compila el paquete como ejecutable con PyInstaller."""
    if not valid_filename(PACKAGE_NAME):
        _fail(f"Nombre de paquete inválido para Windows: {PACKAGE_NAME}")

    entry = SRC / PACKAGE_NAME / "main.py"
    executable_name = get_executable_name(PACKAGE_NAME)

    output_dir = (ROOT / output).resolve() if not output.is_absolute() else output
    pyinstaller_dir = output_dir / "_pyinstaller"
    final_path = output_dir / executable_name

    if not entry.exists():
        _fail(f"No se encontró el punto de entrada: {entry}")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--name",
        PACKAGE_NAME,
        "--console",
        f"--collect-all={PACKAGE_NAME}",
        f"--paths={SRC}",
        f"--distpath={pyinstaller_dir / 'dist'}",
        f"--workpath={pyinstaller_dir / 'work'}",
        f"--specpath={pyinstaller_dir / 'spec'}",
    ]

    if onefile:
        cmd.append("--onefile")

    if not no_icon:
        icon = get_icon(SRC / PACKAGE_NAME / "resources")
        if not icon.exists():
            _fail(f"No se encontró el icono: {icon}")
        cmd.append(f"--icon={icon}")
        console.print(f"Icono:      {icon}")

    cmd.append(str(entry))

    console.print(f"Plataforma: {sys.platform}")
    console.print(f"Paquete:    {PACKAGE_NAME}")
    console.print("Compilando con PyInstaller... (esto puede tardar algunos minutos)")

    subprocess.run(cmd, check=True)

    produced = pyinstaller_dir / "dist" / executable_name

    if not produced.exists():
        _fail(f"No se encontró {produced}. Revisa la salida de PyInstaller.")

    output_dir.mkdir(parents=True, exist_ok=True)
    produced.replace(final_path)
    console.print(f"[green]✓[/] Listo: {final_path}")


if __name__ == "__main__":
    app()
