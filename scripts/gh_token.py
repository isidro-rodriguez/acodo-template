"""Obtiene un token de instalación para una GitHub App.

Comandos:
    access  Genera el token de instalación (salida + portapapeles).
    test    Comprueba el acceso al repositorio configurado.

Uso:
    uv run scripts/gh_token.py access
    uv run scripts/gh_token.py access --only-token --no-clipboard
    uv run scripts/gh_token.py test
    uv run scripts/gh_token.py test -f .local/otro.json

Configuración (JSON):
    {
      "repository": "owner/repo",
      "app-id": "123456",
      "private-key": "private-key.pem",
      "installation-id": "12345678",
      "api-url": "https://api.github.com"
    }

    `private-key` admite ruta relativa al propio JSON, ruta absoluta
    o el contenido PEM embebido. Por defecto se lee
    `.local/gh_app.json` relativo a la raíz del proyecto.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Annotated, NoReturn

import jwt
import typer
from rich.console import Console
from rich.table import Table

DEFAULT_API_URL = "https://api.github.com"
DEFAULT_CONFIG_FILE = Path(__file__).resolve().parent.parent / ".local" / "gh_app.json"
JWT_LIFETIME = 480  # 8 min: margen bajo el máximo de 10 min de GitHub.
REPO_SLUG_RE = re.compile(r"^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$")

CONFIG_TEMPLATE: dict = {
    "repository": "owner/repo",
    "app-id": "123456",
    "private-key": "private-key.pem",
    "installation-id": "12345678",
    "api-url": "https://api.github.com",
}

app = typer.Typer(
    name="gh-token",
    help="Genera tokens de instalación para una GitHub App.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()
err_console = Console(stderr=True)


# =============================================================================
#  Configuración
# =============================================================================


def _fail(message: str) -> NoReturn:
    """Imprime un error con la plantilla del JSON y aborta."""
    err_console.print(f"[bold red]Error:[/] {message}")
    err_console.print()
    err_console.print("[bold]Plantilla esperada del fichero de configuración:[/]")
    err_console.print(json.dumps(CONFIG_TEMPLATE, indent=2, ensure_ascii=False))
    raise typer.Exit(code=1)


def _load_config(path: Path) -> dict:
    """Lee y valida el JSON de configuración."""
    if not path.is_file():
        _fail(f"No se encontró el fichero de configuración: {path}")
    try:
        cfg = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        _fail(f"{path} no es un JSON válido: {exc}")
    except OSError as exc:
        _fail(f"No se pudo leer {path}: {exc.strerror}")

    if not isinstance(cfg, dict):
        _fail(f"{path} debe contener un objeto JSON en la raíz.")

    for key in ("repository", "app-id", "private-key", "installation-id"):
        if not cfg.get(key):
            _fail(f"Falta la clave '{key}' en {path}.")
    return cfg


def _load_private_key(raw: str, config_path: Path) -> str:
    """Acepta ruta absoluta, relativa al JSON, o el PEM embebido."""
    candidate = Path(raw).expanduser()
    if candidate.is_file():
        return candidate.read_text(encoding="utf-8")
    local_candidate = config_path.parent / raw
    if local_candidate.is_file():
        return local_candidate.read_text(encoding="utf-8")
    if "BEGIN" in raw and "PRIVATE KEY" in raw:
        return raw.replace("\\n", "\n")
    raise ValueError("La clave privada no es un fichero legible ni un PEM válido.")


def _normalize_repo(raw: str) -> str:
    """Acepta `owner/repo` o URL de GitHub y devuelve `owner/repo`."""
    value = raw.strip()
    for prefix in (
        "https://github.com/",
        "http://github.com/",
        "git@github.com:",
    ):
        if value.startswith(prefix):
            value = value[len(prefix) :]
            break
    if value.endswith(".git"):
        value = value[:-4]
    value = value.strip("/")
    if not REPO_SLUG_RE.match(value):
        raise ValueError(
            f"'{raw}' no parece un repositorio válido (usa 'owner/repo' o la URL)."
        )
    return value


# =============================================================================
#  JWT + API
# =============================================================================


def _build_jwt(app_id: str, private_key: str) -> str:
    """Construye el JWT de la App (RS256)."""
    now = int(time.time())
    try:
        return jwt.encode(
            {"iss": app_id, "iat": now - 60, "exp": now + JWT_LIFETIME},
            private_key,
            algorithm="RS256",
        )
    except Exception as exc:
        raise ValueError(f"No se pudo firmar el JWT: {exc}") from exc


def _request(
    method: str,
    url: str,
    token: str | None = None,
    payload: dict | None = None,
) -> dict:
    """Realiza una petición JSON a la API de GitHub."""
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(url, data=data, method=method)
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("X-GitHub-Api-Version", "2022-11-28")
    if token is not None:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        try:
            detail = json.load(exc).get("message", "")
        except (json.JSONDecodeError, UnicodeDecodeError):
            detail = ""
        raise ValueError(f"GitHub devolvió {exc.code}: {detail or exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise ValueError(f"No se pudo contactar con GitHub: {exc.reason}") from exc


def _generate_token(cfg: dict, config_path: Path) -> dict:
    """Pide a GitHub un installation token y devuelve el body completo."""
    api_url = cfg.get("api-url") or DEFAULT_API_URL
    key = _load_private_key(str(cfg["private-key"]), config_path)
    jwt_token = _build_jwt(str(cfg["app-id"]), key)
    return _request(
        "POST",
        f"{api_url}/app/installations/{cfg['installation-id']}/access_tokens",
        jwt_token,
    )


# =============================================================================
#  Portapapeles (sin dependencias Python)
# =============================================================================


def _copy_windows(text: str) -> None:
    if sys.platform != "win32":  # Estrecha el tipo: ty omite el resto en Linux/macOS.
        raise NotImplementedError("Solo disponible en Windows.")

    import ctypes

    CF_UNICODETEXT = 13
    GMEM_MOVEABLE = 0x0002

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    user32 = ctypes.WinDLL("user32", use_last_error=True)

    kernel32.GlobalAlloc.restype = ctypes.c_void_p
    kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalFree.argtypes = [ctypes.c_void_p]
    user32.OpenClipboard.argtypes = [ctypes.c_void_p]
    user32.SetClipboardData.restype = ctypes.c_void_p
    user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]

    data = text.encode("utf-16-le") + b"\x00\x00"

    if not user32.OpenClipboard(None):
        raise RuntimeError("OpenClipboard falló.")
    try:
        if not user32.EmptyClipboard():
            raise RuntimeError("EmptyClipboard falló.")
        handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
        if not handle:
            raise RuntimeError("GlobalAlloc falló.")
        locked = kernel32.GlobalLock(handle)
        if not locked:
            kernel32.GlobalFree(handle)
            raise RuntimeError("GlobalLock falló.")
        try:
            ctypes.memmove(locked, data, len(data))
        finally:
            kernel32.GlobalUnlock(handle)
        if not user32.SetClipboardData(CF_UNICODETEXT, handle):
            kernel32.GlobalFree(handle)
            raise RuntimeError("SetClipboardData falló.")
    finally:
        user32.CloseClipboard()


def _copy_posix(text: str) -> None:
    if sys.platform == "darwin":
        cmd = ["pbcopy"]
    else:
        if os.environ.get("WAYLAND_DISPLAY") and shutil.which("wl-copy"):
            cmd = ["wl-copy"]
        elif shutil.which("xclip"):
            cmd = ["xclip", "-selection", "clipboard"]
        elif shutil.which("xsel"):
            cmd = ["xsel", "--clipboard", "--input"]
        elif shutil.which("wl-copy"):
            cmd = ["wl-copy"]
        else:
            raise RuntimeError(
                "No se encontró 'wl-copy', 'xclip' ni 'xsel' en el PATH."
            )
    try:
        subprocess.run(cmd, input=text.encode("utf-8"), check=True, timeout=5)
    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        FileNotFoundError,
    ) as exc:
        raise RuntimeError(f"No se pudo copiar al portapapeles: {exc}") from exc


def _copy_to_clipboard(text: str) -> None:
    if sys.platform == "win32":
        _copy_windows(text)
    else:
        _copy_posix(text)


# =============================================================================
#  Opciones de Typer
# =============================================================================


FileOption = Annotated[
    Path,
    typer.Option(
        "--file",
        "-f",
        help="Fichero JSON de configuración.",
    ),
]

OnlyTokenOption = Annotated[
    bool,
    typer.Option(
        "--only-token",
        "-o",
        help="Imprime solo el token en vez del JSON completo.",
    ),
]

NoClipboardOption = Annotated[
    bool,
    typer.Option(
        "--no-clipboard",
        help="No copiar el resultado al portapapeles.",
    ),
]

NoPrintOption = Annotated[
    bool,
    typer.Option(
        "--no-print",
        help="No imprimir el resultado por stdout.",
    ),
]


# =============================================================================
#  Comandos de Typer
# =============================================================================


@app.command()
def access(
    file: FileOption = DEFAULT_CONFIG_FILE,
    only_token: OnlyTokenOption = False,
    no_clipboard: NoClipboardOption = False,
    no_print: NoPrintOption = False,
) -> None:
    """Genera un token de instalación para la GitHub App."""
    cfg: dict[str, str] = _load_config(file)

    try:
        repo_slug = _normalize_repo(str(cfg["repository"]))
        body = _generate_token(cfg, file)
    except ValueError as exc:
        err_console.print(f"[bold red]Error:[/] {exc}")
        raise typer.Exit(code=1) from None

    # El JSON de salida incluye el repositorio de destino.
    output_data = {"repository": repo_slug, **body}
    output = (
        body["token"]
        if only_token
        else json.dumps(output_data, indent=2, ensure_ascii=False)
    )

    if not no_print:
        console.print(output)

    if not no_clipboard:
        try:
            _copy_to_clipboard(output)
            err_console.print("[green]✓[/] Copiado al portapapeles.")
        except RuntimeError as exc:
            err_console.print(f"[yellow]Aviso:[/] {exc}")


@app.command()
def test(
    file: FileOption = DEFAULT_CONFIG_FILE,
) -> None:
    """Comprueba el acceso al repositorio configurado."""
    cfg = _load_config(file)

    try:
        repo_slug = _normalize_repo(str(cfg["repository"]))
        body = _generate_token(cfg, file)
        token = body["token"]
        api_url = cfg.get("api-url") or DEFAULT_API_URL
        info = _request("GET", f"{api_url}/repos/{repo_slug}", token)
    except ValueError as exc:
        err_console.print(f"[bold red]Error:[/] {exc}")
        raise typer.Exit(code=1) from None

    perms = info.get("permissions") or {}

    def mark(value: bool | None) -> str:
        if value is True:
            return "[green]✓[/]"
        if value is False:
            return "[red]✗[/]"
        return "[dim]·[/]"

    vis = "privado" if info.get("private") else "público"

    table = Table(
        title=f"Acceso a {info.get('full_name', repo_slug)}",
        show_header=False,
        title_style="bold",
    )
    table.add_column("Campo", style="bold cyan", no_wrap=True)
    table.add_column("Valor")
    table.add_row("Repositorio", f"{info.get('full_name', repo_slug)} ({vis})")
    table.add_row("URL", info.get("html_url", "-"))
    table.add_row("Rama por defecto", info.get("default_branch", "-"))
    table.add_row(
        "Permisos",
        f"pull={mark(perms.get('pull'))}  "
        f"push={mark(perms.get('push'))}  "
        f"admin={mark(perms.get('admin'))}",
    )
    console.print(table)


if __name__ == "__main__":
    app()
