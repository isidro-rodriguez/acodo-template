"""Pruebas para verificar que ``acodo_template.main`` se ejecuta."""

from acodo_template.main import main


def test_main_existe() -> None:
    """``main`` está definida y es invertible."""
    assert callable(main)


def test_main_ejecuta_sin_excepciones() -> None:
    """``main`` ejecuta sin lanzar excepciones (no comprobamos salida)."""
    main()  # Si no saltó error, se ejecutó con éxito.


def test_main_via_script_ejecuta_con_codigo_cero() -> None:
    """``python -m acodo_template`` termina con código 0 (ejecuta sin problemas)."""
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "-m", "acodo_template"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
