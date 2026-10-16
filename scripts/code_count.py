"""Conteo de líneas de código y docstrings.

Cuenta las líneas efectivas separando el código fuente de los docstrings,
excluyendo líneas en blanco y comentarios ordinarios (#).

Uso:
    uv run python scripts/code_count.py
    uv run python scripts/code_count.py --verbose
    uv run python scripts/code_count.py -v
    uv run python scripts/code_count.py --tree
    uv run python scripts/code_count.py -t
    uv run python scripts/code_count.py --verbose --tree
"""

import ast
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, Self

import typer
from rich.console import Console
from rich.table import Table
from rich.tree import Tree

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

CODE_EXTENSIONS = {".py"}

app = typer.Typer(add_completion=False)
console = Console()
err_console = Console(stderr=True)


@dataclass(slots=True)
class LineStats:
    """Métricas de código y docstrings para un fichero o categoría."""

    code: int = 0
    docstrings: int = 0

    @property
    def total(self) -> int:
        """Suma total de líneas efectivas (código + docstrings)."""
        return self.code + self.docstrings

    def __add__(self, other: Self) -> Self:
        """Suma las métricas de dos conteos."""
        return LineStats(
            code=self.code + other.code,
            docstrings=self.docstrings + other.docstrings,
        )


@dataclass
class Category:
    """Grupo de ficheros con sus métricas de código y docstrings."""

    name: str
    files: list[tuple[Path, LineStats]] = field(default_factory=list)

    @property
    def totals(self) -> LineStats:
        """Suma acumulada de todas las métricas de la categoría."""
        stats = LineStats()
        for _, file_stats in self.files:
            stats += file_stats
        return stats


def _extract_docstring_range(node: ast.AST) -> range | None:
    """Extrae el rango de líneas (1-indexed) de un docstring si el nodo lo posee."""
    if not isinstance(
        node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
    ):
        return None

    if not node.body:
        return None

    first_stmt = node.body[0]
    if not isinstance(first_stmt, ast.Expr):
        return None

    if isinstance(first_stmt.value, ast.Constant) and isinstance(
        first_stmt.value.value, str
    ):
        start = first_stmt.lineno
        end = first_stmt.end_lineno or start
        return range(start, end + 1)

    return None


def _get_docstring_lines(content: str) -> set[int]:
    """Obtiene los números de línea (1-indexed) pertenecientes a docstrings."""
    doc_lines: set[int] = set()
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return doc_lines

    for node in ast.walk(tree):
        line_range = _extract_docstring_range(node)
        if line_range:
            doc_lines.update(line_range)

    return doc_lines


