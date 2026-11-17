# Changelog

Todos los cambios relevantes de `acodo-template` se documentan en este fichero.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el
proyecto usa [Versionado Semántico](https://semver.org/lang/es/).

## [Unreleased]

## [0.4.0] - 2026-11-17

### Added

- `AGENTS.md` con el bloque de reglas compartidas de los proyectos Python (assistant-skills) y
  unas reglas de proyecto escritas para un proyecto derivado; `CLAUDE.md` solo lo importa
  (`@AGENTS.md`), así todos los agentes leen el mismo fichero.
- Bloques `template-only` en `README.md` y `AGENTS.md`: la skill `new-python-project` los
  elimina al crear un proyecto, de modo que el resultado no necesita retoques a mano.
- El README explica cómo crear un proyecto con la skill o con `scaffold.py`.
- `poe backup` usa `scripts/backup.py`, que funciona igual en Linux y Windows y deja
  `<proyecto>-<fecha>.bundle` en la raíz.

### Changed

- El comando de consola pasa de `main` a `acodo-template` (en un proyecto derivado, su
  nombre): un nombre genérico chocaba entre herramientas instaladas con `uv tool`.
- Dependencias de desarrollo al día: ruff 0.17.3, pytest 9.2.0 y ty 0.0.94.

### Fixed

- `.gitignore` ignora `*.bundle`: las copias de `poe backup` podían acabar en un commit.

### Removed

- `--error-on-warning` en el `ty check` de la CI: ty ya falla con avisos por defecto, así
  que el flag no añadía nada.
- Reglas obsoletas del antiguo `CLAUDE.md` (copias en `.local/`, carpeta `resources/`,
  `uv sync --all-packages`).

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
