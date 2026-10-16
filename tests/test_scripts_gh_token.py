import json
import subprocess
from collections.abc import Callable
from pathlib import Path
from types import ModuleType, SimpleNamespace

import jwt
import pytest
import typer
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

VALID_CONFIG = {
    "repository": "owner/repo",
    "app-id": "123456",
    "private-key": "private-key.pem",
    "installation-id": "12345678",
}


@pytest.fixture
def gh_token(load_script: Callable[[str], ModuleType]) -> ModuleType:
    return load_script("gh_token")


@pytest.fixture(scope="module")
def rsa_key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture(scope="module")
def private_pem(rsa_key: rsa.RSAPrivateKey) -> str:
    return rsa_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()


# ---------------------------------------------------------------------------
#  Configuración
# ---------------------------------------------------------------------------


def write_config(tmp_path: Path, cfg: dict[str, str]) -> Path:
    path = tmp_path / "gh_app.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")
    return path


def test_load_config_returns_valid_config(gh_token: ModuleType, tmp_path: Path) -> None:
    path = write_config(tmp_path, VALID_CONFIG)

    assert gh_token._load_config(path) == VALID_CONFIG


@pytest.mark.parametrize("missing", list(VALID_CONFIG))
def test_load_config_requires_every_key(
    gh_token: ModuleType, tmp_path: Path, missing: str
) -> None:
    cfg = {k: v for k, v in VALID_CONFIG.items() if k != missing}

    with pytest.raises(typer.Exit):
        gh_token._load_config(write_config(tmp_path, cfg))


def test_load_config_rejects_invalid_json(gh_token: ModuleType, tmp_path: Path) -> None:
    path = tmp_path / "gh_app.json"
    path.write_text("{no es json", encoding="utf-8")

    with pytest.raises(typer.Exit):
        gh_token._load_config(path)


@pytest.mark.parametrize(
    ("cfg", "expected"),
    [
        ({}, "https://api.github.com"),
        (
            {"api-url": "https://ghe.example.com/api/v3/"},
            "https://ghe.example.com/api/v3",
        ),
    ],
)
def test_resolve_api_url(gh_token: ModuleType, cfg: dict, expected: str) -> None:
    assert gh_token._resolve_api_url(cfg) == expected


def test_resolve_api_url_rejects_invalid(gh_token: ModuleType) -> None:
    with pytest.raises(typer.Exit):
        gh_token._resolve_api_url({"api-url": "htp:/mal"})


# ---------------------------------------------------------------------------
#  Repositorio y clave privada
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw",
    [
        "owner/repo",
        "https://github.com/owner/repo.git",
        "https://www.github.com/owner/repo?tab=x",
        "git@github.com:owner/repo.git",
    ],
)
def test_normalize_repo_accepts_slug_and_urls(gh_token: ModuleType, raw: str) -> None:
    assert gh_token._normalize_repo(raw) == "owner/repo"


@pytest.mark.parametrize("raw", ["no-es-un-repo", "https://github.com/-abc/repo"])
def test_normalize_repo_rejects_invalid(gh_token: ModuleType, raw: str) -> None:
    with pytest.raises(ValueError):
        gh_token._normalize_repo(raw)


def test_load_private_key_reads_file_next_to_config(
    gh_token: ModuleType, tmp_path: Path, private_pem: str
) -> None:
    (tmp_path / "private-key.pem").write_text(private_pem, encoding="utf-8")

    key = gh_token._load_private_key("private-key.pem", tmp_path / "gh_app.json")

    assert key == private_pem


def test_load_private_key_accepts_embedded_pem_with_escaped_newlines(
    gh_token: ModuleType, tmp_path: Path, private_pem: str
) -> None:
    embedded = private_pem.replace("\n", "\\n")

    key = gh_token._load_private_key(embedded, tmp_path / "gh_app.json")

    assert key == private_pem


def test_load_private_key_rejects_garbage(gh_token: ModuleType, tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        gh_token._load_private_key("no-existe.pem", tmp_path / "gh_app.json")


# ---------------------------------------------------------------------------
#  JWT
# ---------------------------------------------------------------------------


def test_build_jwt_is_signed_with_the_private_key(
    gh_token: ModuleType, rsa_key: rsa.RSAPrivateKey, private_pem: str
) -> None:
    token = gh_token._build_jwt("123456", private_pem)

    claims = jwt.decode(token, rsa_key.public_key(), algorithms=["RS256"])
    assert claims["iss"] == "123456"
    assert claims["exp"] - claims["iat"] <= 600  # GitHub exige menos de 10 minutos


def test_build_jwt_rejects_invalid_key(gh_token: ModuleType) -> None:
    with pytest.raises(ValueError):
        gh_token._build_jwt("123456", "no-es-una-clave")


# ---------------------------------------------------------------------------
#  Portapapeles
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("platform", "wayland", "available", "expected"),
    [
        ("darwin", False, [], ["pbcopy"]),
        ("linux", True, ["wl-copy", "xclip"], ["wl-copy"]),
        ("linux", False, ["xclip", "wl-copy"], ["xclip", "-selection", "clipboard"]),
        ("linux", False, ["xsel"], ["xsel", "--clipboard", "--input"]),
    ],
)
def test_copy_posix_picks_command(
    gh_token: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    platform: str,
    wayland: bool,
    available: list[str],
    expected: list[str],
) -> None:
    captured: dict[str, object] = {}

    def fake_run(cmd: list[str], **kwargs: object) -> None:
        captured["cmd"] = cmd
        captured["input"] = kwargs["input"]

    # Se parchean los nombres del módulo, no los módulos globales (`sys`, etc.).
    monkeypatch.setattr(gh_token, "sys", SimpleNamespace(platform=platform))
    monkeypatch.setattr(
        gh_token,
        "get_env",
        lambda name: "wayland-0" if wayland and name == "WAYLAND_DISPLAY" else None,
    )
    monkeypatch.setattr(
        gh_token,
        "shutil",
        SimpleNamespace(which=lambda name: name if name in available else None),
    )
    monkeypatch.setattr(
        gh_token,
        "subprocess",
        SimpleNamespace(
            run=fake_run,
            CalledProcessError=subprocess.CalledProcessError,
            TimeoutExpired=subprocess.TimeoutExpired,
        ),
    )

    gh_token._copy_posix("hola")

    assert captured == {"cmd": expected, "input": b"hola"}


def test_copy_posix_fails_without_clipboard_tool(
    gh_token: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(gh_token, "sys", SimpleNamespace(platform="linux"))
    monkeypatch.setattr(gh_token, "get_env", lambda name: None)
    monkeypatch.setattr(gh_token, "shutil", SimpleNamespace(which=lambda name: None))

    with pytest.raises(RuntimeError):
        gh_token._copy_posix("hola")
