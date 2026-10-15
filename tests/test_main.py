import pytest

from pyplate.main import main


def test_main_prints_greeting(capsys: pytest.CaptureFixture[str]) -> None:
    """Verifica que `main` imprime el mensaje de bienvenida."""
    main()

    assert "listo y funcionando" in capsys.readouterr().out
