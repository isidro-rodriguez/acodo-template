import importlib.util
import tarfile
import zipfile
from pathlib import Path
from types import ModuleType

import pytest
from typer.testing import CliRunner

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "backup.py"
EXPECTED = {"pyproject.toml", "src/pkg/mod.py"}

runner = CliRunner()


@pytest.fixture
def backup(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Carga `scripts/backup.py` apuntando a un proyecto temporal."""
    spec = importlib.util.spec_from_file_location("backup_script", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    (tmp_path / "src" / "pkg" / "__pycache__").mkdir(parents=True)
    (tmp_path / "src" / "pkg" / "mod.py").write_text("x = 1\n")
    (tmp_path / "src" / "pkg" / "__pycache__" / "mod.pyc").write_bytes(b"\x00")
    (tmp_path / "pyproject.toml").write_text("[project]\n")
    (tmp_path / "ignored.txt").write_text("no se incluye\n")

    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "BACKUP_DIR", tmp_path / ".local")
    return module


def test_default_is_zip_in_local(backup: ModuleType, tmp_path: Path) -> None:
    result = runner.invoke(backup.app, [])

    assert result.exit_code == 0
    with zipfile.ZipFile(tmp_path / ".local" / "backup.zip") as zf:
        assert set(zf.namelist()) == EXPECTED
    assert not (tmp_path / "src" / "pkg" / "__pycache__").exists()


def test_tar_gz_with_custom_file(backup: ModuleType, tmp_path: Path) -> None:
    output = tmp_path / "out" / "copia.tar.gz"

    result = runner.invoke(backup.app, ["-a", "tar.gz", "-f", str(output)])

    assert result.exit_code == 0
    with tarfile.open(output) as tf:
        assert set(tf.getnames()) == EXPECTED


def test_output_cannot_overwrite_project_file(
    backup: ModuleType, tmp_path: Path
) -> None:
    result = runner.invoke(backup.app, ["-f", str(tmp_path / "pyproject.toml")])

    assert result.exit_code == 1
    assert (tmp_path / "pyproject.toml").read_text() == "[project]\n"