def _count_file_lines(path: Path) -> LineStats:
    """Cuenta por separado las líneas de código y de docstrings."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return LineStats()

    doc_line_numbers = (
        _get_docstring_lines(content) if path.suffix.lower() == ".py" else set()
    )

    code_lines = 0
    docstring_lines = 0

    for line_no, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            continue

        if line_no in doc_line_numbers:
            docstring_lines += 1
        else:
            code_lines += 1

    return LineStats(code=code_lines, docstrings=docstring_lines)


def _files_with_exts(base: Path, extensions: set[str]) -> Iterator[Path]:
    if not base.is_dir():
        return
    for path in sorted(base.rglob("*")):
        if path.is_file() and path.suffix.lower() in extensions:
            yield path


def _py_files(base: Path) -> Iterator[Path]:
    return _files_with_exts(base, {".py"})


def build_categories() -> list[Category]:
    """Construye las categorías de conteo con métricas desglosadas."""
    definitions = {
        "scripts": ROOT / "scripts",
        "tests": ROOT / "tests",
        "src": SRC,
    }

    return [
        Category(
            name=name,
            files=[(path, _count_file_lines(path)) for path in _py_files(base)],
        )
        for name, base in definitions.items()
    ]


def _print_verbose_tables(categories: list[Category]) -> None:
    """Imprime el informe usando tablas de Rich."""
    for category in categories:
        cat_totals = category.totals
        table = Table(
            title=f"{category.name} ({len(category.files)} ficheros)",
            title_style="cyan",
            show_lines=True,
            width=80,
            border_style="dim",
        )
        table.add_column("Ruta", overflow="fold")
        table.add_column("Código", justify="right", style="green")
        table.add_column("Docstr", justify="right", style="yellow")
        table.add_column("Total", justify="right", style="bold")

        sorted_files = sorted(category.files, key=lambda item: -item[1].total)
        for path, stats in sorted_files:
            relative = path.relative_to(ROOT)
            table.add_row(
                str(relative),
                str(stats.code),
                str(stats.docstrings),
                str(stats.total),
            )

        table.add_row(
            "[bold]TOTAL[/bold]",
            f"[bold green]{cat_totals.code}[/bold green]",
            f"[bold yellow]{cat_totals.docstrings}[/bold yellow]",
            f"[bold]{cat_totals.total}[/bold]",
        )
        console.print(table)
        console.print()


def _print_summary_table(categories: list[Category]) -> None:
    """Imprime la tabla resumen global."""
    grand_totals = LineStats()
    total_files = 0
    for category in categories:
        grand_totals += category.totals
        total_files += len(category.files)

    table = Table(
        title="Resumen por directorio",
        title_style="magenta",
        width=80,
        border_style="dim",
    )
    table.add_column("Categoría", style="cyan")
    table.add_column("Código", justify="right", style="green")
    table.add_column("Docstr", justify="right", style="yellow")
    table.add_column("Total", justify="right", style="bold")
    table.add_column("Ficheros", justify="right")

    for category in categories:
        t = category.totals
        table.add_row(
            category.name,
            str(t.code),
            str(t.docstrings),
            str(t.total),
            str(len(category.files)),
        )

    table.add_row(
        "[bold]TOTAL[/]",
        f"[bold green]{grand_totals.code}[/]",
        f"[bold yellow]{grand_totals.docstrings}[/]",
        f"[bold]{grand_totals.total}[/]",
        f"[bold]{total_files}[/]",
    )

    console.print(table)
    console.print(
        f"[dim]{total_files} ficheros procesados: "
        f"{grand_totals.code} líneas de código, "
        f"{grand_totals.docstrings} líneas de docstrings "
        f"({grand_totals.total} líneas totales).[/dim]"
    )


def _print_tree(categories: list[Category], verbose: bool) -> None:
    """Imprime el informe usando árbol de Rich."""
    root_tree = Tree("code_count", style="bold cyan")

    grand_totals = LineStats()
    total_files = 0

    for category in categories:
        cat_totals = category.totals
        grand_totals += cat_totals
        total_files += len(category.files)

        cat_branch = root_tree.add(
            f"[bold]{category.name}[/bold]/"
            f"([green]{cat_totals.code}[/green]/"
            f"[yellow]{cat_totals.docstrings}[/yellow]/"
            f"[white]{cat_totals.total}[/white], {len(category.files)} ficheros)"
        )

        if verbose:
            sorted_files = sorted(category.files, key=lambda item: -item[1].total)
            for path, stats in sorted_files:
                relative = path.relative_to(ROOT)
                cat_branch.add(
                    f"{relative} ([green]{stats.code}[/green]/"
                    f"[yellow]{stats.docstrings}[/yellow]/"
                    f"[white]{stats.total}[/white])"
                )

    root_tree.add(
        f"[bold magenta]TOTAL[/bold magenta] "
        f"([green]{grand_totals.code} l. código[/green], "
        f"[yellow]{grand_totals.docstrings} l. docstrings[/yellow], "
        f"[white]{grand_totals.total} l. totales[/white], {total_files} ficheros)"
    )

    console.print(root_tree)


# =============================================================================
#  Opciones de Typer
# =============================================================================


VerboseOption = Annotated[
    bool,
    typer.Option(
        "--verbose",
        "-v",
        help="Lista el resultado de cada fichero.",
    ),
]

TreeOption = Annotated[
    bool,
    typer.Option(
        "--tree",
        "-t",
        help="Muestra el resultado en árbol de Rich en vez de tabla.",
    ),
]


# =============================================================================
#  Comandos de Typer
# =============================================================================


@app.command()
def main(
    verbose: VerboseOption = False,
    tree: TreeOption = False,
) -> None:
    """Muestra el informe de conteo de líneas por categorías."""
    categories = build_categories()

    if tree:
        _print_tree(categories, verbose)
    else:
        if verbose:
            _print_verbose_tables(categories)
        _print_summary_table(categories)


if __name__ == "__main__":
    app()
