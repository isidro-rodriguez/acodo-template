# AGENTS.md

## Language

- **Code and identifiers in English**: variables, functions, constants, classes, methods,
  parameters, modules, and tests.
- **Documentation in Spanish**: docstrings, comments, error messages, README, docs, and commits.
- User-facing error messages must be in Spanish. Exception names and internal identifiers must
  be in English.
- This file, `AGENTS.md`, is written in English so the agent does not need to translate
  instructions.

## Expected structure (standalone Python project with uv)

```bash
.
├── .github/                # GitHub Actions CI
├── .pre-commit-config.yaml # pre-commit/pre-push hooks (ruff, ty, pytest, zensical)
├── .python-version         # Python version pin
├── AGENTS.md               # This file
├── CHANGELOG.md            # Keep a Changelog (Spanish)
├── LICENSE                 # MIT
├── pyproject.toml          # Project: deps, build, tools (ruff, ty, pytest, uv)
├── py.typed                # PEP 561 marker
├── README.md               # Project documentation
├── src/
│   └── <package>/          # Source code (rename "acodo_template" to your name)
│       ├── resources/      # Static assets
│       ├── __init__.py     # Exposes __version__ via importlib.metadata
│       ├── __main__.py     # python -m <package>
│       ├── main.py         # CLI entry point
│       └── py.typed        # Distributed with package
└── tests/                  # Tests with pytest
```

- Every `__init__.py` must include a short docstring describing the module or package.
- The project uses `uv` as dependency manager and build backend.
- `acodo-framework` is a runtime dependency; `acodo-cli` is in the `dev` dependency group.

## Project rules (load-bearing)

- **One `uv.lock` and one venv** at the project root.
- **Use `uv sync`** (not `--all-packages`): resolves the current project and its `dev` group.
- **Run tools from the root** so they cover all code.
- Package dependencies go in its `pyproject.toml` (`dependencies` and `dependency-groups.dev`).
- To add dependencies: `uv add <pkg>` (runtime) or `uv add --dev <pkg>` (dev).

## Tools and canonical commands

Do not use `pip install` directly.

```bash
uv sync
uv run ruff format .
uv run ruff check .
uv run ty check
uv run pytest
```

Documentation (Zensical, optional):

```bash
uv run zensical build       # build the site
uv run zensical serve       # local preview
```

If a tool is missing, install it in the `dev` group:

```bash
uv add --dev <tool>
```

## Agent workflow

1. Before changing, read `README.md`, `pyproject.toml`, `AGENTS.md`, and related tests.
2. Make the smallest necessary change. Do not refactor unrelated code.
3. If you need a new dependency, justify it. If stdlib solves it, do not add it.
4. Do not modify CI, global config, or structure unless the task requires it.
5. Before finishing, run quality commands from the root and fix until they pass.
6. If something fails and you cannot resolve it, show the exact error and propose the minimal fix.
7. Do not leave secrets, temporary files, or TODOs without context.

## Code rules

- Follow PEP 8 and Pythonic style with strict type annotations.
- Use `acodo-framework` (module `acodo`) as the utility library.
- Google-style docstrings for public identifiers: complete, with examples when they add value.
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
- Tests must pass on Linux and Windows.
- Test files live in `tests/`. Run `uv run pytest` from the root.

## CI

- GitHub Actions on `ubuntu-latest` and `windows-latest`.
- Minimum steps from the root:
    - `uv sync`
    - `uv run ruff format --check .`
    - `uv run ruff check .`
    - `uv run ty check`
    - `uv run pytest`
- Python version declared in `pyproject.toml` / `.python-version`.
- Use `astral-sh/setup-uv` to install `uv`.

## Commits

- Never commit automatically; report success and wait for confirmation.
- Use Conventional Commits in Spanish.
- Examples:
    - `feat: añade cálculo de totales`
    - `fix: corrige validación de entrada`
    - `docs: actualiza CHANGELOG para 0.1.1`
    - `test: cubre casos límite`
    - `chore: bump versión a 0.2.0`
- Atomic commit explaining the *why*, not just the *what*.
- Do not mix unrelated changes.

## Definition of done

A task is done when:

- `uv run ruff format --check .` passes without errors.
- `uv run ruff check .` passes without errors.
- `uv run ty check` passes without errors.
- `uv run pytest` passes without errors.
- Documentation and README updated if API or usage changes.
- Project version bumped in `pyproject.toml` and `CHANGELOG.md` updated (required before push).

## Versioning and changelog (pre-push)

Before any `git push` with code changes:

1. **Bump version** in `pyproject.toml` following SemVer:
    - **MAJOR**: breaking changes to public API.
    - **MINOR**: new backward-compatible functionality.
    - **PATCH**: bug fixes, internal refactors, docs affecting published package.
2. **Update `CHANGELOG.md`** (Keep a Changelog):
    - Entries under `## [Unreleased]` while working, or promote to `## [X.Y.Z] - YYYY-MM-DD` on
      bump.
    - Group under `### Added`, `### Changed`, `### Fixed`, `### Removed`, `### Deprecated`,
      `### Security`.
    - Write in Spanish, imperative or past tense, explaining the *why*.
3. **Lockfile consistency**: if bump changes dep constraints, update `pyproject.toml`, run
   `uv sync`, commit updated `uv.lock`.
4. **Atomic release commit** before push:
    - `chore: bump versión a X.Y.Z`
    - `docs: actualiza CHANGELOG para X.Y.Z`
      Or a single combined commit if change and release are inseparable.

If unsure whether a change is breaking, ask the user before choosing MAJOR. When in doubt between
PATCH and MINOR, prefer MINOR.

## Using `acodo-cli`

This template assumes `acodo-cli` is available (installed in the `dev` group via `uv sync`).

Useful commands during development:

```bash
uv run acodo check        # Verifies project quality (ruff, ty, tests)
uv run acodo <command>    # Other CLI commands
```

`acodo-cli` depends on `acodo-framework` at runtime; both come in the lockfile after `uv sync`.

## Limits

- Do not modify `AGENTS.md` without justified reason.
- Do not use `pip install` directly.
- Do not use `uv sync --all-packages` (for workspaces, not standalone projects).
- Do not add unnecessary dependencies.
- Do not change CI, Ruff, ty, pytest, or Zensical config without justification.
- Do not format files unrelated to the change.
- Do not rewrite code unnecessarily.
- If you cannot ask, choose the minimal change and document the assumption in the commit or PR.
