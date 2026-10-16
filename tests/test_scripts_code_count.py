import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "code_count.py"


@pytest.fixture
def code_count_module() -> ModuleType:
    """Carga `scripts/code_count.py` como módulo de prueba."""
    spec = importlib.util.spec_from_file_location("code_count_script", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["code_count_script"] = module
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
#  LineStats
# ---------------------------------------------------------------------------


def test_line_stats_total(code_count_module: ModuleType) -> None:
    """La propiedad total suma código y docstrings."""
    stats = code_count_module.LineStats(code=10, docstrings=5)
    assert stats.total == 15


def test_line_stats_total_zero(code_count_module: ModuleType) -> None:
    """Un conteo vacío tiene total cero."""
    stats = code_count_module.LineStats()
    assert stats.total == 0


def test_line_stats_add(code_count_module: ModuleType) -> None:
    """Suma dos LineStats campo a campo."""
    a = code_count_module.LineStats(code=10, docstrings=5)
    b = code_count_module.LineStats(code=3, docstrings=2)
    result = a + b
    assert result.code == 13
    assert result.docstrings == 7
    assert result.total == 20


# ---------------------------------------------------------------------------
#  Category
# ---------------------------------------------------------------------------


def test_category_totals(code_count_module: ModuleType) -> None:
    """totals acumula las métricas de todos los ficheros."""
    cat = code_count_module.Category(name="scripts")
    cat.files = [
        (Path("a.py"), code_count_module.LineStats(code=10, docstrings=5)),
        (Path("b.py"), code_count_module.LineStats(code=3, docstrings=2)),
    ]
    totals = cat.totals
    assert totals.code == 13
    assert totals.docstrings == 7
    assert totals.total == 20


def test_category_totals_empty(code_count_module: ModuleType) -> None:
    """Una categoría sin ficheros tiene totales nulos."""
    cat = code_count_module.Category(name="vacía")
    assert cat.totals.total == 0


# ---------------------------------------------------------------------------
#  _get_docstring_lines
# ---------------------------------------------------------------------------


def test_get_docstring_lines_single_line(code_count_module: ModuleType) -> None:
    """Detecta un docstring de una sola línea."""
    content = '"""modulo docstring"""\nx = 1\n'
    lines = code_count_module._get_docstring_lines(content)
    assert lines == {1}


def test_get_docstring_lines_multiline(code_count_module: ModuleType) -> None:
    """Detecta un docstring de varias líneas."""
    content = '"""doc\\\nmulti\\\n"""\nx = 1\n'
    lines = code_count_module._get_docstring_lines(content)
    assert lines == {1, 2, 3}


def test_get_docstring_lines_class_and_function(code_count_module: ModuleType) -> None:
    """Detecta docstrings de clase y función además del módulo."""
    content = (
        '"""modulo"""\n'
        "class C:\n"
        '    """clase"""\n'
        "    def m(self):\n"
        '        """funcion"""\n'
        "        pass\n"
    )
    lines = code_count_module._get_docstring_lines(content)
    assert lines == {1, 3, 5}


def test_get_docstring_lines_none(code_count_module: ModuleType) -> None:
    """Sin docstrings devuelve un conjunto vacío."""
    content = "x = 1\n# comentario\n"
    lines = code_count_module._get_docstring_lines(content)
    assert lines == set()


def test_get_docstring_lines_syntax_error(code_count_module: ModuleType) -> None:
    """Con sintaxis inválida no falla y devuelve vacío."""
    content = "x =\n"
    lines = code_count_module._get_docstring_lines(content)
    assert lines == set()


# ---------------------------------------------------------------------------
#  _count_file_lines
# ---------------------------------------------------------------------------


def test_count_file_lines(code_count_module: ModuleType, tmp_path: Path) -> None:
    """Cuenta código y docstrings por separado en un fichero real."""
    path = tmp_path / "sample.py"
    path.write_text(
        '"""documento de modulo"""\n'
        "x = 1\n"
        "# comentario ordinario\n"
        "\n"
        "def f():\n"
        '    """doc de funcion"""\n'
        "    return x\n",
        encoding="utf-8",
    )
    stats = code_count_module._count_file_lines(path)
    assert stats.code == 3  # x = 1, def f():, return x
    assert stats.docstrings == 2  # doc de modulo, doc de funcion
    assert stats.total == 5


def test_count_file_lines_ignores_comments_and_blanks(
    code_count_module: ModuleType, tmp_path: Path
) -> None:
    """Líneas en blanco y comentarios no cuentan como código."""
    path = tmp_path / "sample.py"
    path.write_text(
        "# solo comentario\n\n   \nx = 1\n",
        encoding="utf-8",
    )
    stats = code_count_module._count_file_lines(path)
    assert stats.code == 1
    assert stats.docstrings == 0
    assert stats.total == 1
