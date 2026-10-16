import tarfile
import zipfile
from collections.abc import Callable
from pathlib import Path
from types import ModuleType

import pytest
from typer.testing import CliRunner

EXPECTED = {"pyproject.toml", "src/pkg/mod.py"}


@pytest.fixture
def backup(
    load_script: Callable[[str], ModuleType],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> ModuleType:
    """Carga `backup.py` apuntando a un proyecto temporal."""
    module = load_script("backup")

    (tmp_path / "src" / "pkg" / "__pycache__").mkdir(parents=True)
    (tmp_path / "src" / "pkg" / "mod.py").write_bytes(b"x = 1\n")
    (tmp_path / "src" / "pkg" / "__pycache__" / "mod.pyc").write_bytes(b"\x00")
    (tmp_path / "pyproject.toml").write_bytes(b"[project]\n")
    (tmp_path / "ignored.txt").write_bytes(b"no se incluye\n")

    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "BACKUP_DIR", tmp_path / ".local")
    return module


def test_default_is_zip_in_local(
    backup: ModuleType, tmp_path: Path, runner: CliRunner
) -> None:
    result = runner.invoke(backup.app, [])

    assert result.exit_code == 0
    with zipfile.ZipFile(tmp_path / ".local" / "backup.zip") as zf:
        assert set(zf.namelist()) == EXPECTED


def test_tar_gz_with_custom_file(
    backup: ModuleType, tmp_path: Path, runner: CliRunner
) -> None:
    output = tmp_path / "out" / "copia.tar.gz"

    result = runner.invoke(backup.app, ["-a", "tar.gz", "-f", str(output)])

    assert result.exit_code == 0
    with tarfile.open(output) as tf:
        assert set(tf.getnames()) == EXPECTED


def test_removes_pycache_dirs(
    backup: ModuleType, tmp_path: Path, runner: CliRunner
) -> None:
    runner.invoke(backup.app, [])

    assert not (tmp_path / "src" / "pkg" / "__pycache__").exists()


def test_rerun_replaces_previous_archive(
    backup: ModuleType, tmp_path: Path, runner: CliRunner
) -> None:
    runner.invoke(backup.app, [])
    (tmp_path / "src" / "pkg" / "mod.py").write_bytes(b"x = 2\n")

    result = runner.invoke(backup.app, [])

    assert result.exit_code == 0
    with zipfile.ZipFile(tmp_path / ".local" / "backup.zip") as zf:
        assert zf.read("src/pkg/mod.py") == b"x = 2\n"


def test_output_cannot_overwrite_project_file(
    backup: ModuleType, tmp_path: Path, runner: CliRunner
) -> None:
    result = runner.invoke(backup.app, ["-f", str(tmp_path / "pyproject.toml")])

    assert result.exit_code == 1
    assert (tmp_path / "pyproject.toml").read_bytes() == b"[project]\n"
