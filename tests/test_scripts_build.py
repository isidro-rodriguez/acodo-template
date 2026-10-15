import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build.py"


@pytest.fixture
def build() -> ModuleType:
    spec = importlib.util.spec_from_file_location("build_script", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_discover_package_name_single(tmp_path: Path, build: ModuleType) -> None:
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text("")
    assert build.discover_package_name(tmp_path) == "pkg"


def test_discover_package_name_requires_exactly_one(
    tmp_path: Path, build: ModuleType
) -> None:
    with pytest.raises(SystemExit):
        build.discover_package_name(tmp_path)

    for name in ("aaa", "bbb"):
        (tmp_path / name).mkdir()
        (tmp_path / name / "__init__.py").write_text("")
    with pytest.raises(SystemExit):
        build.discover_package_name(tmp_path)


def test_get_executable_name(
    build: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sys, "platform", "win32")
    assert build.get_executable_name("pkg") == "pkg.exe"

    monkeypatch.setattr(sys, "platform", "linux")
    assert build.get_executable_name("pkg") == "pkg"


def test_get_icon(build: ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "platform", "win32")
    assert build.get_icon(Path("res")).name == "icon.ico"

    monkeypatch.setattr(sys, "platform", "linux")
    assert build.get_icon(Path("res")).name == "icon.png"


def test_main_rejects_invalid_package_name(
    build: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(build, "PACKAGE_NAME", "con")
    with pytest.raises(SystemExit):
        build.main()
