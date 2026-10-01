# Python Boilerplate

Boilerplate moderno y minimalista para proyectos en Python (3.13), optimizado para `uv`, `ruff`, `pytest`, `mypy`.

---

## 🚀 Instalación y Configuración

```bash
uv sync     # Crear entorno virtual e instalar dependencias
uv venv     # Crear manualmente solo el entorno virtual
```

---

## 🛠️ Comandos Habituales

```bash
uv run main                         # Ejecutar el script principal
uv run ruff check                   # Analizar errores de código
uv run ruff check --fix             # Lint automático
uv run ruff format                  # Formateado automático según PEP 8
uv run ty check                     # Comprobar tipado estricto
uv run pdoc .\src\ -d google        # Documentación rápida en HTML
uv run pytest                       # Ejecutar la suite de pruebas unitarias
uv add --dev pytest-cov             # Añadir una dependencia de desarrollo
uv remove pytest-cov                # Eliminar una dependencia instalada
uv run pre-commit run --all-files   # Ejecutar secuencia pre-commit
uv lock                             # Actualizar `uv.lock`
```

---

## 📁 Estructura del Proyecto

```bash
.
├── src/
│   └── python_boilerplate/
│       ├── __init__.py
│       └── main.py          # Lógica del punto de entrada
├── tests/
│   └── test_main.py         # Pruebas unitarias con pytest
├── .gitignore               # Lista de ficheros y directorios ignorados para commits
├── .pre-commit-config.yaml  # Lista de comandos de comprobación previa a un commit
├── AGENTS.md                # Reglas de conducta y guía para agentes IA
├── pyproject.toml           # Configuración del proyecto, scripts, ruff y pytest
└── README.md                # Guía de uso y comandos del proyecto
```
