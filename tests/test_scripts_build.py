import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock

import pytest
import typer
from typer.testing import CliRunner

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build.py"

runner = CliRunner()


@pytest.fixture
def build_module(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Carga `scripts/build.py` apuntando a un proyecto temporal."""
    spec = importlib.util.spec_from_file_location("build_script", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    pkg = tmp_path / "src" / "pkg"
    pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text("")
    (pkg / "main.py").write_text("")
    resources = pkg / "resources"
    resources.mkdir()
    icon_name = "icon.ico" if sys.platform == "win32" else "icon.png"
    (resources / icon_name).write_bytes(b"fake icon")

    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "SRC", tmp_path / "src")
    monkeypatch.setattr(module, "PACKAGE_NAME", "pkg")
    return module


def _fake_subprocess_run(
    monkeypatch: pytest.MonkeyPatch, module: ModuleType
) -> list[list[str]]:
    """Sustituye `subprocess.run` y crea el binario producido por PyInstaller."""
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], **kwargs: object) -> MagicMock:
        calls.append(list(cmd))
        mock = MagicMock()
        mock.returncode = 0
        distpath: str | None = None
        for i, arg in enumerate(cmd):
            if arg == "--distpath" and i + 1 < len(cmd):
                distpath = cmd[i + 1]
            elif arg.startswith("--distpath="):
                distpath = arg.split("=", 1)[1]
        if distpath is not None:
            dist = Path(distpath)
            exe = "pkg.exe" if sys.platform == "win32" else "pkg"
            produced = dist / exe
            produced.parent.mkdir(parents=True, exist_ok=True)
            produced.write_bytes(b"fake binary")
        return mock

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    return calls


# ---------------------------------------------------------------------------
#  CLI flags
# ---------------------------------------------------------------------------


def test_cli_exposes_flags(build_module: ModuleType) -> None:
    """Typer expone --onefile, --no-icon y --output en la ayuda."""
    result = runner.invoke(build_module.app, ["--help"])

    assert result.exit_code == 0
    assert "--onefile" in result.output
    assert "--no-icon" in result.output
    assert "--output" in result.output


# ---------------------------------------------------------------------------
#  discover_package_name
# ---------------------------------------------------------------------------


def test_discover_package_name_single(tmp_path: Path, build_module: ModuleType) -> None:
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text("")
    assert build_module.discover_package_name(tmp_path) == "pkg"


def test_discover_package_name_requires_exactly_one(
    tmp_path: Path, build_module: ModuleType
) -> None:
    with pytest.raises(SystemExit):
        build_module.discover_package_name(tmp_path)

    for name in ("aaa", "bbb"):
        (tmp_path / name).mkdir()
        (tmp_path / name / "__init__.py").write_text("")
    with pytest.raises(SystemExit):
        build_module.discover_package_name(tmp_path)


# ---------------------------------------------------------------------------
#  get_executable_name / get_icon
# ---------------------------------------------------------------------------


def test_get_executable_name(
    build_module: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sys, "platform", "win32")
    assert build_module.get_executable_name("pkg") == "pkg.exe"

    monkeypatch.setattr(sys, "platform", "linux")
    assert build_module.get_executable_name("pkg") == "pkg"


def test_get_icon(build_module: ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "platform", "win32")
    assert build_module.get_icon(Path("res")).name == "icon.ico"

    monkeypatch.setattr(sys, "platform", "linux")
    assert build_module.get_icon(Path("res")).name == "icon.png"


# ---------------------------------------------------------------------------
#  main
# ---------------------------------------------------------------------------


def test_main_rejects_invalid_package_name(
    build_module: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(build_module, "PACKAGE_NAME", "con")
    with pytest.raises(typer.exceptions.Exit):
        build_module.main()


def test_main_default_omits_onefile_and_uses_icon(
    build_module: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = _fake_subprocess_run(monkeypatch, build_module)

    build_module.main()

    assert len(calls) == 1
    cmd = calls[0]
    assert "--onefile" not in cmd
    assert any(arg.startswith("--icon=") for arg in cmd)
    assert str(build_module.SRC / "pkg" / "main.py") in cmd
    exe = "pkg.exe" if sys.platform == "win32" else "pkg"
    assert (build_module.ROOT / "build" / exe).exists()


def test_main_onefile_adds_flag(
    build_module: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = _fake_subprocess_run(monkeypatch, build_module)

    build_module.main(onefile=True)

    assert "--onefile" in calls[0]


def test_main_no_icon_omits_icon_and_skips_validation(
    build_module: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Eliminar el icono para comprobar que --no-icon no lo valida.
    icon_name = "icon.ico" if sys.platform == "win32" else "icon.png"
    (build_module.SRC / "pkg" / "resources" / icon_name).unlink()

    calls = _fake_subprocess_run(monkeypatch, build_module)

    build_module.main(no_icon=True)

    assert not any(arg.startswith("--icon=") for arg in calls[0])


def test_main_missing_icon_without_no_icon_fails(
    build_module: ModuleType,
) -> None:
    icon_name = "icon.ico" if sys.platform == "win32" else "icon.png"
    (build_module.SRC / "pkg" / "resources" / icon_name).unlink()

    with pytest.raises(typer.exceptions.Exit):
        build_module.main()


def test_main_output_custom_directory(
    build_module: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = _fake_subprocess_run(monkeypatch, build_module)
    custom_output = build_module.ROOT / "dist"

    build_module.main(output=custom_output)

    exe = "pkg.exe" if sys.platform == "win32" else "pkg"
    assert (custom_output / exe).exists()
    # Los directorios de trabajo de PyInstaller están bajo el directorio de salida.
    assert any(str(custom_output / "_pyinstaller") in arg for arg in calls[0])
