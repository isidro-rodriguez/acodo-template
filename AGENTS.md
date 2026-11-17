# AGENTS.md

Instructions for AI agents working on **acodo-template**: plantilla mínima para proyectos Python 3.13+ con `acodo` y las herramientas de Astral (uv, ruff, ty).

The shared sections below are the same in every project. Project-specific rules are at the
end, under **Project rules**, and take precedence when they differ.

<!-- shared:start — managed by assistant-skills/new-python-project (scaffold.py sync). Edit there, not here. -->
## Shared rules

**Language.** Code and identifiers in English. Docstrings, comments, README, `docs/`,
CHANGELOG, commits and user-facing messages in Spanish. This file stays in English.

**Tools.** `uv` only, never `pip install`; run everything from the project root.
Quality gate: `uv run ruff format --check .`, `uv run ruff check .`, `uv run ty check`,
`uv run pytest`. The same gate as `poe check`, if Poe the Poet is installed globally; poe is
never a project dependency, and everything must also work with plain `uv run`.

**Workflow.**

1. Read `README.md`, `pyproject.toml`, this file and the related tests before changing code.
2. Make the smallest change that solves the task: no unrelated refactors, no formatting of
   untouched files, no new dependency without a reason (prefer the standard library).
3. Don't change CI, tool configuration or project structure unless the task needs it.
4. Don't run a failing command more than twice: stop, give the root cause and the exact error,
   propose the minimal fix and ask.
5. Don't run state-changing git commands (commit, push, tag, reset, rebase) unless the user
   asks or the commit policy in **Project rules** allows it. Never `--no-verify`.
6. Leave no secrets, temporary files or TODOs without context. Never hand-edit `uv.lock`.

**Code.** Strict type hints on every signature. Google-style docstrings: complete for public
identifiers, one line for private ones; a public docstring's `Raises` also lists the
exceptions raised by the private functions it calls. Comments explain the *why*. Prefer
simple, explicit code; `pathlib` over `os.path`. Ruff and ty enforce the rest; don't fight
them with ignores.

**Tests.** `pytest` in `tests/`. Cover relevant logic and every fixed bug; they must pass on
Linux and Windows.

**Commits.** Conventional Commits in Spanish (`feat:`, `fix:`, `docs:`, `test:`,
`refactor:`, `chore:`), one intent per commit, explaining the *why*.

**Releases.** Only for versioned projects (a real version and `CHANGELOG.md`). Before
pushing changes to the package, use the `python-release` skill. Without it: SemVer bump,
`## [Unreleased]` → `## [X.Y.Z] - YYYY-MM-DD` in `CHANGELOG.md`, `uv lock`, then
`chore: bump versión a X.Y.Z`. Never tag without confirmation.

**Done** when the quality gate and any extra gate in **Project rules** pass, and the README
and docs reflect any change in usage.

Project rules below take precedence over these. Shared rules change in assistant-skills
(`scaffold.py sync`), not by hand here.
<!-- shared:end -->

## Project rules

<!-- template-only:start -->
### This repository is the template

`acodo-template` is the starting point that the `new-python-project` skill
(assistant-skills) copies to create projects: it renames `acodo_template`/`acodo-template`,
resets the version and `CHANGELOG.md`, removes every `template-only` block (like this one)
and rebuilds this file from the rules below. So:

- Keep the names `acodo_template` and `acodo-template` everywhere; the scaffold replaces them.
- Write **Project rules** for a derived project, not for the template; anything that only
  applies to the template goes inside `<!-- template-only:start -->` /
  `<!-- template-only:end -->` blocks (here and in `README.md`).
- After changing the template, release it with the `python-release` skill.
<!-- template-only:end -->

### Structure

```
.
├── .github/                # CI (ubuntu + windows, Python 3.13 and 3.14) and Dependabot
├── .pre-commit-config.yaml # hooks: commit (format, lint, ty, tests), push (tests + coverage)
├── AGENTS.md               # This file (CLAUDE.md imports it)
├── CHANGELOG.md            # Keep a Changelog, Spanish
├── pyproject.toml          # Project, dependencies, tools and Poe tasks
├── uv.lock                 # Lockfile, tracked by git
├── scripts/backup.py       # poe backup: <project>-<timestamp>.bundle in the root (gitignored)
├── src/acodo_template/     # __init__ exposes __version__; __main__ and main.py (entry point)
└── tests/                  # pytest
```

- Python 3.13+. `acodo` is the utility library and the only runtime dependency: use it before
  writing helpers of your own.
- Run the app with `uv run acodo-template` or `uv run python -m acodo_template`.
- Every `__init__.py` has a short docstring. `README.md` stays minimal: what it is,
  installation, usage, quality commands and links.

### Extra quality gates

- Install the hooks once with `uv run pre-commit install`; they run the shared gate on commit
  and the tests with coverage on push.
- CI (`.github/workflows/ci.yaml`): `uv sync --locked`, the shared gate, and pytest with
  coverage uploaded to Codecov.

### Commit policy

Never commit automatically: report the result and wait for confirmation.

### Publishing

Not published: there is no publish workflow. The project is versioned (`CHANGELOG.md`), so
the shared **Releases** rules apply before pushing changes.
