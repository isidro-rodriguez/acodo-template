import importlib.util
import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType

import pytest
from typer.testing import CliRunner

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


@pytest.fixture
def load_script(monkeypatch: pytest.MonkeyPatch) -> Callable[[str], ModuleType]:
    """Devuelve una función que importa `scripts/<nombre>.py` como módulo aislado."""

    def _load(name: str) -> ModuleType:
        spec = importlib.util.spec_from_file_location(
            f"script_{name}", SCRIPTS / f"{name}.py"
        )
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, spec.name, module)
        spec.loader.exec_module(module)
        return module

    return _load


@pytest.fixture
def runner() -> CliRunner:
    """Ejecutor de comandos Typer para los tests de CLI."""
    return CliRunner()
