# Decision 01 — Repository Workflow

**Date:** 2026-08-27
**Status:** accepted

## Decision

The canonical repository is `https://github.com/eugenelin89/rocketsim.git`. The primary branch is `main`. For an approved task that changes repository files, the normal completion workflow is:

```text
implement
→ validate
→ implementation commit
→ record the implementation SHA and parent diff in the prompt record
→ prompt-record commit
→ push completed commits to origin/main
```

Routine completion pushes do not require separate conversational approval. Force pushes, history rewriting, destructive Git operations, discarding user work, and committing unrelated work remain prohibited. A push may be omitted only for a specific technical or repository-state blocker, which must be reported while preserving the local commits.

The portable platform baseline requires an isolated Python 3.12 environment with its own pip. On the primary development machine, that environment is the Miniconda environment named `rocketsim`, created with both `python=3.12` and `pip`. It is the only project-environment layer; no `venv` is nested inside it. Other developers may use an equivalent isolated Python 3.12 environment, including standard-library `venv`.

`pyproject.toml` remains the sole package and dependency declaration. Installations use `python -m pip`; Pygame is the runtime dependency, pytest is the development dependency, and the project uses a `src/` package layout.

## Context and problem

The starting directory contained project documentation but was not a Git repository and had no executable Python baseline. The project needs a reproducible environment and an explicit history-and-push workflow before flight code begins.

An initial repository-local `.venv` was created with Homebrew Python 3.12.12 before any commit. Homebrew's bundled `ensurepip` wheel was owned by another local user with restrictive permissions, so pip could not be installed normally. Although `get-pip.py` temporarily recovered that generated environment, the workaround was rejected as the canonical setup. Before the initial commit, the environment policy was corrected to use the project owner's established Miniconda workflow without changing machine-wide Homebrew files.

The older milestone documentation also describes a runnable Pygame window as part of Milestone 0. Prompt 01 is newer and more specific: it limits this task to repository and tooling setup and expressly defers the application loop and flight behavior. This decision applies that narrower scope.

## Options considered

- Use the primary machine's dedicated Miniconda `rocketsim` environment for isolation, Python 3.12, and pip while retaining `pyproject.toml` for all project dependencies.
- Keep the recovered Homebrew-created `.venv`, which would make a machine-specific permissions workaround part of the primary workflow.
- Require Conda for every developer, which would unnecessarily reduce portability.
- Nest a `venv` inside Conda, which would add a redundant environment layer and make interpreter provenance less clear.
- Build the older Milestone 0 application-loop deliverables now, which would exceed Prompt 01's explicit scope.

## Rationale

The selected baseline matches the primary machine's established environment manager while keeping the repository portable and `pyproject.toml` authoritative. Explicit `python -m pip` and `conda run -n rocketsim python ...` commands make interpreter provenance clear. The two-commit history preserves a reviewable implementation commit while keeping its prompt provenance separate.

## Consequences and tradeoffs

- The primary development machine must use the `rocketsim` Conda environment rather than Conda `base`, Homebrew Python, or a nested `venv`.
- Other developers remain free to use an equivalent isolated Python 3.12 environment.
- Conda manages only the environment, Python, and pip; project dependencies remain declared in `pyproject.toml`.
- Prompt records add repository history and storage overhead because they include implementation diffs.
- The repository is importable and testable, but it is intentionally not yet runnable as a simulator.
- Future changes that alter this workflow should supersede this record rather than silently editing its history.

## Related prompt records

- `docs/prompts/prompt_01_platform.md`

## Superseding decision

None.
