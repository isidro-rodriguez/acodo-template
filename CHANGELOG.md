# Changelog

Todos los cambios relevantes de `acodo-template` se documentan en este fichero.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el
proyecto usa [Versionado Semántico](https://semver.org/lang/es/).

## [0.3.0] - 2026-10-24

### Added

- Tareas de [Poe the Poet](https://poethepoet.natn.io/) (`check`, `fix`, `backup`) como atajo
  opcional para quien tenga `poe` instalado globalmente; no es dependencia del proyecto.
- `uv.lock` versionado, para que la CI use exactamente las mismas versiones (`uv sync --locked`).

### Changed

- La plantilla pasa a ser un repositorio independiente que depende solo de la librería `acodo`
  (`acodo>=0.3,<1`), en lugar de generarse desde el monorepo y usar `acodo-cli`.
- README reducido a lo esencial; los detalles para agentes y desarrolladores pasan a `AGENTS.md`.

### Removed

- Referencias a `acodo-framework`, `acodo-cli`, Zensical y a ficheros que la plantilla no
  incluye (`.python-version`, `py.typed` en la raíz).
