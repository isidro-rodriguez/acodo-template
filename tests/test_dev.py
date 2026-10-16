from collections.abc import Callable, Sequence
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest
from typer.testing import CliRunner

ROOT = Path(__file__).resolve().parents[1]

ALL_STEPS = [
    ("ruff", "format"),
    ("ruff", "check", "--fix"),
    ("ty", "check"),
    ("pytest",),
]


class FakeRun:
    """Sustituto de `dev._run`: registra los comandos y simula sus códigos."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, ...]] = []
        self.codes: dict[tuple[str, ...], int] = {}
        self.default = 0

    def __call__(self, command: Sequence[str]) -> int:
        cmd = tuple(command)
        self.calls.append(cmd)
        return self.codes.get(cmd[2:], self.default)

    @property
    def steps(self) -> list[tuple[str, ...]]:
        """Comandos de calidad ejecutados, sin `python -m`."""
        return [cmd[2:] for cmd in self.calls]


@pytest.fixture
def dev(load_script: Callable[..., ModuleType]) -> ModuleType:
    return load_script("dev", ROOT)


@pytest.fixture
def fake_run(dev: ModuleType, monkeypatch: pytest.MonkeyPatch) -> FakeRun:
    fake = FakeRun()
    monkeypatch.setattr(dev, "_run", fake)
    return fake


# ---------------------------------------------------------------------------
#  Comandos registrados
# ---------------------------------------------------------------------------


def test_help_lists_scripts_and_project_commands(
    dev: ModuleType, runner: CliRunner
) -> None:
    result = runner.invoke(dev.app, ["--help"])

    for command in ("backup", "build", "code-count", "gh-token", "check", "api"):
        assert command in result.output


def test_gh_token_group_exposes_its_commands(
    dev: ModuleType, runner: CliRunner
) -> None:
    result = runner.invoke(dev.app, ["gh-token", "--help"])

    assert "access" in result.output
    assert "test" in result.output


# ---------------------------------------------------------------------------
#  check
# ---------------------------------------------------------------------------


def test_check_runs_every_step_by_default(
    dev: ModuleType, fake_run: FakeRun, runner: CliRunner
) -> None:
    result = runner.invoke(dev.app, ["check"])

    assert result.exit_code == 0
    assert fake_run.steps == ALL_STEPS


def test_check_flags_select_steps_in_fixed_order(
    dev: ModuleType, fake_run: FakeRun, runner: CliRunner
) -> None:
    result = runner.invoke(dev.app, ["check", "--types", "--lint"])

    assert result.exit_code == 0
    assert fake_run.steps == [("ruff", "check", "--fix"), ("ty", "check")]


def test_check_fails_but_still_runs_remaining_steps(
    dev: ModuleType, fake_run: FakeRun, runner: CliRunner
) -> None:
    fake_run.codes[("ruff", "check", "--fix")] = 1

    result = runner.invoke(dev.app, ["check"])

    assert result.exit_code == 1
    assert fake_run.steps == ALL_STEPS


# ---------------------------------------------------------------------------
#  api
# ---------------------------------------------------------------------------


@pytest.fixture
def with_uv(dev: ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(dev, "shutil", SimpleNamespace(which=lambda _name: "uv"))


@pytest.mark.usefixtures("with_uv")
def test_api_defaults_to_the_discovered_package(
    dev: ModuleType,
    fake_run: FakeRun,
    runner: CliRunner,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = tmp_path / "src" / "pkg"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("")
    monkeypatch.setattr(dev, "SRC", tmp_path / "src")

    result = runner.invoke(dev.app, ["api"])

    assert result.exit_code == 0
    (command,) = fake_run.calls
    assert command[-1] == str(package)
    assert command[:7] == ("uv", "run", "--with", "pdoc", "pdoc", "-d", "google")
    assert "-o" not in command


@pytest.mark.usefixtures("with_uv")
def test_api_accepts_custom_path_and_output(
    dev: ModuleType, fake_run: FakeRun, runner: CliRunner, tmp_path: Path
) -> None:
    module = tmp_path / "mod.py"
    module.write_text("")
    output = tmp_path / "docs"

    result = runner.invoke(dev.app, ["api", "-p", str(module), "-o", str(output)])

    assert result.exit_code == 0
    (command,) = fake_run.calls
    assert command[-1] == str(module.resolve())
    assert command[command.index("-o") + 1] == str(output.resolve())


@pytest.mark.usefixtures("with_uv")
def test_api_propagates_pdoc_failure(
    dev: ModuleType, fake_run: FakeRun, runner: CliRunner, tmp_path: Path
) -> None:
    module = tmp_path / "mod.py"
    module.write_text("")
    fake_run.default = 3

    result = runner.invoke(dev.app, ["api", "-p", str(module)])

    assert result.exit_code == 3


def test_api_requires_uv(
    dev: ModuleType,
    fake_run: FakeRun,
    runner: CliRunner,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(dev, "shutil", SimpleNamespace(which=lambda _name: None))
    module = tmp_path / "mod.py"
    module.write_text("")

    result = runner.invoke(dev.app, ["api", "-p", str(module)])

    assert result.exit_code == 1
    assert fake_run.calls == []
    assert "uv" in result.output
