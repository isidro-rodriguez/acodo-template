# PyPlate

Plantilla minimalista para proyectos en **Python >= 3.13**.

Está optimizada para el uso de las herramientas de [Astral](https://astral.sh):
`uv`, `ruff` y `ty`.

## 🚀 Instalación

`ruff` y `ty` están en el grupo `dev` de `pyproject.toml`, así que sus versiones
quedan fijadas en `uv.lock` y coinciden en local y en CI. `pre-commit` y `pdoc`
se usan con `uvx` (o instálalos globalmente con `uv tool install pre-commit pdoc`).

```bash
uv sync    # Crea el entorno virtual e instala dependencias (grupo dev)
```

## 🛠️ Comandos Habituales

```bash
uv run pyplate                  # Ejecutar la aplicación (también: python -m pyplate)
uv run ruff format              # Formateado automático según PEP 8
uv run ruff check               # Lint automático
uv run ty check                 # Comprobar tipado estricto
uv run pytest                   # Ejecutar la suite de pruebas unitarias
uvx pre-commit run --all-files  # Ejecutar secuencia pre-commit
uvx pdoc src/pyplate -d google  # Documentación rápida en HTML

uv run python scripts/backup.py                   # Copia de seguridad en .local/
uv run python scripts/code_count.py               # Conteo de líneas de código y docstrings
uv run --group build python scripts/build.py      # Ejecutable único en build/
uv run python scripts/gh_token.py access          # Token de instalación de una GitHub App
uv run python scripts/gh_token.py test            # Comprueba el acceso al repositorio
```

### 🔑 Token de GitHub App

`scripts/gh_token.py` genera un token de instalación (válido 1 hora) a partir de
una configuración JSON, por defecto `.local/gh_app.json`:

```json
{
  "repository": "owner/repo",
  "app-id": "123456",
  "private-key": "private-key.pem",
  "installation-id": "12345678",
  "api-url": "https://api.github.com"
}
```

`private-key` admite ruta relativa al JSON, ruta absoluta o el PEM embebido.
Opciones útiles: `--only-token` (imprime solo el token), `--no-clipboard` (no lo
copia al portapapeles) y `-f ruta.json` (usa otra configuración). Mantén la clave
privada y el JSON en `.local/`, que git ignora.

## 📁 Estructura del Proyecto

```bash
.
├── .github/                # Configuración y automatizaciones de GitHub
│   ├── workflows/              # Definiciones de flujos de GitHub Actions
│   │   └── ci.yml                  # Pipeline de integración continua: lint, tipado, tests
│   └── dependabot.yml          # Actualizaciones automáticas (GitHub Actions y uv)
├── .local/                 # Ficheros locales privados (ignorado por git; salida de backup.py)
├── scripts/                # Scripts utilitarios encapsulados
│   ├── backup.py               # Realiza una copia de seguridad del proyecto
│   ├── build.py                # Empaqueta la aplicación con PyInstaller
│   ├── code_count.py           # Cuenta líneas de código y de docstrings
│   └── gh_token.py             # Genera tokens de instalación de una GitHub App
├── src/                    # Código fuente del proyecto (layout src)
│   └── pyplate/                # Paquete principal de Python
│       ├── resources/              # Recursos del paquete (iconos)
│       ├── __init__.py             # Marca pyplate como paquete; expone la versión
│       ├── __main__.py             # Permite ejecutar con `python -m pyplate`
│       └── main.py                 # Lógica del punto de entrada
├── tests/                  # Pruebas del proyecto
│   └── test_main.py            # Ejemplo de prueba con pytest
├── .gitattributes          # Reglas de atributos Git: finales de línea, binarios, diffs, etc.
├── .gitignore              # Lista de ficheros y directorios ignorados para commits
├── .pre-commit-config.yaml # Lista de comandos de comprobación previa a un commit
├── .python-version         # Versión de Python fijada para el proyecto
├── AGENTS.md               # Reglas de conducta y guía para agentes IA
├── LICENSE                 # Licencia MIT
├── pyproject.toml          # Configuración del proyecto, scripts, ruff, ty y pytest
├── README.md               # Guía de uso y comandos del proyecto
└── uv.lock                 # Versiones exactas de dependencias (se versiona)
```

## Licencia

[MIT](LICENSE).
