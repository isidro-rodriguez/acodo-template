"""Herramientas de desarrollo del proyecto.

Reúne en una sola CLI los scripts de `scripts/`, la documentación de la API y
las comprobaciones de calidad.

Uso:
    uv run dev.py --help
    uv run dev.py check
    uv run dev.py check --lint --types
    uv run dev.py api
    uv run dev.py backup --archiver tar.gz
    uv run dev.py gh-token access
"""

import importlib.util
import shutil
import subprocess
import sys
import time
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Annotated, NoReturn

import typer
from rich.console import Console
from rich.table import Table

ROOT = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"
SRC = ROOT / "src"


@dataclass(frozen=True, slots=True)
class Step:
    """Comprobación de calidad: nombre visible y comando a ejecutar."""

    name: str
    command: tuple[str, ...]


STEPS = {
    "format": Step("ruff format", (sys.executable, "-m", "ruff", "format")),
    "lint": Step("ruff check", (sys.executable, "-m", "ruff", "check", "--fix")),
    "types": Step("ty check", (sys.executable, "-m", "ty", "check")),
    "tests": Step("pytest", (sys.executable, "-m", "pytest")),
}
"""Comprobaciones disponibles, en el orden en que se ejecutan."""


def _load_script(name: str) -> ModuleType:
    """Importa `scripts/<name>.py` (`scripts` no es un paquete)."""
    module_name = f"dev_scripts_{name}"
    spec = importlib.util.spec_from_file_location(module_name, SCRIPTS / f"{name}.py")
    if spec is None or spec.loader is None:
        raise ImportError(f"No se pudo cargar el script {name!r}.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


backup = _load_script("backup")
build = _load_script("build")
code_count = _load_script("code_count")
gh_token = _load_script("gh_token")

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Herramientas de desarrollo del proyecto.",
)
console = Console()
err_console = Console(stderr=True)

app.command("backup")(backup.main)
app.command("build")(build.main)
app.command("code-count")(code_count.main)
app.add_typer(
    gh_token.app,
    name="gh-token",
    help="Genera tokens de instalación de una GitHub App.",
)


# =============================================================================
#  Utilidades
# =============================================================================


def _fail(message: str) -> NoReturn:
    """Imprime un error y aborta con código 1."""
    err_console.print(f"[bold red]Error:[/] {message}")
    raise typer.Exit(code=1)


def _run(command: Sequence[str]) -> int:
    """Ejecuta `command` en la raíz del proyecto y devuelve su código de salida."""
    return subprocess.run(command, cwd=ROOT, check=False).returncode


# =============================================================================
#  Opciones de Typer
# =============================================================================


ApiOutputOption = Annotated[
    Path | None,
    typer.Option(
        "--output",
        "-o",
        file_okay=False,
        resolve_path=True,
        help="Genera el HTML en este directorio en vez de abrir el navegador.",
    ),
]

ApiPathOption = Annotated[
    Path | None,
    typer.Option(
        "--path",
        "-p",
        exists=True,
        resolve_path=True,
        help="Paquete o módulo a documentar (por defecto src/<paquete>).",
    ),
]

FormatOption = Annotated[
    bool,
    typer.Option(
        "--format",
        help="Formatea el código (ruff format).",
    ),
]

LintOption = Annotated[
    bool,
    typer.Option(
        "--lint",
        help="Revisa y autocorrige el lint (ruff check).",
    ),
]

TestOption = Annotated[
    bool,
    typer.Option(
        "--tests",
        help="Ejecuta las pruebas (pytest).",
    ),
]

TypesOption = Annotated[
    bool,
    typer.Option(
        "--types",
        help="Comprueba el tipado (ty check).",
    ),
]


# =============================================================================
#  Comandos de Typer
# =============================================================================


@app.command()
def check(
    format_: FormatOption = False,
    lint: LintOption = False,
    types: TypesOption = False,
    tests: TestOption = False,
) -> None:
    """Ejecuta las comprobaciones de calidad; sin opciones, todas."""
    flags = {"format": format_, "lint": lint, "types": types, "tests": tests}
    selected = [key for key, enabled in flags.items() if enabled] or list(STEPS)

    results: list[tuple[Step, int, float]] = []
    for key in selected:
        step = STEPS[key]
        console.rule(f"[bold]{step.name}")
        start = time.perf_counter()
        code = _run(step.command)
        results.append((step, code, time.perf_counter() - start))

    table = Table(title="Resultado", title_style="dim", border_style="dim")
    table.add_column("Comprobación", style="cyan")
    table.add_column("Estado")
    table.add_column("Tiempo", justify="right")
    for step, code, seconds in results:
        status = "[green]✓ OK[/]" if code == 0 else f"[bold red]✗ código {code}[/]"
        table.add_row(step.name, status, f"{seconds:.1f} s")
    console.print(table)

    if any(code != 0 for _, code, _ in results):
        raise typer.Exit(code=1)


@app.command()
def api(
    path: ApiPathOption = None,
    output: ApiOutputOption = None,
) -> None:
    """Muestra la documentación de la API con pdoc (docstrings estilo Google)."""
    uv = shutil.which("uv")
    if uv is None:
        _fail("No se encontró `uv` en el PATH.")

    target = path or SRC / build._discover_package_name(SRC)
    command = [uv, "run", "--with", "pdoc", "pdoc", "-d", "google"]
    if output is not None:
        command += ["-o", str(output)]
    command.append(str(target))

    try:
        code = _run(command)
    except KeyboardInterrupt:  # Ctrl-C cierra el servidor de pdoc.
        raise typer.Exit(code=0) from None
    if code != 0:
        raise typer.Exit(code=code)
    if output is not None:
        console.print(f"[green]✓[/] Documentación generada en {output}")


if __name__ == "__main__":
    app()
