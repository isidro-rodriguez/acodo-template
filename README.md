# acodo-template

<!-- template-only:start -->
Plantilla mínima para proyectos **Python >= 3.13** con [`acodo`](https://pypi.org/project/acodo/)
como biblioteca de utilidades y las herramientas de [Astral](https://astral.sh)
(`uv`, `ruff` y `ty`).

## 🧩 Crear un proyecto

Con un agente que tenga la skill
[`new-python-project`](https://github.com/isidro-rodriguez/assistant-skills/tree/main/skills/new-python-project),
basta con pedirlo: «crea un proyecto Python llamado `mi-cli` para…». O directamente con su
script:

```bash
python scaffold.py new mi-cli --dest mi-cli --description "Qué hace el proyecto."
```

Copia la plantilla, renombra el paquete, el proyecto y el comando, deja la versión en 0.1.0
con un `CHANGELOG.md` nuevo, genera `AGENTS.md`/`CLAUDE.md` con las reglas compartidas y
quita los bloques propios de la plantilla (como este).
<!-- template-only:end -->

## 🚀 Instalación

```bash
git clone https://github.com/isidro-rodriguez/acodo-template.git
cd acodo-template
uv sync
uv run pre-commit install   # hooks de commit y push (opcional)
```

## 🛠️ Uso

```bash
uv run acodo-template       # o: uv run python -m acodo_template
```

## ✅ Calidad

```bash
uv run ruff format .
uv run ruff check .
uv run ty check
uv run pytest
```

### Atajos con poe (opcional)

Si tienes [Poe the Poet](https://poethepoet.natn.io/) instalado globalmente
(`uv tool install poethepoet`):

```bash
poe check    # formato, lint, tipos y tests
poe fix      # aplica formato y correcciones de Ruff
poe backup   # git bundle del repositorio
```

## Enlaces

- Acodo: <https://github.com/isidro-rodriguez/acodo> · [documentación](https://isidro-rodriguez.github.io/acodo/)
- Reglas para agentes: [AGENTS.md](AGENTS.md)

## Licencia

[MIT](LICENSE).
