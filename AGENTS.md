# AGENTS.md

## Language

- **Code and identifiers in English**: variables, functions, constants, classes, methods,
  parameters, modules, and tests.
- **Documentation in Spanish**: docstrings, comments, error messages, README, docs, and commits.
- User-facing error messages must be in Spanish. Exception names and internal identifiers must
  be in English.
- This file, `AGENTS.md`, is written in English so the agent does not need to translate
  instructions.

## Expected structure

```bash
.
├── .local/                 # Private local files, not tracked by git
├── scripts/                # Encapsulated utility scripts
├── src/                    # Source code
├── tests/                  # Pytest checks
├── .gitattributes          # Git attributes (line endings, binary handling)
├── .gitignore              # Git ignore rules
├── .pre-commit-config.yaml # Pre-commit hooks configuration
├── pyproject.toml          # Project metadata, dependencies, and tool config
├── README.md               # Minimal informative project overview
└── AGENTS.md               # Instructions for the agent
```

- Every `__init__.py` must include a short docstring describing the module or package.
- The README must be informative and minimal: what it is, installation, basic usage, and quality
  commands. Do not turn the README into an extensive manual.
- Do not modify this file (`AGENTS.md`) under any circumstance. If a task appears to require
  changing it, stop and ask the user.

## Tools and canonical commands

Do not use `pip install` directly.

```bash
uv sync
uvx ruff format .
uvx ruff check .
uvx ty check
uv run pytest
uvx pre-commit run --all-files
uvx pdoc -o docs/api src/<package>
```

If a tool is missing, ask developer:

```bash
uv add --dev <tool>
```

## Agent workflow

1. Before changing anything, read `README.md`, `pyproject.toml`, `AGENTS.md`, and the related
   tests.
2. Make the smallest necessary change. Do not refactor unrelated code.
3. If you need a new dependency, justify it. If the standard library can solve it, do not add it.
4. Do not modify CI, global configuration, or project structure unless the task requires it.
5. Before finishing, run the quality commands and fix until they pass.
6. If something fails and you cannot resolve it, show the exact error and propose the minimal fix.
7. Do not leave secrets, temporary files, or TODOs without context.

## Code rules

- Follow PEP 8 and Pythonic style with strict type annotations.
- Use Google-style docstrings for public identifiers: complete, with examples when they add value.
- For private identifiers, use brief docstrings.
- Do not repeat obvious things in docstrings or add unnecessary examples.
- Avoid overengineering. Prefer simple and explicit solutions.
- Keep functions and classes small, with clear English names.

Example of a public docstring:

```python
def sum_numbers(a: int, b: int) -> int:
    """Suma dos números enteros.

    Args:
        a: Primer número.
        b: Segundo número.

    Returns:
        La suma de ``a`` y ``b``.

    Examples:
        >>> sum_numbers(2, 3)
        5
    """
    return a + b
```

## Tests

- Use `pytest`.
- Cover relevant logic and fixed bugs.
- Do not chase 100% coverage. Prioritize useful and readable tests.
- Tests must run on Linux and Windows.

## CI

- GitHub Actions must work on `ubuntu-latest` and `windows-latest`.
- Minimum steps:
  - `uv sync`
  - `uvx ruff format .`
  - `uvx ruff check .`
  - `uvx ty check`
  - `uv run pytest`
- Use a supported Python version declared in `pyproject.toml`.
- You may use `astral-sh/setup-uv` to install `uv`.

## Commits

- Use Conventional Commits in Spanish.
- Examples:
  - `feat: añade cálculo de totales`
  - `fix: corrige validación de entrada`
  - `docs: actualiza ejemplos de uso`
  - `test: cubre casos límite`
  - `chore: configura pre-commit`
- A commit must be atomic and explain the why, not only the what.
- Do not mix unrelated changes.

## Definition of done

A task is done when:

- `uvx ruff format .` leaves no pending changes.
- `uvx ruff check .` passes without errors.
- `uvx ty check` passes without errors.
- `uv run pytest` passes.
- `uvx pre-commit run --all-files` passes.
- Documentation and README are updated if the API or usage changes.
- The commit is atomic and in Spanish.

## Limits

- Do not modify `AGENTS.md` under any circumstance.
- Do not use `pip install` directly.
- Do not add unnecessary dependencies.
- Do not change CI, Ruff, ty, pytest, or pdoc without justification.
- Do not format unrelated files.
- Do not rewrite code that is not necessary for the task.
- If you cannot ask, choose the minimal change and document the assumption in the commit or PR.
