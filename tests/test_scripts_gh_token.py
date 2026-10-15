import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest
import typer

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "gh_token.py"


@pytest.fixture
def gh_token() -> ModuleType:
    spec = importlib.util.spec_from_file_location("gh_token_script", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_resolve_api_url_defaults(gh_token: ModuleType) -> None:
    assert gh_token._resolve_api_url({}) == "https://api.github.com"


def test_resolve_api_url_accepts_valid_and_strips_slash(
    gh_token: ModuleType,
) -> None:
    cfg = {"api-url": "https://ghe.example.com/api/v3/"}
    assert gh_token._resolve_api_url(cfg) == "https://ghe.example.com/api/v3"


def test_resolve_api_url_rejects_invalid(gh_token: ModuleType) -> None:
    with pytest.raises(typer.Exit):
        gh_token._resolve_api_url({"api-url": "htp:/mal"})


def test_load_config_rejects_invalid_api_url_in_full_flow(
    gh_token: ModuleType, tmp_path: Path
) -> None:
    cfg = {
        "repository": "owner/repo",
        "app-id": "123456",
        "private-key": "private-key.pem",
        "installation-id": "12345678",
        "api-url": "no-es-url",
    }
    config = tmp_path / "gh_app.json"
    config.write_text(json.dumps(cfg), encoding="utf-8")
    loaded = gh_token._load_config(config)
    with pytest.raises(typer.Exit):
        gh_token._resolve_api_url(loaded)


def test_copy_posix_prefers_wayland(
    gh_token: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(gh_token.sys, "platform", "linux")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-0")
    monkeypatch.setattr(gh_token.shutil, "which", lambda name: "/usr/bin/wl-copy")
    captured: dict = {}

    def fake_run(cmd: object, **kwargs: object) -> None:
        captured["cmd"] = cmd

    monkeypatch.setattr(gh_token.subprocess, "run", fake_run)
    gh_token._copy_posix("hola")
    assert captured["cmd"] == ["wl-copy"]


def test_normalize_repo_accepts_slug_and_urls(gh_token: ModuleType) -> None:
    assert gh_token._normalize_repo("owner/repo") == "owner/repo"
    assert gh_token._normalize_repo("https://github.com/owner/repo.git") == "owner/repo"
    assert (
        gh_token._normalize_repo("https://www.github.com/owner/repo?tab=x")
        == "owner/repo"
    )
    assert gh_token._normalize_repo("git@github.com:owner/repo.git") == "owner/repo"


def test_normalize_repo_rejects_invalid_social_url(
    gh_token: ModuleType,
) -> None:
    with pytest.raises(ValueError):
        gh_token._normalize_repo("https://github.com/-abc/repo")


def test_normalize_repo_still_rejects_garbage(gh_token: ModuleType) -> None:
    with pytest.raises(ValueError):
        gh_token._normalize_repo("no-es-un-repo")


def test_module_does_not_use_os_environ(gh_token: ModuleType) -> None:
    source = Path(gh_token.__file__ or SCRIPT).read_text(encoding="utf-8")
    assert "os.environ" not in source
    assert "get_env" in source
