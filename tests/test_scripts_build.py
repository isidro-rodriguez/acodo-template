import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType

import pytest
import typer
from typer.testing import CliRunner


@pytest.fixture
def build(
    load_script: Callable[[str], ModuleType],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> ModuleType:
    """Carga `build.py` apuntando a un proyecto temporal con un paquete `pkg`."""
    module = load_script("build")

    package = tmp_path / "src" / "pkg"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text('"""Paquete."""\n')
    (package / "main.py").write_text("x = 1\n")

    monkeypatch.setattr(module, "SRC", tmp_path / "src")
    return module


@pytest.fixture
def fake_build(build: ModuleType, monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """`build` con PyInstaller simulado: crea en `--distpath` lo que generaría."""

    def fake_run(cmd: list[str]) -> None:
        prefix = "--distpath="
        dist = Path(next(a[len(prefix) :] for a in cmd if a.startswith(prefix)))
        executable = build._get_executable_name("pkg")
        if "--onefile" in cmd:
            dist.mkdir(parents=True, exist_ok=True)
            (dist / executable).write_text("binario")
        else:
            (dist / "pkg" / "_internal").mkdir(parents=True, exist_ok=True)
            (dist / "pkg" / executable).write_text("binario")

    monkeypatch.setattr(build, "_run_pyinstaller", fake_run)
    return build


def test_discover_package_name_single(build: ModuleType, tmp_path: Path) -> None:
    assert build._discover_package_name(tmp_path / "src") == "pkg"


@pytest.mark.parametrize("names", [[], ["a", "b"]])
def test_discover_package_name_requires_exactly_one(
    build: ModuleType, tmp_path: Path, names: list[str]
) -> None:
    src = tmp_path / "otro"
    src.mkdir()
    for name in names:
        (src / name).mkdir()
        (src / name / "__init__.py").write_text("")

    with pytest.raises(typer.Exit):
        build._discover_package_name(src)


def test_run_pyinstaller_reports_failure(
    build: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(typer.Exit):
        build._run_pyinstaller([sys.executable, "-c", "raise SystemExit(3)"])

    assert "código 3" in capsys.readouterr().err


def test_default_build_creates_folder_with_executable(
    fake_build: ModuleType, tmp_path: Path, runner: CliRunner
) -> None:
    output = tmp_path / "out"

    result = runner.invoke(fake_build.app, ["-o", str(output), "--no-icon"])

    assert result.exit_code == 0
    executable = fake_build._get_executable_name("pkg")
    assert (output / "pkg" / executable).is_file()


def test_rebuild_replaces_previous_folder(
    fake_build: ModuleType, tmp_path: Path, runner: CliRunner
) -> None:
    args = ["-o", str(tmp_path / "out"), "--no-icon"]

    first = runner.invoke(fake_build.app, args)
    second = runner.invoke(fake_build.app, args)

    assert first.exit_code == 0
    assert second.exit_code == 0


def test_onefile_build_creates_single_file(
    fake_build: ModuleType, tmp_path: Path, runner: CliRunner
) -> None:
    output = tmp_path / "out"

    result = runner.invoke(
        fake_build.app, ["-o", str(output), "--no-icon", "--onefile"]
    )

    assert result.exit_code == 0
    assert (output / fake_build._get_executable_name("pkg")).is_file()


def test_missing_icon_fails_unless_no_icon(
    fake_build: ModuleType, tmp_path: Path, runner: CliRunner
) -> None:
    result = runner.invoke(fake_build.app, ["-o", str(tmp_path / "out")])

    assert result.exit_code == 1
    assert "icono" in result.output
