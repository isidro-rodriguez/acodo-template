# PyPlate

Plantilla de proyectos **Python >= 3.13**.

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
uv run dev.py --help            # Lista todos los comandos de desarrollo

uv run dev.py check             # Calidad completa: format, lint, tipado y tests
uv run dev.py check --lint --types  # Solo algunas (--format --lint --types --tests)
uv run dev.py api               # Documentación de la API en el navegador (pdoc)
uv run dev.py api -p ruta -o docs/api   # Otra ruta y/o generar el HTML en un directorio

uv run dev.py backup            # Copia de seguridad en .local/backup.zip
uv run dev.py code-count        # Conteo de líneas de código y docstrings
uv run --group build dev.py build   # Empaqueta la aplicación
uv run dev.py gh-token access   # Token de instalación de una GitHub App
uv run dev.py gh-token test     # Comprueba el acceso al repositorio

uvx pre-commit run --all-files  # Ejecutar secuencia pre-commit
```

Cada comando de `scripts/` también se puede ejecutar por separado
(`uv run python scripts/backup.py`). `check` equivale a ejecutar
`ruff format`, `ruff check --fix`, `ty check` y `pytest`, sin detenerse en el
primer fallo y con un resumen final.

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

## 📁 Estructura del Proyecto

```bash
.
├── .github/                # Configuración y automatizaciones de GitHub
│   ├── workflows/              # Definiciones de flujos de GitHub Actions
│   │   └── ci.yml                  # Pipeline de integración continua: lint, tipado, tests
│   └── dependabot.yml          # Actualizaciones automáticas (GitHub Actions y uv)
├── .local/                 # Ficheros locales privados (ignorado por git)
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
├── dev.py                  # CLI de desarrollo: scripts, API (pdoc) y control de calidad
├── LICENSE                 # Licencia MIT
├── pyproject.toml          # Configuración del proyecto, scripts, ruff, ty y pytest
├── README.md               # Guía de uso y comandos del proyecto
└── uv.lock                 # Versiones exactas de dependencias (se versiona)
```

## Licencia

[MIT](LICENSE).
