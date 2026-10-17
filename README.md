# PyPlate

Plantilla de proyectos **Python >= 3.13**.

Está optimizada para el uso de las herramientas de [Astral](https://astral.sh):
`uv`, `ruff` y `ty`.

Utiliza también las herramientas del framework Acodo:

- [Acodo CLI](https://github.com/isidro-rodriguez/acodo-cli)
- [Acodo utils](https://github.com/isidro-rodriguez/acodo-utils)

## 🚀 Instalación

`ruff` y `ty` están en el grupo `dev` de `pyproject.toml`, así que sus versiones
quedan fijadas en `uv.lock` y coinciden en local y en CI. `pdoc`se usan con `uvx`
(o instálalos globalmente con `uv tool install pdoc`).

```bash
uv sync    # Crea el entorno virtual e instala dependencias (grupo dev)
```

## 🛠️ Comandos Habituales

```bash
# Ejecutar la aplicación (también: python -m acodo_template)
uv run main

# Tooling de control de calidad
uv run ruff format --check # Formato
uv run ruff check # Lint
uv run ty check # Comprobación de tipos
uv run pytest # Pruebas 

# Ejecutar el CLI de Acodo
uv run acodo
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
│   ├── workflows/          # Definiciones de flujos de GitHub Actions
│   │   └── ci.yml          # Pipeline de integración continua: lint, tipado, tests
│   └── dependabot.yml      # Actualizaciones automáticas (GitHub Actions y uv)
├── .local/                 # Ficheros locales privados (ignorado por git)
├── src/                    # Código fuente del proyecto (layout src)
│   └── acodo_template/            # Paquete principal de Python
│       ├── resources/      # Recursos del paquete (iconos)
│       ├── __init__.py     # Marca acodo_template como paquete; expone la versión
│       ├── __main__.py     # Permite ejecutar con `python -m acodo_template`
│       └── main.py         # Lógica del punto de entrada
├── tests/                  # Pruebas del proyecto
│   └── test_main.py        # Ejemplo de prueba con pytest
├── .gitattributes          # Reglas de atributos Git: finales de línea, binarios, diffs, etc.
├── .gitignore              # Lista de ficheros y directorios ignorados para commits
├── .python-version         # Versión de Python fijada para el proyecto
├── AGENTS.md               # Reglas de conducta y guía para agentes IA
├── LICENSE                 # Licencia MIT
├── pyproject.toml          # Configuración del proyecto, scripts, ruff, ty y pytest
├── README.md               # Guía de uso y comandos del proyecto
└── uv.lock                 # Versiones exactas de dependencias (se versiona)
```

## Licencia

[MIT](LICENSE).
