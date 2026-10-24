# acodo-template

Plantilla mínima para proyectos **Python >= 3.13** con [`acodo`](https://pypi.org/project/acodo/)
como biblioteca de utilidades y las herramientas de [Astral](https://astral.sh)
(`uv`, `ruff` y `ty`).

## 🚀 Instalación

```bash
git clone https://github.com/isidro-rodriguez/acodo-template.git mi-proyecto
cd mi-proyecto
uv sync
```

Renombra el paquete `acodo_template` y el proyecto en `pyproject.toml` a tu gusto.

## 🛠️ Uso

```bash
uv run main                 # o: uv run python -m acodo_template
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

- Plantilla: <https://github.com/isidro-rodriguez/acodo-template>
- Acodo: <https://github.com/isidro-rodriguez/acodo> · [documentación](https://isidro-rodriguez.github.io/acodo/)

## Licencia

[MIT](LICENSE).
