# acodo-template

Plantilla mínima para proyectos **Python >= 3.13**. Es una base independiente que se clona y
personaliza para iniciar un nuevo proyecto Python con las herramientas de
[Astral](https://astral.sh) (`uv`, `ruff` y `ty`).

Depende de `acodo-framework` y usa `acodo-cli` en desarrollo; ambos se instalan desde PyPI.
El repositorio se genera automáticamente desde el monorepo
[acodo](https://github.com/isidro-rodriguez/acodo) en cada versión: los cambios se hacen allí.

## 🚀 Instalación

Clona el repositorio y sincroniza las dependencias:

```bash
git clone https://github.com/isidro-rodriguez/acodo-template.git mi-proyecto
cd mi-proyecto
uv sync
```

## 🛠️ Uso

```bash
uv run main           # Imprime el logo (también: python -m acodo_template)
python -m acodo_template
```

### Comandos de calidad

El `pyproject.toml` incluye la configuración de Ruff, ty y pytest y sus dependencias de
desarrollo. Ejecuta:

```bash
uv run ruff format .
uv run ruff check .
uv run ty check
uv run pytest
```

## 📁 Estructura del repositorio

```bash
mi-proyecto/
├── .github/
│   └── workflows/
│       └── ci.yaml           # GitHub Actions: lint, tipos, tests (Linux/Win, Py 3.13/3.14)
├── .pre-commit-config.yaml   # Hooks pre-commit/pre-push (ruff, ty, pytest, zensical)
├── .python-version           # Versión de Python fijada (3.13+)
├── AGENTS.md                 # Instrucciones para agentes de código (este archivo adaptado)
├── CHANGELOG.md              # Historial de cambios (Keep a Changelog)
├── LICENSE                   # Licencia MIT
├── pyproject.toml            # Configuración del proyecto, deps, build, tools (ruff, ty, pytest)
├── py.typed                  # Marca el paquete como tipado (PEP 561)
├── README.md                 # Este archivo
├── src/
│   └── acodo_template/       # Paquete principal
│       ├── resources/        # Recursos estáticos (iconos)
│       │   ├── icon.ico
│       │   └── icon.png
│       ├── __init__.py       # Expone __version__ (leída de metadatos via importlib.metadata)
│       ├── __main__.py       # Permite `python -m acodo_template`
│       ├── main.py           # Punto de entrada CLI
│       └── py.typed          # Marca el paquete como tipado (distribuido)
└── tests/
    └── test_main.py          # Tests de ejemplo con pytest
```

Esta es la estructura inicial; ajústala a las necesidades de tu proyecto.

## Configuración incluida

El `pyproject.toml` incluye la configuración de:

- **Ruff** (`[tool.ruff.*]`): formato, lint, reglas de importación, target Python
- **ty** (`[tool.ty.*]`): comprobación de tipos estricta
- **pytest** (`[tool.pytest.*]`): opciones de test, coverage
- **uv build** (`[tool.uv.build-backend]`): backend de build con `module-name = "acodo_template"`
- **Entry point**: `main = "acodo_template.main:main"`

Personalízala según las necesidades de tu proyecto.

## Enlaces

- Repositorio de la plantilla: <https://github.com/isidro-rodriguez/acodo-template>
- Monorepo del que se genera: <https://github.com/isidro-rodriguez/acodo>
- Documentación de Acodo: <https://isidro-rodriguez.github.io/acodo/>
- PyPI: [`acodo-framework`](https://pypi.org/project/acodo-framework/) · [`acodo-cli`](https://pypi.org/project/acodo-cli/)

## Licencia

[MIT](LICENSE).