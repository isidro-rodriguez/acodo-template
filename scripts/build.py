"""Compila un binario en fichero único mediante PyInstaller.

Uso:
    uv run --group build python scripts/build.py

Genera:
    Windows: build/<paquete>.exe
    Linux/macOS: build/<paquete>

El nombre del paquete se toma del directorio ``src/<paquete>``. Incluye el
icono desde ``<paquete>/resources`` y valida que el nombre sea seguro como
nombre de fichero en Windows.
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

_INVALID_WINDOWS_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
"""Caracteres no permitidos por Windows en nombres de archivo."""

_RESERVED_WINDOWS_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}
"""Nombres reservados por Windows."""


def discover_package_name(src: Path) -> str:
    """Obtiene el nombre del único paquete Python situado en `src`.

    Args:
        src: Directorio que contiene el paquete (layout ``src``).

    Returns:
        El nombre del directorio del paquete.

    Raises:
        SystemExit: Si no hay exactamente un paquete en `src`.
    """
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
    """Devuelve la ruta del icono apropiado para la plataforma actual.

    Args:
        resources: Directorio `resources` del paquete que contiene los iconos.

    Returns:
        Ruta al icono correspondiente a la plataforma.
    """
    filename = "icon.ico" if sys.platform == "win32" else "icon.png"
    return resources / filename


def get_executable_name(package_name: str) -> str:
    """Devuelve el nombre del ejecutable generado para la plataforma actual.

    Args:
        package_name: Nombre del paquete, usado como base del ejecutable.

    Returns:
        ``"<package_name>.exe"`` en Windows, ``"<package_name>"`` en el resto.
    """
    if sys.platform == "win32":
        return f"{package_name}.exe"

    return package_name


def main() -> None:
    """Compila el paquete como ejecutable standalone con PyInstaller.

    Raises:
        SystemExit: Si el nombre no es válido, falta el punto de entrada o el
            icono, o no se produce el binario esperado.
        subprocess.CalledProcessError: Si PyInstaller termina con error.
    """
    entry = SRC / PACKAGE_NAME / "main.py"
    icon = get_icon(SRC / PACKAGE_NAME / "resources")
    executable_name = get_executable_name(PACKAGE_NAME)

    output_dir = ROOT / "build" / "_pyinstaller"
    final_path = ROOT / "build" / executable_name

    if not entry.exists():
        raise SystemExit(f"No se encontró el punto de entrada: {entry}")

    if not icon.exists():
        raise SystemExit(f"No se encontró el icono: {icon}")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--noconfirm",
        "--clean",
        "--name",
        PACKAGE_NAME,
        "--console",
        f"--collect-all={PACKAGE_NAME}",
        f"--paths={SRC}",
        f"--distpath={output_dir / 'dist'}",
        f"--workpath={output_dir / 'work'}",
        f"--specpath={output_dir / 'spec'}",
        f"--icon={icon}",
        str(entry),
    ]

    print(f"Plataforma: {sys.platform}")
    print(f"Paquete:    {PACKAGE_NAME}")
    print(f"Icono:      {icon}")
    print("Compilando con PyInstaller... (esto puede tardar algunos minutos)")

    subprocess.run(cmd, check=True)

    produced = output_dir / "dist" / executable_name

    if not produced.exists():
        raise SystemExit(f"No se encontró {produced}. Revisa la salida de PyInstaller.")

    final_path.parent.mkdir(parents=True, exist_ok=True)
    produced.replace(final_path)
    print(f"Listo: {final_path}")


if __name__ == "__main__":
    main()
