"""Conteo de líneas de código y docstrings.

Cuenta las líneas efectivas separando el código fuente de los docstrings,
excluyendo líneas en blanco y comentarios ordinarios (#).

Uso:
    uv run python scripts/code_count.py
"""

import ast
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Self

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

CODE_EXTENSIONS = {".py"}


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
        return type(self)(
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

    # Comprobación estricta para el análisis estático de tipos
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


def count_file_lines(path: Path) -> LineStats:
    """Cuenta por separado las líneas de código y de docstrings.

    Args:
        path: Fichero a analizar.

    Returns:
        Estructura LineStats con las métricas obtenidas.
    """
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
            files=[(path, count_file_lines(path)) for path in _py_files(base)],
        )
        for name, base in definitions.items()
    ]


def _print_category(category: Category) -> None:
    """Imprime el detalle de ficheros mostrando código y docstrings."""
    print(f"\n## {category.name} ({len(category.files)} ficheros)")
    print(f"  {'Código':>8} {'Docstr':>8} {'Total':>8}  Ruta")
    print(f"  {'-' * 30}")

    sorted_files = sorted(category.files, key=lambda item: -item[1].total)
    for path, stats in sorted_files:
        relative = path.relative_to(ROOT)
        print(f"  {stats.code:>8} {stats.docstrings:>8} {stats.total:>8}  {relative}")

    cat_totals = category.totals
    print(f"  {'-' * 30}")
    print(
        f"  {cat_totals.code:>8} {cat_totals.docstrings:>8} "
        f"{cat_totals.total:>8}  TOTAL {category.name}"
    )


def main() -> None:
    """Muestra el informe comparativo por categorías."""
    categories = build_categories()
    for category in categories:
        _print_category(category)

    grand_totals = LineStats()
    total_files = 0

    for category in categories:
        grand_totals += category.totals
        total_files += len(category.files)

    print(f"\n{'=' * 60}")
    print(f"  {'Categoría':<16} {'Código':>8} {'Docstr':>8} {'Total':>8}")
    print(f"  {'-' * 44}")
    for category in categories:
        t = category.totals
        print(f"  {category.name:<16} {t.code:>8} {t.docstrings:>8} {t.total:>8}")
    print(f"  {'-' * 44}")
    print(
        f"  {'TOTAL':<16} {grand_totals.code:>8} {grand_totals.docstrings:>8} "
        f"{grand_totals.total:>8}"
    )

    print(
        f"\n  {total_files} ficheros procesados: {grand_totals.code} líneas de código, "
        f"{grand_totals.docstrings} líneas de docstrings "
        f"({grand_totals.total} líneas totales)."
    )


if __name__ == "__main__":
    main()
