# Changelog

Todos los cambios relevantes de `acodo-template` se documentan en este fichero.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el
proyecto usa [Versionado Semántico](https://semver.org/lang/es/).

## [0.2.1] - 2026-10-19

### Fixed

- El CI del repositorio independiente fallaba: usaba `uv sync --all-packages --locked` (sin `uv.lock`) y `--cov=packages`; ahora usa `uv sync --dev` y `--cov=src`.
- `pyproject.toml` declaraba `acodo-cli`/`acodo-framework` con `workspace = true`, inválido fuera del monorepo; el workflow de publicación elimina `[tool.uv.sources]` al sincronizar el repositorio.

### Changed

- El grupo `dev` incluye `pytest`, `pytest-cov`, `ruff`, `ty` y `pre-commit`, y el `pyproject.toml` lleva la configuración de Ruff, ty, pytest y coverage que el README ya anunciaba.
- Hook `pytest-cov` de pre-push apunta a `src`.
- README: sección «Enlaces» y aclaración de que el repositorio se genera desde el monorepo.

## [0.2.0] - 2026-10-19

### Added

- Configuración de publicación: `.gitattributes`, `.gitignore`, `.pre-commit-config.yaml`.
- CI/CD con GitHub Actions: workflow `ci.yaml` y Dependabot en `.github/dependabot.yml`.
- Documentación del agente: `AGENTS.md` con reglas del proyecto y comandos canónicos.
- README actualizado con instrucciones de uso de la plantilla.
- Configuración de IDE: `.idea/acodo.iml`.

## [0.1.0] - 2026-10-17

### Added

- Versión inicial dentro del workspace de Acodo, adaptada desde la plantilla independiente.

### Changed

- Depende de `acodo-framework` y usa `acodo-cli` en desarrollo, ambos como miembros del workspace.
- La versión se declara solo en `pyproject.toml` y se lee con `importlib.metadata`.
- Los colores del logo se asignan sin solapes de rango y los tests usan nombres en inglés.

### Fixed

- El `py.typed` estaba fuera del paquete y no se distribuía; ahora está en `src/acodo_template/`.