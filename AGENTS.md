# Agent Guidelines — Python

Código simple, legible, stdlib antes que dependencias nuevas.

## Style (PEP8 + Ruff)

- Orden imports: stdlib > third-party > local.
- Sin mutable default args.
- Funciones: responsabilidad única, ~50 líneas como máximo.
- Nunca silenciar errores.

## Types & Docs

- Type hints estrictos (ty).
- Docstrings Google-style: completos en público, una línea en privado/anidado.
- Docstring público hereda `Raises` de las funciones privadas que llama.
- Comentarios explican el *porqué*, no el *qué*.

## Ahorro de tokens

- Previene bucles: no reintentes comandos fallidos más de 2 veces.
- Ahorra contexto con respuestas concisas.
- Cambios eficientes, prioriza manipulaciones en masa.

## Testing

- pytest, Arrange-Act-Assert.
- Testear parsers/calculadoras/edge cases, UI no.
- Crear directorio `temp/` para scripts, tests o ficheros temporales. BORRARLO AL FINALIZAR.

## Tooling

- `uv` para paquetes
- `ruff` para lint/format
- `pytest` para testeo
- `ty` para tipado

## Pre-commit checklist (orden estricto, detener en el primer fallo)

1. `uv run ruff check --fix`
2. `uv run ruff format`
3. `uv run ruff check`
4. `uv run ty check`
5. `uv run pytest`
