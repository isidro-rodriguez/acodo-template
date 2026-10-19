"""Pruebas de la entrada de la aplicación ``acodo_template.main``."""

import subprocess
import sys

import pytest

from acodo_template import __version__
from acodo_template.main import LOGO_ART, _color_key, main


def test_main_is_callable() -> None:
    """``main`` está definida y es invocable."""
    assert callable(main)


def test_main_prints_the_logo(capsys: pytest.CaptureFixture[str]) -> None:
    """``main`` imprime todas las filas del logo."""
    main()

    output = capsys.readouterr().out
    assert len(output.splitlines()) == len(LOGO_ART.strip("\n").splitlines())


@pytest.mark.parametrize(
    ("row", "expected"),
    [
        (0, "green"),
        (2, "light_green"),
        (6, "green"),
        (8, "orange"),
        (10, "orange"),
        (11, "dark_brown"),
        (14, "dark_brown"),
    ],
)
def test_color_key_by_row(row: int, expected: str) -> None:
    """Cada fila del logo tiene un único color, sin solapes entre rangos."""
    assert _color_key(row) == expected


def test_version_is_declared() -> None:
    """La versión se lee de los metadatos del paquete."""
    assert __version__


def test_module_runs_with_exit_code_zero() -> None:
    """``python -m acodo_template`` termina con código 0."""
    result = subprocess.run(
        [sys.executable, "-m", "acodo_template"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
