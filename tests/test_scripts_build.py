import importlib.util
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest
import typer
from typer.testing import CliRunner

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build.py"

runner = CliRunner()


@pytest.fixture
def build(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Carga `scripts/build.py` apuntando a un proyecto temporal con un paquete."""
    spec = importlib.util.spec_from_file_location("build_script", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    package = tmp_path / "src" / "pkg"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text('"""Paquete."""\n')
    (package / "main.py").write_text("x = 1\n")

    monkeypatch.setattr(module, "SRC", tmp_path / "src")
    return module


def fake_pyinstaller(build: ModuleType, cmd: list[str]) -> None:
    """Simula PyInstaller: crea en `--distpath` lo que generaría de verdad."""
    prefix = "--distpath="
    dist = Path(next(a[len(prefix) :] for a in cmd if a.startswith(prefix)))
    executable = build._get_executable_name("pkg")
    if "--onefile" in cmd:
        dist.mkdir(parents=True, exist_ok=True)
        (dist / executable).write_text("binario")
    else:
        (dist / "pkg" / "_internal").mkdir(parents=True, exist_ok=True)
        (dist / "pkg" / executable).write_text("binario")


@pytest.fixture
def patched_run(build: ModuleType, monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    monkeypatch.setattr(
        build, "_run_pyinstaller", lambda cmd: fake_pyinstaller(build, cmd)
    )
    return build


def test_discover_package_name_single(build: ModuleType, tmp_path: Path) -> None:
    assert build._discover_package_name(tmp_path / "src") == "pkg"


@pytest.mark.parametrize("names", [[], ["a", "b"]])
def test_discover_package_name_requires_exactly_one(
    build: ModuleType, tmp_path: Path, names: list[str]
) -> None:
    src = tmp_path / "otro"
    for name in names:
        (src / name).mkdir(parents=True)
        (src / name / "__init__.py").write_text("")
    src.mkdir(exist_ok=True)

    with pytest.raises(typer.Exit):
        build._discover_package_name(src)


def test_executable_name_depends_on_platform(
    build: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(build, "sys", SimpleNamespace(platform="win32"))
    assert build._get_executable_name("pkg") == "pkg.exe"

    monkeypatch.setattr(build, "sys", SimpleNamespace(platform="linux"))
    assert build._get_executable_name("pkg") == "pkg"


def test_run_pyinstaller_reports_failure(
    build: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(typer.Exit):
        build._run_pyinstaller([sys.executable, "-c", "raise SystemExit(3)"])

    assert "código 3" in capsys.readouterr().err


def test_default_build_creates_folder_with_executable(
    patched_run: ModuleType, tmp_path: Path
) -> None:
    output = tmp_path / "out"

    result = runner.invoke(patched_run.app, ["-o", str(output), "--no-icon"])

    assert result.exit_code == 0
    executable = patched_run._get_executable_name("pkg")
    assert (output / "pkg" / executable).is_file()


def test_rebuild_replaces_previous_folder(
    patched_run: ModuleType, tmp_path: Path
) -> None:
    args = ["-o", str(tmp_path / "out"), "--no-icon"]

    first = runner.invoke(patched_run.app, args)
    second = runner.invoke(patched_run.app, args)

    assert first.exit_code == 0
    assert second.exit_code == 0


def test_onefile_build_creates_single_file(
    patched_run: ModuleType, tmp_path: Path
) -> None:
    output = tmp_path / "out"

    result = runner.invoke(
        patched_run.app, ["-o", str(output), "--no-icon", "--onefile"]
    )

    assert result.exit_code == 0
    assert (output / patched_run._get_executable_name("pkg")).is_file()


def test_missing_icon_fails_unless_no_icon(
    patched_run: ModuleType, tmp_path: Path
) -> None:
    result = runner.invoke(patched_run.app, ["-o", str(tmp_path / "out")])

    assert result.exit_code == 1
    assert "icono" in result.output
