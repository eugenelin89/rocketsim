# Prompt 01 — Platform Baseline

**Recorded:** 2026-08-27T10:48:05-07:00
**Scope:** platform
**Implementation commit:** `a0ae3e626744e61ce8ba2a80e5565990699fa190`
**Implementation commit message:** `Initialize rocket simulator repository baseline`
**Diff type:** root-commit patch (the repository had no parent commit)

## Chronology

1. The original Prompt 01 requested a minimal, implementation-ready repository baseline using Python 3.12, a repository-local `.venv`, Pygame, pytest, a `src/` package layout, documentation, and a two-commit Git/prompt-history workflow.
2. Work began, Git was initialized on `main`, `origin` was configured, repository files were prepared, and a Homebrew-created `.venv` was attempted. Work stopped before any commit or push.
3. Homebrew Python 3.12.12 could create the environment executables, but its bundled `ensurepip` wheel was unreadable because it belonged to another local user with restrictive permissions. Pip was temporarily recovered inside `.venv` with the official `get-pip.py`.
4. Before any repository history was committed, the user corrected the environment strategy. The workaround-based `.venv` was rejected as the canonical development environment.
5. The final accepted baseline requires an isolated Python 3.12 environment with its own pip. The primary development machine uses the Miniconda environment `rocketsim`, created explicitly with `python=3.12` and `pip`, with no nested `venv`.
6. Dependencies were installed with `python -m pip` from `pyproject.toml`, all validation ran explicitly through `conda run -n rocketsim python ...`, and the implementation was committed as the repository root commit.

## Starting repository state

- The directory contained `AGENTS.md`, `Pygame_Rocket_Simulator_Project_Context.md`, `README.md`, and six supporting documents under `docs/`.
- The directory was not initially a Git repository.
- The canonical GitHub repository was reachable and empty.
- No pre-existing prompt or decision records existed.
- No rocket simulator implementation existed.

## Context and constraints

- Preserve the existing project documents and keep the task limited to Prompt 01 repository/platform setup.
- Do not implement a Pygame application loop, rendering, rocket state, physics, telemetry, or future subsystems.
- Use Python 3.12 in an isolated environment.
- On the primary machine, use the Miniconda environment `rocketsim` with both Python and pip.
- Do not use Conda `base`, Homebrew Python, system Python, user-global Python, or a nested Conda-plus-`venv` environment for project work.
- Keep `pyproject.toml` as the canonical package and dependency declaration.
- Preserve the implementation commit and prompt-record commit as separate history.
- Push routine completed work to `origin/main` without force pushing or rewriting history.

## Decisions made

- The repository uses Python 3.12, a `src/` package layout, Pygame as its only runtime dependency, and pytest as its only development dependency.
- The portable requirement is any isolated Python 3.12 environment with its own pip; Miniconda is a primary-machine recommendation, not a universal repository requirement.
- The primary machine uses `/Users/eugenelin/.conda/envs/rocketsim/bin/python`; dependencies are installed with `python -m pip`.
- The generated Homebrew-based `.venv` was moved to Trash after verifying that it contained only generated environment files. `.venv/` remains ignored for developers who use standard-library `venv` elsewhere.
- The newer, more specific Prompt 01 scope overrides the older Milestone 0 wording that mentions a runnable Pygame window. Application and flight behavior remain deferred.
- Repository history uses an implementation commit followed by a separate prompt-record commit, then a push to `origin/main`.

## Implementation summary

- Initialized Git on `main` and configured `origin` as `https://github.com/eugenelin89/rocketsim.git`.
- Added Python packaging metadata and dependency declarations in `pyproject.toml`.
- Added the importable `rocket_sim` package and one pytest baseline test.
- Added Python/Pygame/macOS ignore rules.
- Added the implementation-oriented project understanding and accepted repository-workflow decision.
- Updated `README.md` and `AGENTS.md` with the corrected Conda/portable-environment policy and canonical Git workflow.
- Preserved and committed the original project documentation.
- Created the external Miniconda environment `rocketsim`, installed the editable project and dependencies, and validated interpreter provenance and package operation.
- Implemented no rocket physics or Pygame application functionality.

## Files created by Prompt 01

- `.gitignore`
- `pyproject.toml`
- `src/rocket_sim/__init__.py`
- `tests/test_package.py`
- `docs/product/PROJECT_UNDERSTANDING.md`
- `docs/decisions/decision_01_repository_workflow.md`

## Existing files modified

- `AGENTS.md`
- `README.md`
- `Pygame_Rocket_Simulator_Project_Context.md` (one trailing-whitespace cleanup for `git diff --check`)

## Existing files preserved and included in the root commit

- `docs/ARCHITECTURE.md`
- `docs/MILESTONES.md`
- `docs/PHYSICS_MODEL.md`
- `docs/PROJECT_BRIEF.md`
- `docs/RESEARCH_LOG.md`
- `docs/VALIDATION.md`

## Files deleted or removed

- No repository source or documentation file was deleted.
- The generated repository-local `.venv/` was removed from the working tree by moving it to `/Users/eugenelin/.Trash/rocketsim-venv-prompt01-20260827`. It was never committed.

## Validation

Environment creation and installation:

```bash
conda create -y -n rocketsim python=3.12 pip
conda run -n rocketsim python -m pip install --upgrade pip
conda run -n rocketsim python -m pip install -e ".[dev]"
```

Verified results:

- Conda version: 25.7.0
- Environment: `rocketsim`
- Python: 3.12.14
- Python executable: `/Users/eugenelin/.conda/envs/rocketsim/bin/python`
- pip: 26.2.1 from `/Users/eugenelin/.conda/envs/rocketsim/lib/python3.12/site-packages/pip`
- Pygame: 2.6.1
- pytest: 8.4.2
- `rocket_sim`: imported successfully; version 0.1.0
- pytest: 1 test passed
- `.venv`: absent from the repository and still covered by `.gitignore`
- `git diff --cached --check`: passed before the implementation commit
- Secret scan: no credential patterns found
- Staging audit: no environments, caches, credentials, generated package metadata, unrelated files, or physics code were committed

Validation commands:

```bash
conda info --envs
conda run -n rocketsim python --version
conda run -n rocketsim python -c "import sys; print(sys.executable)"
conda run -n rocketsim python -m pip --version
conda run -n rocketsim python -c "import pygame; print(pygame.version.ver)"
conda run -n rocketsim python -c "import pytest; print(pytest.__version__)"
conda run -n rocketsim python -c "import rocket_sim; print(rocket_sim.__version__)"
conda run -n rocketsim python -m pytest
conda run -n rocketsim python -m pip show pygame
conda run -n rocketsim python -m pip show pytest
git diff --cached --check
```

Validation used the `rocketsim` Conda interpreter explicitly. It did not use Conda `base`, the removed `.venv`, Homebrew Python, system Python, or user-global Python.

## Commit and push metadata

- Implementation commit: `a0ae3e626744e61ce8ba2a80e5565990699fa190`
- Implementation message: `Initialize rocket simulator repository baseline`
- Commit type: root commit; no parent exists
- Branch: `main`
- Remote: `origin https://github.com/eugenelin89/rocketsim.git`
- Push status at prompt-record creation: pending the required separate prompt-record commit
- Required next action: commit this record as `Record prompt 01 platform implementation`, then push both commits with `git push -u origin main`

## Original Prompt 01 — verbatim

~~~~~~text
Work in the repository:

```text
/Users/eugenelin/dev/cwsf2027/rocketsim
```

Canonical GitHub repository:

```text
https://github.com/eugenelin89/rocketsim.git
```

This is **Prompt 01**, the first implementation task for the CWSF 2027 Pygame rocket simulator project.

The purpose of this task is to establish a clean, reproducible, version-controlled repository baseline before any rocket-flight physics is implemented.

---

# 1. Required reading and inspection

Before making any changes:

1. Read `AGENTS.md` completely.
2. Read `Pygame_Rocket_Simulator_Project_Context.md` completely.
3. Read the current `README.md`.
4. Read the supporting project documents in `docs/`, especially:

   * `docs/PROJECT_BRIEF.md`
   * `docs/ARCHITECTURE.md`
   * `docs/MILESTONES.md`
   * `docs/PHYSICS_MODEL.md`
   * `docs/VALIDATION.md`
   * `docs/RESEARCH_LOG.md`
5. Inspect the complete current repository tree.
6. Inspect whether this directory is already a Git repository.
7. If it is a Git repository, inspect:

   * current branch
   * Git status
   * existing commits
   * existing remotes
8. Preserve all existing files and unrelated user work.
9. Do not assume the repository matches the approximate structure below; verify the actual working tree first.

If the canonical documents disagree with one another, do not silently choose one interpretation. Prefer the most specific/current repository rule and document any meaningful ambiguity.

---

# 2. Goal

Establish a clean, minimal, implementation-ready repository baseline for **Milestone 0**.

The completed repository should have:

* a proper Python project configuration
* a repository-local Python virtual environment
* minimal dependencies
* an importable `rocket_sim` package
* pytest infrastructure
* appropriate Git ignore rules
* implementation-oriented project documentation
* prompt and decision history directories
* Git initialized and configured
* the GitHub repository configured as `origin`
* the local primary branch named `main`
* all completed work committed according to `AGENTS.md`
* the prompt record committed separately
* all resulting commits pushed successfully to `origin/main`

This task should prepare the repository for Prompt 02.

**Do not implement rocket-flight physics in this task.**

---

# 3. Current repository

The repository currently contains approximately:

```text
rocketsim/
├── AGENTS.md
├── Pygame_Rocket_Simulator_Project_Context.md
├── README.md
└── docs/
    ├── ARCHITECTURE.md
    ├── MILESTONES.md
    ├── PHYSICS_MODEL.md
    ├── PROJECT_BRIEF.md
    ├── RESEARCH_LOG.md
    └── VALIDATION.md
```

Verify this before editing.

Do not remove or replace these documents.

---

# 4. Target repository structure

Create only the structure justified by the current milestone.

The repository should end approximately as:

```text
rocketsim/
├── AGENTS.md
├── Pygame_Rocket_Simulator_Project_Context.md
├── README.md
├── .gitignore
├── pyproject.toml
│
├── src/
│   └── rocket_sim/
│       └── __init__.py
│
├── tests/
│
└── docs/
    ├── ARCHITECTURE.md
    ├── MILESTONES.md
    ├── PHYSICS_MODEL.md
    ├── PROJECT_BRIEF.md
    ├── RESEARCH_LOG.md
    ├── VALIDATION.md
    │
    ├── product/
    │   └── PROJECT_UNDERSTANDING.md
    │
    ├── prompts/
    │
    └── decisions/
```

Do not create speculative future subsystem directories merely because they appear in long-term architecture discussions.

In particular, do **not** create empty future directories such as:

```text
physics/
rendering/
app/
motors/
environment/
experiments/
config/
```

unless something in this task creates a concrete need for one.

Those structures should emerge when implementation actually requires them.

Prefer architecture that grows from concrete milestones rather than a large pre-created hierarchy.

---

# 5. Python baseline

Establish a simple Python baseline appropriate for this project.

Use:

* Python 3.12
* standard-library `venv`
* repository-local `.venv`
* Pygame for interactive visualization
* pytest for testing
* `src/` package layout
* package name `rocket_sim`
* `pyproject.toml` as the canonical project and dependency configuration

Keep dependencies minimal.

Do not add:

* NumPy
* SciPy
* pandas
* matplotlib
* game engines
* external physics engines
* numerical frameworks
* GUI frameworks beyond Pygame
* machine-learning libraries
* unnecessary development tools

unless this task genuinely requires them.

---

# 6. Python virtual environment

The project must use its own isolated Python virtual environment.

Use standard-library:

```text
venv
```

rather than Conda for this project baseline.

The virtual environment should be:

```text
.venv/
```

at the repository root.

If `.venv` does not already exist:

1. verify that Python 3.12 is available
2. create it using:

```bash
python3.12 -m venv .venv
```

Use the Python executable inside `.venv` for all project dependency installation, testing, and validation.

Prefer explicit commands such as:

```bash
.venv/bin/python -m pip ...
```

rather than relying on whatever Python happens to be active in the shell.

For interactive use, the environment may be activated with:

```bash
source .venv/bin/activate
```

but automated work should preferably use `.venv/bin/python` explicitly.

Do not install project dependencies into:

* system Python
* user-global Python
* Conda `base`
* another Conda environment
* another unrelated virtual environment

The shell may currently show Conda `(base)`. That does not make Conda `base` the project environment.

All project Python operations must use `.venv`.

Add:

```text
.venv/
```

to `.gitignore`.

Never commit `.venv`.

If Python 3.12 is genuinely unavailable, inspect available Python versions and report the issue rather than silently substituting a materially different version.

Make only the smallest justified adjustment if required.

---

# 7. `pyproject.toml`

Create a conventional, minimal `pyproject.toml`.

It should define:

* project/package metadata
* supported Python version
* runtime dependency on Pygame
* development dependency on pytest
* `src/` package discovery/configuration
* enough packaging configuration for editable installation

Prefer a setup that supports:

```bash
.venv/bin/python -m pip install -e ".[dev]"
```

Use `pyproject.toml` as the canonical dependency declaration.

Do not additionally introduce:

* `requirements.txt`
* Conda environment files
* Poetry
* Pipenv
* uv
* Hatch
* another dependency manager

unless a concrete repository requirement justifies it.

Avoid redundant tooling.

---

# 8. Dependency installation

After creating `.venv` and `pyproject.toml`, install the project using the project virtual environment.

Preferred workflow:

```bash
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e ".[dev]"
```

Do not install development dependencies globally.

Do not install them into Conda `base`.

---

# 9. `.gitignore`

Create an appropriate `.gitignore` for a Python/Pygame project on macOS.

It should ignore at least:

```text
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.coverage
htmlcov/
build/
dist/
*.egg-info/
.DS_Store
```

Also ignore appropriate IDE/editor-specific user state where useful.

Do not ignore:

* Python source
* documentation
* tests
* prompt records
* decision records
* research records
* validation records
* useful test fixtures
* reproducibility data that should belong in source control

Do not invent a broad generated-data ignore rule before such a generated-data location exists.

---

# 10. Minimal Python package

Create the minimum necessary package structure:

```text
src/
└── rocket_sim/
    └── __init__.py
```

The package should be importable after editable installation.

Do not implement physics yet.

Do not create placeholder classes or abstractions for future systems merely to make the project appear more complete.

If a minimal package version constant or similarly trivial package metadata is useful, that is acceptable.

---

# 11. Testing baseline

Establish enough testing infrastructure to prove the Python project is working correctly.

A minimal baseline test may verify that:

```python
import rocket_sim
```

works successfully from the installed development environment.

Do not write tests for physics that does not exist.

Do not create fake APIs solely so they can be tested.

The purpose of testing during Prompt 01 is to verify the repository/tooling baseline.

---

# 12. `docs/product/PROJECT_UNDERSTANDING.md`

Create:

```text
docs/product/PROJECT_UNDERSTANDING.md
```

This document should be an implementation-oriented snapshot of the repository as it actually exists after this task.

Keep it concise.

Include:

* project purpose
* current milestone
* current implementation status
* repository layout
* Python baseline
* supported Python version
* `.venv` strategy
* dependency strategy
* architecture boundaries
* physics/rendering separation
* SI-unit convention
* world-coordinate convention
* fixed-timestep requirement
* current tests
* explicit current non-goals
* immediate next implementation task

Do not copy the entire contents of `Pygame_Rocket_Simulator_Project_Context.md`.

The project-context file is canonical high-level context.

`PROJECT_UNDERSTANDING.md` should describe what is actually implemented and established in the repository now.

---

# 13. README

Review the existing `README.md`.

Update it only as necessary to accurately describe the now-established repository.

It should include enough information for a new developer to:

1. understand what the project is
2. know its current status
3. create `.venv`
4. activate `.venv` if desired
5. install the package/development dependencies
6. run the tests
7. find the detailed project documentation

Setup instructions should be similar to:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest
```

Use whatever exact commands match the resulting repository.

Do not duplicate the entire project-context document in README.

---

# 14. Architecture constraints to preserve

Although detailed simulation code is out of scope for Prompt 01, preserve the following established architecture principles:

* physics uses SI units internally
* world +x is right
* world +y is up
* gravity will act in -y
* Pygame screen coordinates must not become physics coordinates
* screen-coordinate inversion belongs at the rendering boundary
* simulation time must remain distinct from wall-clock/display time
* physics will initially use a fixed timestep
* rendering FPS must not determine simulation results
* the physics core should remain independent of Pygame wherever practical
* first flight dynamics will be 2D
* first rocket model will use constant mass
* new physical effects should be introduced incrementally
* physics must be validated, not merely visually inspected

Do not implement these systems yet.

---

# 15. Physics scope — explicitly out of scope

Do **not** implement any actual rocket flight dynamics in Prompt 01.

Do not implement:

* gravity integration
* rocket motion
* thrust
* launch angles
* burnout
* coast
* projectile motion
* ground collision
* trajectory rendering
* telemetry
* aerodynamic drag
* wind
* changing mass
* propellant consumption
* thrust curves
* atmosphere
* Mach calculations
* parachutes
* recovery
* orientation
* angular velocity
* torque
* stability
* center of pressure
* center of gravity calculations
* guidance
* control
* swarm behavior
* optimization

Prompt 01 is repository/platform setup only.

---

# 16. Prompt archive

Follow the prompt archive requirements in `AGENTS.md`.

Because this prompt causes repository changes, it must receive a prompt record.

Determine the next unused prompt ID.

This is expected to be approximately:

```text
docs/prompts/prompt_01_platform.md
```

but inspect first and use the actual next unused ID.

The prompt record must preserve this user implementation prompt verbatim.

It should also record, as required by `AGENTS.md`:

* date/time when practical
* relevant context
* constraints
* decisions made
* implementation summary
* files created
* files modified
* files deleted, if any
* validation performed
* implementation commit SHA
* implementation commit diff against its parent
* push status and relevant repository metadata where useful

Do not reconstruct historical prompt records for work that predates this policy.

---

# 17. Required implementation/diff workflow

The implementation commit and prompt-record commit must remain separate.

The required sequence is:

```text
user prompt
    ↓
repository changes
    ↓
validation
    ↓
implementation commit
    ↓
obtain implementation commit SHA
    ↓
generate implementation commit diff against parent
    ↓
complete prompt record with SHA + diff
    ↓
commit prompt record separately
    ↓
push both commits
```

After making and validating the implementation/documentation changes, create the implementation commit first.

A suitable message would be:

```text
Initialize rocket simulator repository baseline
```

After that commit:

1. obtain its commit SHA
2. generate its diff against its parent
3. place the implementation SHA and implementation diff in the prompt record
4. finish the prompt record
5. commit the prompt record separately

A suitable second commit message would be approximately:

```text
Record prompt 01 platform implementation
```

The prompt-record commit should not be folded into the implementation commit.

The implementation diff stored in the prompt record should be the diff of the **implementation commit**, not the later prompt-record commit.

---

# 18. Decision records

Ensure:

```text
docs/decisions/
```

exists.

Do not create decision records merely to populate the directory.

Create a decision record only if this task establishes or changes a meaningful durable decision.

Potential baseline decisions include:

* Python 3.12
* repository-local standard-library `.venv`
* `pyproject.toml` as canonical project/dependency configuration
* `src/` package layout
* Pygame as visualization layer
* pytest as testing baseline
* SI internal units
* physics/rendering separation
* fixed physics timestep independent of rendering FPS

However, many of these may already be explicitly established in the canonical project documents.

Avoid redundant decision records.

If they are already accepted and clearly documented, do not create duplicate records merely for bookkeeping.

If one genuinely new durable repository-platform decision is made during implementation, prefer one coherent decision record rather than several trivial ones.

---

# 19. Update repository Git/push policy in `AGENTS.md`

The project now has a canonical GitHub remote:

```text
https://github.com/eugenelin89/rocketsim.git
```

Update `AGENTS.md` only as necessary so that future agents have an explicit repository-specific rule:

For an approved task that changes repository files, the normal completed-task workflow for this repository is:

```text
implement
→ validate
→ implementation commit
→ record implementation SHA + parent diff in prompt record
→ prompt-record commit
→ push completed commits to origin/main
```

Once `origin` is established, routine completed task commits and their required prompt records should be pushed to:

```text
origin/main
```

without requiring a separate conversational approval for each routine push.

A push may be omitted only when there is a concrete reason such as:

* authentication failure
* network/connectivity failure
* permission failure
* remote conflict
* unsafe unrelated repository state
* another specific technical blocker

If a push cannot be completed, preserve the local commits and report the exact blocker.

Do not loosen any existing protections against:

* force pushing
* destructive Git operations
* rewriting published history
* discarding user work
* committing unrelated changes

Keep the change to `AGENTS.md` narrow and explicit.

---

# 20. Git initialization

Determine first whether the repository is already initialized.

If not:

```bash
git init
```

If it is already initialized, do not reinitialize it unnecessarily.

Inspect:

```bash
git status
git branch
git remote -v
git log --oneline --decorate -n 5
```

where applicable.

---

# 21. Canonical GitHub remote

The canonical GitHub repository is:

```text
https://github.com/eugenelin89/rocketsim.git
```

Inspect existing remotes:

```bash
git remote -v
```

If no `origin` exists, configure:

```bash
git remote add origin https://github.com/eugenelin89/rocketsim.git
```

If `origin` already exists and points to exactly:

```text
https://github.com/eugenelin89/rocketsim.git
```

leave it unchanged.

If `origin` already exists but points somewhere else:

* do not silently overwrite it
* inspect the situation
* report the conflict unless existing repository documentation clearly proves that changing it is safe and intended

Do not create unnecessary additional remotes.

---

# 22. Primary branch

The canonical primary branch is:

```text
main
```

Ensure the local primary branch is named `main`.

If necessary:

```bash
git branch -M main
```

Do not rename it unnecessarily if it is already `main`.

---

# 23. Git safety before commit

Before committing:

1. inspect `git status`
2. inspect the diff
3. inspect staged files
4. confirm `.venv/` is ignored
5. confirm no virtual-environment contents are staged
6. confirm no secrets or credentials are staged
7. confirm no caches are staged
8. confirm no unrelated files are included
9. run the required tests
10. run:

```bash
git diff --check
```

when practical

Never absorb unrelated pre-existing user work into the task.

Do not use destructive Git commands.

---

# 24. Required validation

At minimum, run the equivalent of:

```bash
.venv/bin/python --version
.venv/bin/python -m pip --version
.venv/bin/python -c "import pygame; print(pygame.version.ver)"
.venv/bin/python -c "import rocket_sim"
.venv/bin/python -m pytest
git diff --check
```

The exact commands may vary slightly if required by the final project configuration.

Report exact commands and outcomes.

Confirm that:

* `.venv/bin/python` is being used
* Pygame is installed in `.venv`
* pytest is installed in `.venv`
* `rocket_sim` imports successfully
* tests pass
* dependencies were not installed into Conda `base`

If Conda `(base)` remains active in the outer shell, that is acceptable as long as the project commands explicitly use `.venv`.

---

# 25. Commit implementation

After implementation and validation, inspect the final implementation diff.

Create the implementation commit.

Preferred commit message:

```text
Initialize rocket simulator repository baseline
```

Do not include unrelated changes.

Record the resulting implementation commit SHA.

Generate the implementation commit diff against its parent for inclusion in the prompt record.

For example, use an appropriate equivalent of:

```bash
git show --format=fuller --stat <implementation-sha>
git diff <implementation-sha>^ <implementation-sha>
```

Use the correct Git command if this is the repository's root commit and therefore has no ordinary parent.

If this is the root commit, record the root-commit diff in an appropriate equivalent form rather than failing because `<sha>^` does not exist.

---

# 26. Complete and commit prompt record

After the implementation commit exists:

1. complete `docs/prompts/prompt_01_platform.md` or the actual next prompt record
2. preserve this prompt verbatim
3. include the implementation commit SHA
4. include the implementation commit diff
5. include validation information
6. include the required implementation metadata

Then commit the prompt record separately.

Preferred message:

```text
Record prompt 01 platform implementation
```

After this commit, inspect:

```bash
git status
git log --oneline --decorate -n 5
```

The history should clearly show the implementation commit followed by the prompt-record commit.

---

# 27. Push to GitHub

After:

* implementation is complete
* validation passes
* implementation commit exists
* prompt record contains the implementation SHA and diff
* prompt-record commit exists
* working tree is clean
* remote configuration is correct
* branch is `main`

push the repository to GitHub.

For the first push, use:

```bash
git push -u origin main
```

This task is not considered complete until the completed commits have been pushed successfully, unless a concrete technical blocker prevents the push.

Do not:

* force push
* use `--force`
* use `--force-with-lease`
* rewrite history
* delete remote work
* create another GitHub repository
* change authentication configuration destructively
* commit credentials
* commit `.venv`

If push fails:

* preserve all local commits
* do not rewrite history to work around it
* report the exact error
* explain what remains local

---

# 28. Post-push verification

After a successful push, verify:

```bash
git status
git branch -vv
git remote -v
git log --oneline --decorate -n 5
```

Confirm:

* current branch is `main`
* local `main` tracks `origin/main`
* working tree is clean
* `origin` points to:

```text
https://github.com/eugenelin89/rocketsim.git
```

* the remote contains the completed implementation and prompt-record commits

Do not claim the push succeeded unless Git confirms it.

---

# 29. Scope discipline

Keep this task intentionally small.

The objective is a trustworthy repository foundation.

Prefer:

```text
small + explicit + validated
```

over:

```text
large + speculative + partially implemented
```

Do not implement future systems merely because they are described in project documentation.

Do not introduce abstractions before there is a concrete requirement for them.

Do not use Prompt 01 as an excuse to start Prompt 02.

---

# 30. Immediate next task after this one

Prompt 02 will implement the first actual physics milestone.

Expected Prompt 02 scope:

**2D constant-mass rocket flight with gravity and finite-duration constant thrust.**

That future task will likely introduce the first concrete divisions between:

* simulation state
* physics
* rendering/application loop

But those structures should be designed from the actual Prompt 02 requirements rather than pre-created speculatively here.

Prompt 02 should include analytical validation of the implemented motion equations.

Do not implement Prompt 02 during this task.

---

# 31. Completion report

When finished, provide a concise but complete report containing:

1. repository state discovered at the beginning
2. original repository tree
3. whether Git was already initialized
4. original branch, if applicable
5. original remotes, if applicable
6. files created
7. files modified
8. directories created
9. final repository tree
10. Python version used
11. `.venv` location
12. whether `.venv` was newly created or reused
13. dependency installation command
14. installed Pygame version
15. installed pytest version
16. confirmation that project dependencies were installed into `.venv`, not Conda `base`
17. testing commands and results
18. `git diff --check` result
19. whether `AGENTS.md` was updated with the canonical push workflow
20. durable decision records created, if any
21. implementation commit SHA and commit message
22. prompt record path
23. prompt-record commit SHA and commit message
24. canonical remote URL
25. final branch name
26. confirmation that local `main` tracks `origin/main`
27. confirmation that both required commits were pushed successfully
28. final `git status`
29. any unresolved issues or assumptions
30. the recommended exact scope for Prompt 02

Do not report success for steps that were not actually completed.
~~~~~~

## Corrective continuation — verbatim

~~~~~~text
Continue working in:

```text
/Users/eugenelin/dev/cwsf2027/rocketsim
```

Canonical GitHub repository:

```text
https://github.com/eugenelin89/rocketsim.git
```

This is a **continuation and correction of Prompt 01**, not a new implementation milestone.

Do not restart the project from scratch.

Do not discard the repository work already completed.

Do not implement rocket physics or Pygame application functionality.

The purpose of this continuation is to correct the Python environment strategy, update the currently uncommitted documentation to match that strategy, finish validation, and then complete the Prompt 01 Git/history/push workflow.

---

# 1. Important current state

Prompt 01 was stopped before any commits or pushes were made.

The following work has already been completed:

* Git was initialized.
* Current branch is `main`.
* `origin` was configured as:

```text
https://github.com/eugenelin89/rocketsim.git
```

* A `.venv` was created using Python 3.12.12.
* The `.venv` currently contains:

  * pip 26.2.1
  * Pygame 2.6.1
  * pytest 8.4.2
  * editable `pygame-rocket-simulator` package

Repository files already created include:

```text
.gitignore
pyproject.toml
src/rocket_sim/__init__.py
tests/test_package.py
docs/product/PROJECT_UNDERSTANDING.md
docs/decisions/decision_01_repository_workflow.md
```

Existing files already updated include:

```text
README.md
AGENTS.md
```

No rocket physics or Pygame application code has been implemented.

No commits have been created.

Nothing has been pushed.

Because this is a newly initialized Git repository, repository files are currently untracked/uncommitted.

Preserve all useful repository files already created or modified.

---

# 2. Environment issue discovered

The previously created `.venv` should **not** become the canonical project-development environment.

The attempted command:

```bash
python3.12 -m venv .venv
```

encountered an `ensurepip` failure.

Python 3.12.12 was available, but Homebrew's bundled pip wheel could not be read by the current user because the file was owned by another local user (`christopherlin`) with restrictive permissions.

The error was approximately:

```text
PermissionError:
.../ensurepip/_bundled/pip-25.3-py3-none-any.whl
```

The virtual environment's Python executables were created, but pip was missing.

The previous work recovered by downloading Python's official `get-pip.py` and bootstrapping pip into `.venv`.

That made `.venv` usable, but this workaround should **not** be adopted as the project's canonical environment setup.

Do not attempt to repair the Homebrew Python installation as part of this task.

Do not:

* change ownership of Homebrew files
* run broad `sudo chown` operations
* reinstall Homebrew
* reinstall Homebrew Python
* modify another user's files
* make machine-wide Python changes

The Homebrew Python ownership problem is outside this repository's scope.

---

# 3. Correct environment strategy

The project owner's normal Python version-management workflow uses **Miniconda**.

For the primary development machine, use a dedicated Conda environment:

```text
rocketsim
```

with:

```text
Python 3.12
pip
```

Create the environment explicitly with both Python and pip:

```bash
conda create -y -n rocketsim python=3.12 pip
```

Do **not** create a `venv` inside this Conda environment.

The intended structure is:

```text
Miniconda
    ↓
Conda environment: rocketsim
    ├── Python 3.12
    └── pip
         ↓
         pyproject.toml
         ↓
         pygame + pytest + editable rocket_sim package
```

Not:

```text
Conda environment
    ↓
nested .venv
    ↓
another Python environment
```

There should be only one active project-environment layer.

---

# 4. Portable project policy

Distinguish between the repository's portable requirement and the primary development-machine recommendation.

The repository-level requirement should be:

> Development must occur in an isolated Python 3.12 environment with pip available for installing the project from `pyproject.toml`.

On the primary development machine:

> Use the Miniconda environment named `rocketsim`, created with Python 3.12 and pip.

Other developers may use an equivalent isolated Python 3.12 environment, including standard-library `venv`, if their local Python installation supports it normally.

Therefore:

* do not make Miniconda a hard requirement for every future developer
* do not require nested Conda + `venv`
* do not use Conda `base` as the project environment
* do not install project dependencies globally
* do not use the problematic Homebrew Python as the primary project environment on this machine
* ensure the selected isolated environment has its own Python and pip

---

# 5. `pyproject.toml` remains canonical

Keep:

```text
pyproject.toml
```

as the canonical declaration of the project's Python package and dependencies.

Conda should provide:

* environment isolation
* Python 3.12
* pip

`pyproject.toml` should continue to define:

* project metadata
* supported Python version
* Pygame runtime dependency
* pytest development dependency
* editable package/install configuration

Do not replace `pyproject.toml` with:

* `environment.yml`
* `requirements.txt`
* Poetry
* Pipenv
* uv
* another dependency manager

unless a concrete future requirement justifies it.

For this task, do not add a Conda `environment.yml`.

The preferred setup on the primary development machine should be:

```bash
conda create -n rocketsim python=3.12 pip
conda activate rocketsim
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Always prefer:

```bash
python -m pip ...
```

over:

```bash
pip ...
```

so that pip is guaranteed to correspond to the same Python interpreter being used for the project.

---

# 6. Inspect before changing the environment

Before deleting the existing `.venv`, inspect the current state.

Run appropriate equivalents of:

```bash
git status
git branch
git remote -v
```

Then inspect the existing `.venv` provenance:

```bash
cat .venv/pyvenv.cfg
```

Record enough information to understand which Python installation created it.

Do not preserve the existing workaround-based `.venv` merely because it currently works.

Because `.venv` is generated environment state and no commits exist yet, it may be safely recreated/replaced without losing repository source work.

---

# 7. Inspect Conda availability

Determine whether Conda is available.

Run:

```bash
which conda
conda --version
conda info --envs
```

Do not assume the environment `rocketsim` does or does not already exist.

### If `rocketsim` does not exist

Create it explicitly with Python 3.12 and pip:

```bash
conda create -y -n rocketsim python=3.12 pip
```

### If `rocketsim` already exists

Inspect it before using it.

Verify:

```bash
conda run -n rocketsim python --version
conda run -n rocketsim python -m pip --version
conda run -n rocketsim python -c "import sys; print(sys.executable)"
```

Confirm that:

* Python is 3.12.x
* pip exists
* the interpreter belongs to the `rocketsim` Conda environment

Do not delete or recreate an existing `rocketsim` environment without first determining what it contains.

If an existing environment by that name clearly belongs to this project and uses the correct Python/pip baseline, reuse it.

If Python is correct but pip is missing, add pip to that environment using Conda rather than bootstrapping it from `get-pip.py`:

```bash
conda install -y -n rocketsim pip
```

If the existing environment is clearly unrelated or presents a conflict, stop and report the specific conflict rather than destructively replacing it.

---

# 8. Remove only the generated `.venv`

Once the Conda environment strategy has been verified and is viable, remove the generated repository-local:

```text
.venv/
```

Before doing so, ensure that `.venv` contains no user-authored source files.

Then remove only that generated environment:

```bash
rm -rf .venv
```

Do not remove any repository source or documentation files.

It is fine to leave:

```text
.venv/
```

in `.gitignore`.

That remains useful because another developer may choose standard-library `venv` on another machine.

---

# 9. Use the Conda environment explicitly

For automated work, prefer commands that make interpreter provenance explicit.

Use:

```bash
conda run -n rocketsim python ...
```

where practical.

This is preferable to relying solely on shell activation because it makes it clear which Python executes each command.

For example:

```bash
conda run -n rocketsim python --version
conda run -n rocketsim python -m pip --version
```

Interactive documentation may still tell a human developer to use:

```bash
conda activate rocketsim
```

followed by normal `python` commands.

Do not run project installation or validation using:

* Conda `base`
* Homebrew Python
* system Python
* user-global Python
* the removed `.venv`

---

# 10. Verify pip before dependency installation

Before installing project dependencies, explicitly verify that pip is installed inside the `rocketsim` Conda environment.

Run:

```bash
conda run -n rocketsim python -m pip --version
```

The output should indicate a pip installation associated with the `rocketsim` environment's Python.

If pip is unexpectedly missing, install it with:

```bash
conda install -y -n rocketsim pip
```

Then verify again:

```bash
conda run -n rocketsim python -m pip --version
```

Do not use `get-pip.py` for the Conda environment.

Do not use a pip executable from:

* Conda `base`
* Homebrew Python
* system Python
* another environment

---

# 11. Install project dependencies in `rocketsim`

Using the `rocketsim` Conda environment, install the project and development dependencies.

Use:

```bash
conda run -n rocketsim python -m pip install --upgrade pip
conda run -n rocketsim python -m pip install -e ".[dev]"
```

All project Python dependencies should be installed in the `rocketsim` environment.

Do not install them into Conda `base`.

Do not globally install them.

Do not add unnecessary dependencies.

After installation, verify package location where useful:

```bash
conda run -n rocketsim python -m pip show pygame
conda run -n rocketsim python -m pip show pytest
```

---

# 12. Update documentation before committing

Because nothing has yet been committed, update the currently uncommitted documentation so the initial Git history reflects the correct environment policy.

Review and update at least:

```text
AGENTS.md
README.md
docs/product/PROJECT_UNDERSTANDING.md
docs/decisions/decision_01_repository_workflow.md
```

Also inspect any other uncommitted file that mentions `.venv` as the mandatory or canonical environment.

Do not mechanically replace every occurrence of `.venv`, because `.venv` may still legitimately appear in `.gitignore` or as a portable alternative for other developers.

---

# 13. Required `AGENTS.md` environment policy

Update `AGENTS.md` narrowly so the environment rules are clear.

The resulting policy should express approximately:

### Python environment policy

* Development must use an isolated Python 3.12 environment.
* The isolated environment must have its own pip suitable for installing the project from `pyproject.toml`.
* On the primary development machine, use the Miniconda environment named `rocketsim`.
* Create that environment with:

```bash
conda create -n rocketsim python=3.12 pip
```

* Do not use Conda `base` as the project environment.
* Do not nest a Python `venv` inside the `rocketsim` Conda environment.
* `pyproject.toml` remains the canonical package/dependency configuration.
* Install the project into the active isolated environment using:

```bash
python -m pip install -e ".[dev]"
```

* Prefer `python -m pip` rather than bare `pip`.
* Other developers may use an equivalent isolated Python 3.12 environment, including standard-library `venv`.
* Project validation must make interpreter provenance clear.
* On the primary development machine, automated commands should preferably use:

```bash
conda run -n rocketsim python ...
```

* Do not install repository dependencies into:

  * Conda `base`
  * system Python
  * Homebrew Python
  * user-global Python

Do not weaken any existing Git, history, validation, prompt archive, decision archive, or safety policies.

---

# 14. Keep the established GitHub workflow in `AGENTS.md`

Preserve the repository-specific Git workflow already added to `AGENTS.md`.

The canonical remote is:

```text
https://github.com/eugenelin89/rocketsim.git
```

For approved tasks that modify repository files, the normal completed-task workflow remains:

```text
implement
→ validate
→ implementation commit
→ capture implementation SHA and parent/root diff
→ complete prompt record
→ prompt-record commit
→ push completed commits to origin/main
```

Routine completed task commits should be pushed to:

```text
origin/main
```

without requiring separate approval for each routine push.

Do not weaken protections against:

* force pushing
* history rewriting
* destructive Git commands
* committing unrelated work
* discarding user work

---

# 15. README environment instructions

Update README so that the primary-machine setup is clear.

The recommended setup should be:

```bash
conda create -n rocketsim python=3.12 pip
conda activate rocketsim
python --version
python -m pip --version
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest
```

Explain concisely that:

* `rocketsim` is the recommended environment on the primary Miniconda-based development machine
* Python 3.12 is required
* pip is installed as part of the Conda environment
* project dependencies come from `pyproject.toml`
* `python -m pip` should be used for installation
* a conventional isolated Python 3.12 `venv` is acceptable on other machines
* Conda `base` should not be used for project dependencies
* nested Conda + `venv` environments are unnecessary and should not be used

Do not include the machine-specific Homebrew permissions incident in the normal README setup instructions unless a concise troubleshooting note is clearly useful.

The README should explain how to use the repository, not become a machine-maintenance log.

---

# 16. `PROJECT_UNDERSTANDING.md`

Update:

```text
docs/product/PROJECT_UNDERSTANDING.md
```

so that it reflects the actual final state.

It should record:

* Python 3.12 baseline
* isolated-environment requirement
* primary-machine use of Conda environment `rocketsim`
* Conda environment explicitly includes pip
* no nested `venv`
* `pyproject.toml` as canonical dependency configuration
* Pygame runtime dependency
* pytest development dependency
* use of `python -m pip`
* no physics implementation yet
* next milestone remains Prompt 02 / first validated rocket physics

Keep this implementation-oriented and concise.

---

# 17. Decision record

Review the currently uncommitted:

```text
docs/decisions/decision_01_repository_workflow.md
```

Because there are **no commits yet**, this record has not become immutable project history.

Revise it directly if necessary so it accurately represents the initial accepted repository baseline.

Do not create a fake "Decision 02" merely to record a reversal of something that was never committed.

If `decision_01_repository_workflow.md` covers environment/tooling choices, update it to reflect:

* isolated Python 3.12
* primary-machine Conda environment `rocketsim`
* environment explicitly includes pip
* no nested `venv`
* `pyproject.toml` dependency management
* use of `python -m pip`
* Git/prompt/push workflow

If environment policy does not logically belong in that decision, do not force unrelated material into it. Instead follow the existing decision-archive rules and make the smallest coherent documentation choice.

---

# 18. Do not change project scope

Do not implement:

* Pygame application loop
* rocket rendering
* gravity integration
* thrust
* burnout
* coast
* trajectories
* telemetry
* drag
* wind
* variable mass
* motor thrust curves
* atmosphere
* recovery
* rotation
* stability
* guidance
* control

This remains Prompt 01 repository/platform setup.

No actual rocket simulation should be added.

---

# 19. Validate the corrected environment

After establishing the Conda environment and installing the project, validate explicitly using that environment.

Run:

```bash
conda run -n rocketsim python --version
conda run -n rocketsim python -c "import sys; print(sys.executable)"
conda run -n rocketsim python -m pip --version
conda run -n rocketsim python -c "import pygame; print(pygame.version.ver)"
conda run -n rocketsim python -c "import pytest; print(pytest.__version__)"
conda run -n rocketsim python -c "import rocket_sim"
conda run -n rocketsim python -m pytest
```

Verify that the printed Python executable belongs to the `rocketsim` Conda environment.

Also verify the environment inventory with:

```bash
conda info --envs
```

Where useful, verify installed project/package metadata with:

```bash
conda run -n rocketsim python -m pip show pygame
conda run -n rocketsim python -m pip show pytest
```

The validation report must clearly establish:

* Python version
* Python executable path
* Conda environment name
* pip version
* pip location/environment association
* Pygame version
* pytest version
* successful `rocket_sim` import
* pytest result

Explicitly confirm that validation did **not** use:

* Conda `base`
* the removed `.venv`
* Homebrew Python
* global Python

---

# 20. Review repository changes

Before committing:

```bash
git status
git diff
git diff --check
```

Also inspect untracked files.

Because this is a new repository with no commits, make sure the implementation commit will contain all intended baseline files.

Confirm:

* `.venv` is not present in the working tree
* `.venv/` is ignored
* the external Conda environment itself is not inside the repository
* no Conda environment files/directories are accidentally staged
* no credentials or secrets are present
* no caches are staged
* no unrelated files are staged
* no rocket-physics implementation has slipped into scope

---

# 21. Complete the implementation commit

Once environment correction, documentation correction, and validation are complete, create the Prompt 01 implementation commit.

Preferred message:

```text
Initialize rocket simulator repository baseline
```

Because this repository currently has no commits, this is expected to be the **root implementation commit**.

Include all intended repository baseline files in this implementation commit except the final prompt record that requires the implementation SHA/diff.

Do not include generated environment contents.

---

# 22. Root-commit diff handling

After creating the implementation commit, obtain its SHA.

Because it is expected to be the root commit, it may have no parent.

Do not fail by assuming:

```text
<sha>^
```

exists.

Generate an appropriate root-commit patch/diff, for example using a root-aware Git command such as:

```bash
git show --format=fuller --root <implementation-sha>
```

or another correct equivalent.

The prompt archive must contain the implementation commit's actual patch/diff in accordance with `AGENTS.md`.

Do not put the later prompt-record commit diff there instead.

---

# 23. Prompt 01 record

Create/complete the required Prompt 01 record under:

```text
docs/prompts/
```

Determine the correct next unused ID, but it is expected to be approximately:

```text
docs/prompts/prompt_01_platform.md
```

The prompt record must preserve the **original full Prompt 01 implementation request verbatim**.

Also preserve this continuation/correction as material follow-up context because it changed how Prompt 01 was implemented.

Do not replace the original Prompt 01 with only this continuation.

The record should make the chronology clear:

1. original Prompt 01 requested repository baseline using `.venv`
2. work began but stopped before commit
3. Homebrew `ensurepip` permissions issue was discovered
4. `.venv` was temporarily recovered using `get-pip.py`
5. before any commit, the user corrected the environment strategy
6. final accepted baseline uses isolated Python 3.12
7. the primary development machine uses Conda environment `rocketsim`
8. the Conda environment is explicitly created with both `python=3.12` and `pip`
9. no nested `venv` is used
10. dependencies are installed using `python -m pip`
11. final implementation was validated using the corrected Conda environment

Include all metadata required by `AGENTS.md`, including:

* implementation commit SHA
* implementation commit root diff/patch
* implementation summary
* files changed
* validation
* relevant environment issue/context
* decisions
* push information when completed

---

# 24. Commit the prompt record separately

After the prompt record contains the implementation SHA and root diff, commit it separately.

Preferred message:

```text
Record prompt 01 platform implementation
```

Do not amend the implementation/root commit merely to insert the prompt record.

The intended history should be:

```text
<implementation SHA>  Initialize rocket simulator repository baseline
<prompt SHA>          Record prompt 01 platform implementation
```

This separation is required by the repository workflow.

---

# 25. Push both commits

Verify:

```bash
git remote -v
git branch
```

The expected remote is:

```text
origin  https://github.com/eugenelin89/rocketsim.git
```

The expected branch is:

```text
main
```

If those are correct, push:

```bash
git push -u origin main
```

Do not force push.

Do not rewrite history.

Do not create another remote.

If the push fails, preserve both local commits and report the exact error.

---

# 26. Final Git verification

After a successful push, run:

```bash
git status
git branch -vv
git remote -v
git log --oneline --decorate -n 5
```

Confirm:

* current branch is `main`
* `main` tracks `origin/main`
* origin points to the canonical GitHub repository
* implementation commit exists
* prompt-record commit exists after it
* both are pushed
* working tree is clean

Do not report successful completion unless these checks support it.

---

# 27. Scope for Prompt 02

Do not start Prompt 02.

The next task should remain:

> Implement the first scientifically validated 2D constant-mass rocket model with gravity and finite-duration constant thrust.

Prompt 02 should introduce only the minimum architecture required by actual implementation.

It should include analytical validation.

It should not yet introduce drag, variable mass, atmosphere, recovery, or rotational dynamics.

---

# 28. Completion report

When finished, provide a concise but complete report containing:

1. Git/repository state found when this continuation began
2. `.venv` provenance found in `pyvenv.cfg`
3. Conda executable/version found
4. Conda environments found before changes
5. whether `rocketsim` already existed or was newly created
6. confirmation that `rocketsim` contains both Python and pip
7. final Python version
8. final Python executable path
9. final pip version
10. confirmation that pip belongs to the `rocketsim` environment
11. confirmation that the final project environment is Conda `rocketsim`
12. confirmation that no nested `venv` is used
13. confirmation that `.venv` was removed
14. confirmation that `.venv/` remains ignored
15. dependency installation command
16. Pygame version
17. pytest version
18. successful `rocket_sim` import
19. pytest result
20. confirmation that validation used `rocketsim`, not Conda `base`, Homebrew Python, or `.venv`
21. documentation files updated for the corrected environment policy
22. decision record status/change
23. `git diff --check` result
24. implementation/root commit SHA and message
25. prompt record path
26. confirmation that the original Prompt 01 and this corrective follow-up are both preserved appropriately
27. prompt-record commit SHA and message
28. final remote URL
29. final branch
30. upstream tracking state
31. confirmation that both commits were pushed to `origin/main`
32. final `git status`
33. any unresolved issues
34. recommended exact scope for Prompt 02

Do not claim any step succeeded unless it was actually performed and verified.
~~~~~~

## Implementation root-commit patch

~~~~~~diff
commit a0ae3e626744e61ce8ba2a80e5565990699fa190
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Thu Aug 27 10:46:57 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Thu Aug 27 10:46:57 2026 -0700

    Initialize rocket simulator repository baseline

diff --git a/.gitignore b/.gitignore
new file mode 100644
index 0000000..60423e3
--- /dev/null
+++ b/.gitignore
@@ -0,0 +1,18 @@
+.venv/
+
+__pycache__/
+*.py[cod]
+*$py.class
+
+.pytest_cache/
+.coverage
+htmlcov/
+
+build/
+dist/
+*.egg-info/
+
+.DS_Store
+.idea/
+.vscode/
+*.swp
diff --git a/AGENTS.md b/AGENTS.md
new file mode 100644
index 0000000..36be41b
--- /dev/null
+++ b/AGENTS.md
@@ -0,0 +1,372 @@
+# Agent Instructions
+
+These instructions apply to the entire repository.
+
+## Required Reading
+
+- Read this file before making repository changes.
+- Read `Pygame_Rocket_Simulator_Project_Context.md` before changing simulation behavior, physics assumptions, architecture, milestone scope, units, coordinate conventions, or validation criteria.
+- Read `docs/product/PROJECT_UNDERSTANDING.md` before implementation work once that file exists. It should record the current implementation-oriented understanding of the simulator and repository.
+- Read relevant records in `docs/decisions/` and relevant subsystem documentation before changing an established physics, architecture, numerical-method, rendering, or workflow decision.
+- Inspect the repository and working tree before editing. Documentation can become stale, so verify claims that depend on current code or configuration.
+
+## General Workflow
+
+- Keep changes scoped to the user's current request.
+- Do not implement future milestones, placeholder systems, or speculative abstractions unless explicitly requested.
+- Do not silently revise previously accepted physics assumptions or architecture decisions. If a decision changes, document the new decision and preserve the prior record.
+- Preserve existing behavior unless the task explicitly requests a behavior change, model change, or bug fix.
+- Preserve user changes and unrelated existing work. Never absorb unrelated work into a task commit.
+- Prefer small, testable milestones and inspect before editing.
+- Separate scientific-model changes from presentation/UI changes whenever practical.
+- If a proposed change affects numerical correctness, explain the expected physical consequence before implementation.
+
+## Scientific Modeling Policy
+
+- Every simulated force or state transition must have a clearly stated physical meaning.
+- Use SI units internally unless a documented decision explicitly says otherwise.
+- Keep units explicit in variable names, configuration, documentation, or type structure where practical.
+- Do not mix screen coordinates with simulation/world coordinates.
+- Do not mix physics timestep with rendering framerate.
+- Do not silently introduce empirical constants, tuning factors, or "game feel" adjustments into the physics model.
+- If a model is approximate, document the approximation and its expected limits.
+- Prefer simple models that can be analytically or numerically validated before adding realism.
+- New realism should be introduced one physical effect at a time when practical.
+- Do not present simplified 2D results as equivalent to full 3D flight dynamics.
+- Do not claim engineering-grade launch prediction without documented calibration, uncertainty analysis, and validation against real data.
+
+## Project Snapshot Policy
+
+- Do not generate or update a full-repository snapshot during normal work.
+- Prefer token-efficient historical records containing the user's prompt, implementation commit diff, and concise implementation metadata.
+- Do not store entire repository snapshots in prompt records.
+- Exclude `.git`, virtual environments, caches, build output, generated plots, replay data, exported frames, and unrelated scratch files from snapshot-style artifacts unless explicitly requested.
+- If simulation output is needed for a prompt record, store a concise summary or a small representative artifact rather than large raw datasets unless the dataset itself is the requested result.
+
+## Prompt Archive And Commit Policy
+
+When a user prompt causes any repository file to be created, modified, moved, or deleted:
+
+- Create a corresponding prompt record in `docs/prompts/`.
+- Use this filename format:
+
+  ```text
+  prompt_[ID]_[scope].md
+  ```
+
+- Use the next unused integer ID, zero-padded to two digits.
+- Choose the scope that the prompt primarily affects, such as `platform`, `physics`, `rendering`, `motor`, `atmosphere`, `validation`, `experiments`, or `docs`.
+- Use `platform` for repository-wide or cross-subsystem work.
+- Preserve the user's implementation prompt verbatim. Include material follow-up constraints or approvals that change how the prompt is implemented.
+- Record the date/time when practical, relevant context and constraints, decisions made, implementation summary, files created/modified/deleted, validation performed, implementation commit SHA, and the implementation commit diff against its parent.
+- Do not reconstruct prompt records for work that predates this policy unless the user explicitly requests it.
+- Commit requested implementation or documentation changes first with a concise, descriptive implementation commit.
+- Generate that commit's diff against its parent, then complete the prompt record with the commit SHA and diff.
+- Commit the prompt record separately.
+- If a meaningful durable decision is made, create or update its decision record and ensure it is committed as documentation, normally with the implementation it explains.
+- Never include unrelated pre-existing work in either commit.
+- Push when a remote exists and doing so is appropriate for the repository workflow. If no remote exists, record that no push was performed.
+- If unrelated changes make a safe path-scoped commit impossible, stop and explain the specific conflict rather than modifying, unstaging, or absorbing those changes.
+
+## Routine Commit Policy
+
+Once the user has approved a task or instructed Codex to implement it, routine commits are part of the normal workflow and do not require separate conversational approval.
+
+- Make the requested changes, run appropriate validation, review the resulting diff, and commit the implementation directly.
+- Create or update required prompt and decision records and commit them according to this policy.
+- Use sufficiently descriptive commit messages that identify the purpose and scope of the change.
+- Prefer messages such as:
+  - `Initialize Pygame rocket simulator repository`
+  - `Implement gravity and powered point-mass flight`
+  - `Add aerodynamic drag model and tests`
+  - `Add motor thrust-curve interpolation`
+  - `Separate simulation timestep from rendering framerate`
+  - `Add analytical trajectory validation`
+- Avoid vague messages such as `changes`, `update`, `fix stuff`, `misc`, or `work`.
+- For larger changes, use a concise subject and a useful body describing important physics, architecture, data, or validation implications.
+- Run non-destructive bookkeeping such as `git status`, `git diff`, `git add`, `git commit`, and `git log` without asking for separate conversational approval during an already-approved task.
+- This policy does not authorize destructive Git commands, discarding or overwriting user work, rewriting published history, force pushing, committing unrelated changes, or silently expanding task scope.
+
+## Repository Push Workflow
+
+The canonical remote for this repository is:
+
+```text
+https://github.com/eugenelin89/rocketsim.git
+```
+
+For an approved task that changes repository files, the normal completed-task workflow is:
+
+```text
+implement
+→ validate
+→ implementation commit
+→ record implementation SHA + parent diff in the prompt record
+→ prompt-record commit
+→ push completed commits to origin/main
+```
+
+Once `origin` is established, routine completed task commits and their required prompt records should be pushed to `origin/main` without requiring separate conversational approval for each push. A push may be omitted only for a concrete blocker such as authentication, connectivity, permission, remote conflict, or unsafe unrelated repository state. Preserve local commits and report the exact blocker.
+
+This workflow does not authorize force pushing, destructive Git operations, rewriting published history, discarding user work, or committing unrelated changes.
+
+## Decision Archive
+
+- Record meaningful durable project decisions in `docs/decisions/`.
+- Use this filename format:
+
+  ```text
+  decision_[ID]_[short_slug].md
+  ```
+
+- Each record must include the decision, date, status (`accepted`, `superseded`, or `reversed`), context/problem, options considered when relevant, rationale, consequences/tradeoffs, related prompt records, and any superseding decision.
+- Create a decision record when a choice materially constrains:
+  - coordinate conventions
+  - internal units
+  - numerical integration method
+  - timestep strategy
+  - force-model semantics
+  - rocket state representation
+  - atmospheric model
+  - motor model
+  - collision/ground-contact behavior
+  - logging/data format
+  - experiment reproducibility
+  - architecture boundaries
+  - development workflow
+- Do not create decision records for every transient coding detail.
+- Decision history is append-preserving. When a decision changes, keep the previous record and mark or link it as superseded or reversed instead of erasing it.
+
+## Architecture Boundaries
+
+- The Pygame application layer owns:
+  - window creation
+  - input handling
+  - drawing
+  - HUD/UI
+  - camera transforms
+  - visualization of trajectories and vectors
+  - display timing
+
+- The physics core owns:
+  - rocket state
+  - force calculations
+  - integration
+  - environment state needed for physics
+  - motor state needed for physics
+  - event/state transitions such as ignition, burnout, apogee, landing, or parachute deployment when introduced
+
+- The physics core should remain independent of Pygame wherever practical.
+- Physics modules must not depend on screen resolution, pixels, fonts, or display coordinates.
+- Simulation state should use world coordinates and SI units.
+- Rendering should transform world state into screen coordinates at the UI boundary.
+- The simulation clock and physics timestep must remain independent from Pygame's display FPS.
+- Configuration/data loading should be separated from force calculations.
+- Motor models should be interchangeable behind a clear interface once more than one motor model exists.
+- Atmospheric models should be replaceable without rewriting rocket dynamics.
+- Experiment and batch-run code should be able to run headlessly without opening a Pygame window.
+- Do not introduce ECS, plugin systems, networking, cloud services, databases, or large frameworks unless an approved milestone requires them.
+
+## Implementation Style
+
+- Favor small components with focused responsibilities and testable interfaces.
+- Keep equations readable and close to their documented physical form.
+- Prefer named dataclasses or domain objects over unstructured dictionaries for durable simulation state.
+- Avoid "magic numbers." Put physical constants and configuration values in named locations.
+- Keep vectors explicit and consistent.
+- If using `pygame.Vector2`, confine Pygame-specific vector usage to boundaries where practical; otherwise use a neutral project vector representation or simple numerical structure.
+- Prefer deterministic simulations for the same configuration unless stochastic behavior is explicitly part of an experiment.
+- Seed random number generators in experiments that use randomness.
+- Preserve raw simulation outputs needed to reproduce derived metrics when practical.
+- Do not optimize prematurely. Correctness and clarity come before micro-optimization.
+- Do not add third-party dependencies without a clear, current need.
+- Avoid broad formatting, renaming, or refactoring unrelated to the current task.
+
+## Numerical Integration
+
+- The initial project should use a documented fixed physics timestep.
+- Rendering FPS must not alter simulation results.
+- If Euler, semi-implicit Euler, RK4, or another integrator is used, document the choice and validation.
+- Run timestep-convergence tests when adding forces whose error may be timestep-sensitive.
+- Do not silently change the integrator or default timestep.
+- When numerical instability appears, diagnose the physical model and timestep before adding arbitrary clamps.
+- Clamps or limits that represent real physical constraints must be documented as such.
+
+## Coordinate System And Units
+
+Unless superseded by a decision record:
+
+- use SI units internally
+- position: meters
+- velocity: meters per second
+- acceleration: meters per second squared
+- force: newtons
+- mass: kilograms
+- time: seconds
+- angle: radians internally, degrees only for display/configuration when convenient
+- world +x: horizontal/right
+- world +y: upward
+- gravity acts in -y
+- screen-coordinate inversion belongs only in rendering
+
+If a different convention is adopted, document it before implementation.
+
+## Repository Tooling
+
+Recommended baseline:
+
+- Python 3.12 or a clearly documented supported Python version
+- Pygame for interactive visualization
+- `pytest` for automated tests
+- standard library `dataclasses`, `math`, `csv`, `json`, and `pathlib` where sufficient
+- optional NumPy only when a real numerical need emerges
+
+## Python Environment Policy
+
+- Development must use an isolated Python 3.12 environment with its own pip capable of installing the project from `pyproject.toml`.
+- On the primary development machine, use the Miniconda environment named `rocketsim`, created with:
+
+  ```bash
+  conda create -n rocketsim python=3.12 pip
+  ```
+
+- Do not use Conda `base` as the project environment, and do not nest a Python `venv` inside the `rocketsim` Conda environment.
+- `pyproject.toml` is the canonical package and dependency configuration. Install the project into the active isolated environment with:
+
+  ```bash
+  python -m pip install -e ".[dev]"
+  ```
+
+- Prefer `python -m pip` to a bare `pip` command so installation uses the selected interpreter.
+- Other developers may use an equivalent isolated Python 3.12 environment, including standard-library `venv`, when supported normally by their machine.
+- Project validation must make interpreter provenance clear. On the primary development machine, automated commands should preferably use `conda run -n rocketsim python ...`.
+- Do not install repository dependencies into Conda `base`, system Python, Homebrew Python, or user-global Python.
+
+Suggested repository structure:
+
+```text
+pygame-rocket-sim/
+├── src/
+│   └── rocket_sim/
+│       ├── app/
+│       ├── physics/
+│       ├── models/
+│       ├── motors/
+│       ├── environment/
+│       ├── rendering/
+│       ├── experiments/
+│       └── config/
+├── tests/
+├── docs/
+│   ├── product/
+│   ├── prompts/
+│   └── decisions/
+├── data/
+│   └── motors/
+├── scripts/
+├── examples/
+├── README.md
+├── AGENTS.md
+└── Pygame_Rocket_Simulator_Project_Context.md
+```
+
+Do not restructure an established repository solely to match this illustrative tree.
+
+## Documentation
+
+- `Pygame_Rocket_Simulator_Project_Context.md` is the primary high-level product, scientific, and milestone document.
+- `AGENTS.md` defines repository-wide agent, workflow, history, physics-discipline, and validation rules.
+- `docs/product/PROJECT_UNDERSTANDING.md` should record the current implementation-oriented understanding of the simulator and repository once implementation begins.
+- `docs/prompts/` contains historical implementation prompts and resulting change records. Prompt records describe what was known and requested at the time and must not be rewritten to reflect later knowledge.
+- `docs/decisions/` contains durable scientific, numerical, product, and architecture decisions.
+- Keep implementation-facing documentation consistent with meaningful code and structure changes.
+- Update equations and assumptions when the implemented model changes.
+
+## Testing And Validation
+
+Physics changes require validation appropriate to the model.
+
+### Minimum validation expectations
+
+- Run unit tests for changed equations and state transitions.
+- Compare simplified cases against analytical solutions whenever one exists.
+- Confirm simulation results do not depend materially on display FPS.
+- Run timestep-convergence checks for meaningful dynamics changes.
+- Check dimensions/units of newly introduced equations.
+- Validate zero-force, zero-thrust, zero-drag, and other limiting cases when relevant.
+- Run `git diff --check` before finishing when practical.
+
+### Examples
+
+For gravity-only projectile motion:
+
+```text
+x(t) = x0 + vx0 * t
+y(t) = y0 + vy0 * t - 0.5 * g * t^2
+vy(t) = vy0 - g * t
+```
+
+For constant thrust with constant mass and fixed thrust direction, compare against constant-acceleration analytical results during powered flight.
+
+For drag models:
+
+- verify drag is zero at zero air-relative speed
+- verify drag opposes air-relative velocity
+- verify drag magnitude scales with v^2 for the quadratic model
+
+For variable mass:
+
+- verify mass never drops below dry mass
+- verify propellant depletion and burnout timing
+- verify thrust becomes zero after burnout unless the selected motor model says otherwise
+
+For atmosphere:
+
+- verify density remains positive
+- verify sea-level values match documented assumptions
+- verify altitude behavior is monotonic over the intended range when using a simple atmosphere model
+
+### Physical-Data Validation
+
+When the project begins comparing against real rocket flights:
+
+- record the source and quality of measured data
+- distinguish calibration data from evaluation data
+- document sensor uncertainty and timing uncertainty
+- do not tune and evaluate on the same run without saying so
+- preserve the configuration used for every comparison
+
+## What Not To Build Yet
+
+Unless explicitly requested, do not add:
+
+- 3D graphics
+- full 6-DOF rigid-body dynamics
+- CFD
+- structural simulation
+- combustion simulation
+- launch-control hardware
+- telemetry radio integration
+- cloud accounts or backend
+- multiplayer/networking
+- machine learning
+- swarm simulation
+- autonomous guidance
+- optimization/search over rocket designs
+- engineering certification or safety claims
+
+These may become future research directions, but the first objective is a trustworthy, understandable 2D rocket simulator.
+
+## Completion Reporting
+
+When finishing an implementation task, report:
+
+1. what changed
+2. what physics/model behavior changed, if any
+3. files created or modified
+4. validation performed
+5. validation not performed and why
+6. important assumptions or limitations
+7. implementation commit SHA
+8. prompt/decision records created
+9. whether the remote was pushed
diff --git a/Pygame_Rocket_Simulator_Project_Context.md b/Pygame_Rocket_Simulator_Project_Context.md
new file mode 100644
index 0000000..f1e6a34
--- /dev/null
+++ b/Pygame_Rocket_Simulator_Project_Context.md
@@ -0,0 +1,756 @@
+# Pygame Rocket Simulator — Project Context for Codex
+
+**Date:** 2026-08-27
+**Purpose:** Canonical project context for implementation work on the Pygame rocket-flight simulator.
+
+## 1. Project Vision
+
+The project is a **2D physics simulation environment for model-rocket flight**, built in Python with Pygame.
+
+The first goal is not to create a visually elaborate game. The first goal is to build a simulation whose behavior is:
+
+- physically understandable
+- mathematically inspectable
+- easy to validate
+- easy to extend one physical effect at a time
+- visually intuitive enough to make the physics observable
+
+The simulator should become a small experimental testbed for studying how rocket behavior changes when launch conditions, motor characteristics, aerodynamics, mass, atmosphere, and eventually stability or control are varied.
+
+Conceptually:
+
+```text
+Rocket configuration
+        ↓
+Initial conditions
+        ↓
+Motor / thrust model
+        ↓
+Environment model
+        ↓
+Force calculation
+        ↓
+Numerical integration
+        ↓
+Rocket state over time
+        ↓
+Visualization + telemetry
+        ↓
+Metrics / experiments / comparison
+```
+
+Pygame is the visualization and interaction layer. The core product is the **simulation model and experiment framework**.
+
+## 2. Core Project Principle
+
+The simulator should make it possible to answer:
+
+> Given a clearly defined rocket model and launch condition, what motion follows from the modeled forces?
+
+The software should:
+
+- represent rocket state explicitly
+- calculate forces explicitly
+- integrate motion through time
+- visualize the resulting trajectory
+- expose the values used in the calculations
+- preserve enough simulation data to reproduce and inspect results
+- allow physical assumptions to be changed deliberately
+- distinguish simplified models from higher-fidelity models
+
+The simulator should not hide physics behind unexplained tuning.
+
+## 3. Terminology
+
+- **World state:** the physical simulation state expressed in world coordinates and SI units.
+- **Rocket state:** the rocket's position, velocity, acceleration, mass, and later orientation/angular state.
+- **Simulation step:** one fixed numerical update of duration `dt`.
+- **Rendering frame:** one Pygame screen update. Rendering frames are not physics timesteps.
+- **Thrust:** force generated by the rocket motor.
+- **Burn time:** interval during which the motor produces thrust.
+- **Burnout:** transition when active motor thrust ends.
+- **Coast phase:** unpowered flight after burnout and before recovery deployment/landing.
+- **Apogee:** maximum altitude reached during a flight.
+- **Drag:** aerodynamic force opposing air-relative motion.
+- **Air-relative velocity:** rocket velocity relative to the surrounding air/wind.
+- **Mass flow:** propellant mass consumed per unit time.
+- **Dry mass:** rocket mass excluding consumed propellant.
+- **Thrust curve:** thrust as a function of time.
+- **Integrator:** numerical method used to advance state through time.
+- **Telemetry:** displayed/logged values such as time, altitude, speed, acceleration, mass, thrust, and Mach number.
+- **Run configuration:** the full set of parameters required to reproduce one simulation.
+
+## 4. Initial Scope
+
+### Input
+
+The first simulator should accept a small rocket configuration such as:
+
+- initial position
+- launch angle
+- initial velocity, normally zero
+- rocket mass
+- thrust magnitude
+- burn duration
+- gravitational acceleration
+- physics timestep
+
+The interface may begin with hard-coded or file-based configuration before interactive controls are introduced.
+
+### Initial Output
+
+The application should eventually be able to:
+
+1. open a Pygame window
+2. display a launch pad / ground reference
+3. initialize a rocket
+4. simulate a fixed physics timestep
+5. apply gravity
+6. apply finite-duration thrust
+7. update velocity and position
+8. render the rocket trajectory
+9. display useful telemetry
+10. detect basic events such as burnout, apogee, and ground contact
+11. reset and rerun a simulation
+12. log a run for validation and later analysis
+
+The first implementation should intentionally exclude drag and variable mass.
+
+## 5. Immediate Milestones
+
+### Milestone 0 — Repository And Simulation Foundation
+
+Establish:
+
+- repository structure
+- Python environment and dependency declaration
+- Pygame application loop
+- fixed physics timestep
+- world-to-screen coordinate transform
+- neutral rocket-state model
+- basic tests
+- documentation, prompt archive, and decision archive
+
+No detailed rocket physics beyond what is needed to validate the application loop.
+
+### Milestone 1 — Gravity + Constant-Thrust Point-Mass Flight
+
+Implement only:
+
+- 2D position
+- 2D velocity
+- constant mass
+- constant gravitational acceleration
+- fixed thrust magnitude during burn
+- fixed thrust direction based on launch angle
+- burnout after a defined burn duration
+- coast under gravity
+- ground-contact termination
+- trajectory visualization
+- telemetry
+- analytical validation of simplified cases
+
+Do **not** implement aerodynamic drag, changing mass, thrust curves, wind, rotation, or parachutes yet.
+
+### Milestone 2 — Aerodynamic Drag
+
+Add:
+
+- quadratic drag
+- air-relative velocity
+- constant initial air density
+- drag coefficient
+- reference area
+- optional constant wind
+- drag vector visualization
+- drag-specific validation
+
+### Milestone 3 — Variable Mass + Motor Thrust Curves
+
+Add:
+
+- dry mass
+- propellant mass
+- propellant depletion
+- mass-flow semantics
+- motor thrust curve
+- interpolation of thrust over time
+- burnout derived from motor data
+- preservation of motor configuration used for a run
+
+Do not add detailed combustion physics.
+
+### Milestone 4 — Atmosphere
+
+Add a documented atmospheric model:
+
+- density as a function of altitude
+- temperature if needed
+- speed of sound
+- Mach number
+
+Keep the model replaceable and clearly identify its valid altitude range.
+
+### Milestone 5 — Recovery
+
+Add:
+
+- apogee detection
+- deployment timing
+- parachute drag model
+- descent
+- landing metrics
+
+Recovery should be represented as another physical state/model, not as an arbitrary velocity clamp.
+
+### Milestone 6 — Rotation And Stability
+
+Only after the point-mass simulator is trustworthy, introduce:
+
+- rocket orientation
+- angular velocity
+- moment of inertia
+- center of mass
+- center of pressure
+- aerodynamic restoring moment
+- torque
+- angular integration
+
+This milestone changes the simulator from point-mass flight toward simplified rigid-body flight dynamics and should be treated as a major architecture/physics decision.
+
+### Milestone 7 — Experiment Framework
+
+Add headless reproducible experiments such as:
+
+- launch-angle sweeps
+- mass sweeps
+- drag-coefficient sweeps
+- wind sensitivity
+- motor comparisons
+- timestep sensitivity
+- model comparisons
+
+Runs should be reproducible and export structured data suitable for plotting or statistical analysis.
+
+## 6. Current Technical Direction
+
+- **Language:** Python
+- **Visualization/UI:** Pygame
+- **Physics:** custom, explicit equations
+- **Testing:** pytest
+- **Data:** CSV/JSON or similarly simple formats initially
+- **Internal units:** SI
+- **Simulation:** 2D first
+- **Physics timestep:** fixed timestep, independent of rendering FPS
+- **Backend:** none
+- **Networking:** none
+- **Cloud:** none
+
+The project should avoid unnecessary dependencies until a clear requirement appears.
+
+## 7. Proposed Repository
+
+Recommended root:
+
+```text
+pygame-rocket-sim/
+```
+
+Suggested structure:
+
+```text
+pygame-rocket-sim/
+├── src/
+│   └── rocket_sim/
+│       ├── __init__.py
+│       ├── app/
+│       │   ├── main.py
+│       │   └── simulation_controller.py
+│       ├── models/
+│       │   ├── rocket.py
+│       │   └── simulation_state.py
+│       ├── physics/
+│       │   ├── forces.py
+│       │   ├── integrators.py
+│       │   └── dynamics.py
+│       ├── motors/
+│       ├── environment/
+│       ├── rendering/
+│       │   ├── camera.py
+│       │   ├── renderer.py
+│       │   └── hud.py
+│       ├── experiments/
+│       └── config/
+├── tests/
+│   ├── test_dynamics.py
+│   ├── test_integrators.py
+│   └── test_events.py
+├── docs/
+│   ├── product/
+│   │   └── PROJECT_UNDERSTANDING.md
+│   ├── prompts/
+│   └── decisions/
+├── data/
+│   └── motors/
+├── examples/
+├── scripts/
+├── README.md
+├── AGENTS.md
+└── Pygame_Rocket_Simulator_Project_Context.md
+```
+
+This is an intended structure, not a requirement to create speculative modules before they are needed.
+
+## 8. Physics-Core Responsibilities
+
+The physics core should remain independent of Pygame wherever practical.
+
+Suggested durable concepts:
+
+```text
+RocketConfig
+RocketState
+EnvironmentState
+MotorModel
+MotorState
+SimulationConfig
+SimulationState
+ForceBreakdown
+FlightEvent
+SimulationSample
+SimulationRun
+Integrator
+```
+
+Responsibilities:
+
+- state representation
+- force calculation
+- state integration
+- motor-state transitions
+- event detection
+- atmosphere/environment values used by physics
+- reproducible simulation stepping
+- data needed for validation and experiments
+
+The physics core should not know about:
+
+- pixels
+- fonts
+- mouse coordinates
+- screen resolution
+- Pygame surfaces
+- camera zoom
+- UI widgets
+
+## 9. Rendering Boundary
+
+The renderer should consume physical state and convert it into a display.
+
+Conceptually:
+
+```text
+World position in meters
+        ↓
+Camera / viewport transform
+        ↓
+Screen position in pixels
+        ↓
+Pygame drawing
+```
+
+The renderer may draw:
+
+- rocket
+- ground
+- trajectory
+- velocity vector
+- thrust vector
+- gravity vector
+- drag vector
+- telemetry
+- phase/event labels
+
+Rendering must not modify the physics state.
+
+## 10. Time Model
+
+The simulation must distinguish:
+
+```text
+real wall-clock time
+display/render frame time
+physics simulation time
+```
+
+The physics result should not materially change because the monitor runs at 60 Hz, 120 Hz, or another display rate.
+
+Initial strategy:
+
+- fixed physics timestep `dt`
+- accumulator-based stepping if needed
+- rendering as often as the Pygame loop allows
+- optional interpolation for visual smoothness later
+
+The exact timestep and integrator should become documented decisions.
+
+## 11. Coordinate Convention
+
+Initial intended world convention:
+
+```text
++x = right
++y = up
+origin = launch point or ground reference
+```
+
+Gravity:
+
+```text
+a_g = (0, -g)
+```
+
+Pygame screen coordinates increase downward, so the renderer must invert the vertical world coordinate when mapping to pixels.
+
+Do not use screen coordinates as the stored physical state.
+
+## 12. Initial Physics Model
+
+### State
+
+For Milestone 1:
+
+```text
+position = (x, y)
+velocity = (vx, vy)
+mass = constant
+time = t
+```
+
+### Gravity
+
+```text
+Fg = (0, -m g)
+```
+
+### Thrust
+
+During powered flight:
+
+```text
+Ft = T * (cos(theta), sin(theta))
+```
+
+After burnout:
+
+```text
+Ft = (0, 0)
+```
+
+### Net force
+
+```text
+Fnet = Ft + Fg
+```
+
+### Acceleration
+
+```text
+a = Fnet / m
+```
+
+### Integration
+
+A fixed-step numerical integrator updates velocity and position.
+
+The chosen integrator must be documented and validated.
+
+## 13. Drag Model
+
+Drag is not part of Milestone 1.
+
+When introduced:
+
+```text
+Fd = 0.5 * rho * Cd * A * v_air^2
+```
+
+and must act opposite the air-relative velocity vector.
+
+Important semantics:
+
+```text
+v_air = v_rocket - v_wind
+```
+
+At zero air-relative velocity, drag must be zero.
+
+The model should expose:
+
+- air density
+- drag coefficient
+- reference area
+- air-relative speed
+- drag magnitude
+- drag vector
+
+## 14. Motor Model
+
+The first motor model is intentionally simple:
+
+```text
+constant thrust T
+for 0 <= t < burn_time
+```
+
+Later, the simulator should support a motor thrust curve:
+
+```text
+time -> thrust
+```
+
+The simulator should preserve the motor data/configuration used in each run so results can be reproduced.
+
+Do not hardcode one specific commercial motor into the physics architecture.
+
+## 15. Data Preservation Rules
+
+Do not discard simulation inputs after calculating summary metrics.
+
+A reproducible run should preserve, directly or through references:
+
+- initial conditions
+- rocket configuration
+- motor configuration
+- environment configuration
+- timestep
+- integrator
+- model versions when meaningful
+- simulation samples or enough data to regenerate them
+- detected flight events
+- summary metrics
+
+Possible derived metrics:
+
+- max altitude
+- time to apogee
+- max speed
+- max acceleration
+- burnout altitude
+- burnout velocity
+- total flight time
+- impact/descent speed
+- downrange distance
+
+Derived metrics should be recalculable.
+
+## 16. Validation Is Core
+
+The simulator is not considered correct simply because the animation looks plausible.
+
+Every milestone should include physics validation.
+
+### Milestone 1 analytical cases
+
+For gravity-only projectile motion:
+
+```text
+x(t) = x0 + vx0 t
+y(t) = y0 + vy0 t - 0.5 g t^2
+vy(t) = vy0 - g t
+```
+
+For constant thrust, fixed direction, and constant mass during the burn:
+
+```text
+ax = T cos(theta) / m
+ay = T sin(theta) / m - g
+```
+
+which permits comparison against constant-acceleration analytical motion during the powered interval.
+
+### Numerical checks
+
+The project should also test:
+
+- smaller timestep produces convergence
+- rendering FPS does not change physical results
+- zero thrust behaves like projectile motion
+- zero gravity behaves as expected
+- zero drag later produces the no-drag solution
+- drag opposes air-relative velocity
+- mass never falls below dry mass once variable mass exists
+- burnout transitions happen once and at the expected time
+- ground contact terminates or transitions the simulation consistently
+
+## 17. Visualization Philosophy
+
+The display should make the physics inspectable.
+
+Useful visual elements include:
+
+- trajectory trace
+- world scale/grid
+- thrust vector
+- gravity vector
+- drag vector
+- velocity vector
+- current altitude
+- current speed
+- vertical speed
+- acceleration
+- simulation time
+- current mass
+- current thrust
+- current flight phase
+- Mach number when the atmosphere model exists
+
+Whenever possible, the user should be able to connect a displayed result with the physical quantities that produced it.
+
+## 18. What Not To Build Yet
+
+Do not implement these in the first technical milestones:
+
+- 3D graphics
+- 6-DOF flight dynamics
+- CFD
+- finite-element structural analysis
+- detailed combustion/chamber simulation
+- supersonic shock modeling
+- active guidance
+- autonomous control
+- swarm robotics
+- telemetry hardware
+- live sensors
+- launch electronics
+- cloud services
+- accounts
+- multiplayer
+- machine learning
+- automatic rocket-design optimization
+- engineering certification
+- safety-critical launch prediction
+
+These are possible future directions, not current scope.
+
+## 19. Scientific Philosophy
+
+The project should:
+
+- model
+- visualize
+- compare
+- validate
+- preserve assumptions
+- make equations inspectable
+- show where numbers came from
+
+When a metric or trajectory is shown, it should be possible to answer:
+
+1. what state variables were used?
+2. what forces were active?
+3. what equations were used?
+4. what timestep and integrator were used?
+5. what assumptions were made?
+6. what configuration produced the run?
+7. how was the result validated?
+
+## 20. Long-Term Direction
+
+The simulator may eventually become a broader aerospace experimentation environment:
+
+```text
+                       Simulation Core
+                              │
+          ┌───────────────────┼───────────────────┐
+          ▼                   ▼                   ▼
+      Rocket Flight       Recovery          Experiments
+          │                   │                   │
+          ▼                   ▼                   ▼
+       Aerodynamics       Parachutes        Parameter Sweeps
+          │
+          ▼
+   Rotation / Stability
+          │
+          ▼
+   Control / Guidance
+```
+
+Potential research extensions could later include:
+
+- stability and center-of-pressure studies
+- launch-condition sensitivity
+- uncertainty propagation
+- sensor simulation
+- estimation algorithms
+- recovery optimization
+- multi-rocket experiments
+- swarm or distributed-airborne-system concepts
+
+These are future directions only. The initial project remains a simple, trustworthy 2D rocket simulator.
+
+## 21. Current State
+
+As of 2026-08-27:
+
+- the project concept has been defined
+- Pygame has been selected as the visualization environment
+- an initial documentation package has been drafted
+- the intended first physics model is a 2D point-mass rocket
+- the first implementation should begin with fixed-step gravity + constant thrust
+- no production repository implementation is assumed by this document unless verified in the working tree
+
+Before implementation, inspect the actual repository state rather than assuming files already exist.
+
+## 22. Codex Working Rules
+
+1. Inspect before editing.
+2. Read `AGENTS.md` and this context document first.
+3. Keep physics independent of Pygame rendering wherever practical.
+4. Keep simulation time independent of rendering FPS.
+5. Use SI units internally unless a decision explicitly changes that rule.
+6. Add one major physical effect at a time.
+7. Validate simplified models analytically before adding realism.
+8. Do not silently change equations, integrator, timestep, units, or coordinate conventions.
+9. Prefer small, testable milestones.
+10. Preserve reproducibility of simulation runs.
+11. Do not introduce backend or heavy-framework complexity.
+12. Do not add future systems merely because they may eventually be useful.
+13. Record meaningful durable decisions.
+14. Report assumptions and validation gaps explicitly.
+15. Treat plausible-looking animation as insufficient evidence of correctness.
+
+## 23. Immediate Next Task
+
+### Milestone 0 + Milestone 1 Foundation
+
+Build the smallest end-to-end simulator that can be scientifically validated.
+
+Target behavior:
+
+- open a Pygame window
+- show ground and launch point
+- instantiate one rocket
+- advance physics with a fixed timestep
+- apply gravity
+- apply constant finite-duration thrust at a fixed launch angle
+- update position and velocity
+- transition to coast after burnout
+- render the trajectory
+- show basic telemetry
+- stop or transition on ground contact
+- support reset/re-run
+- add automated tests
+- compare at least one run against an analytical solution
+
+Do **not** add drag, variable mass, thrust curves, wind, rotation, stability, parachutes, or control yet.
+
+Before editing files, Codex should:
+
+1. inspect the current repository structure
+2. inspect the working tree
+3. identify the next unused prompt and decision IDs
+4. propose the minimal implementation plan
+5. identify assumptions and physics-validation strategy
+6. avoid creating speculative modules that are not needed for Milestone 0/1
+7. proceed only within the approved task scope
diff --git a/README.md b/README.md
new file mode 100644
index 0000000..017d417
--- /dev/null
+++ b/README.md
@@ -0,0 +1,59 @@
+# Pygame Rocket Physics Simulator
+
+A staged 2D model-rocket flight simulator built with Python and Pygame. The project emphasizes explicit assumptions, reproducible runs, analytical validation, and a clean boundary between physics and visualization.
+
+## Current status
+
+Prompt 01 establishes the Milestone 0 repository and tooling baseline. The `rocket_sim` package is installable and tested, but no Pygame application loop or rocket-flight physics is implemented yet.
+
+The next milestone will add 2D constant-mass flight with gravity and finite-duration constant thrust. Drag, variable mass, wind, atmosphere, recovery, rotation, stability, guidance, and control remain out of scope until later milestones.
+
+## Development setup
+
+Python 3.12 and an isolated environment are required. On the primary Miniconda-based development machine, create and use the dedicated `rocketsim` environment:
+
+```bash
+conda create -n rocketsim python=3.12 pip
+conda activate rocketsim
+python --version
+python -m pip --version
+python -m pip install --upgrade pip
+python -m pip install -e ".[dev]"
+python -m pytest
+```
+
+For automated work on that machine, make the interpreter explicit without relying on shell activation:
+
+```bash
+conda run -n rocketsim python -m pytest
+```
+
+Conda supplies isolation, Python, and pip; `pyproject.toml` remains the canonical project and dependency declaration. Use `python -m pip` so pip belongs to the selected interpreter. Do not use Conda `base` for project dependencies, and do not create a nested `venv` inside the `rocketsim` environment.
+
+On other machines, a conventional isolated Python 3.12 environment, including standard-library `venv`, is acceptable when it works normally. Install the same project and development dependencies from `pyproject.toml` with `python -m pip install -e ".[dev]"`.
+
+## Repository layout
+
+```text
+src/rocket_sim/     importable application package
+tests/              pytest test suite
+docs/product/       current implementation understanding
+docs/prompts/       prompt and implementation history
+docs/decisions/     durable project decisions
+```
+
+Subsystem directories will be introduced only when a concrete implementation milestone needs them.
+
+## Documentation
+
+- [`Pygame_Rocket_Simulator_Project_Context.md`](Pygame_Rocket_Simulator_Project_Context.md) — canonical product, scientific, and milestone context
+- [`docs/product/PROJECT_UNDERSTANDING.md`](docs/product/PROJECT_UNDERSTANDING.md) — current implementation-oriented status
+- [`docs/PHYSICS_MODEL.md`](docs/PHYSICS_MODEL.md) — planned model assumptions and equations
+- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — architecture direction
+- [`docs/VALIDATION.md`](docs/VALIDATION.md) — validation strategy
+- [`docs/MILESTONES.md`](docs/MILESTONES.md) — staged development plan
+- [`docs/RESEARCH_LOG.md`](docs/RESEARCH_LOG.md) — research questions and experiment log
+
+## Definition of success
+
+The simulator should become a trustworthy experimental sandbox rather than merely a plausible animation. Results must remain understandable, testable, and traceable to their equations, units, numerical method, and configuration.
diff --git a/docs/ARCHITECTURE.md b/docs/ARCHITECTURE.md
new file mode 100644
index 0000000..451cf9a
--- /dev/null
+++ b/docs/ARCHITECTURE.md
@@ -0,0 +1,255 @@
+# Software Architecture
+
+## Objective
+
+The simulator should be designed so that the physics can run independently of Pygame. Pygame should be a visualization and input layer, not the physics engine itself.
+
+This separation will make it easier to:
+
+- test the physics,
+- run simulations faster than real time,
+- run parameter sweeps,
+- compare models,
+- add alternative visualizations later,
+- and potentially reuse the simulator for autonomous-control experiments.
+
+---
+
+## Proposed Components
+
+### `main.py`
+
+Responsibilities:
+
+- Initialize Pygame.
+- Create the simulation.
+- Run the application loop.
+- Handle top-level user input.
+- Coordinate physics updates and rendering.
+
+It should contain as little physics logic as possible.
+
+### `simulation.py`
+
+Responsibilities:
+
+- Own simulation time.
+- Advance the simulation by a timestep.
+- Coordinate forces and environment.
+- Determine when a flight starts and ends.
+- Record trajectory/history data.
+
+Possible interface:
+
+```python
+simulation.step(dt)
+simulation.reset()
+simulation.is_finished
+```
+
+### `rocket.py`
+
+Responsibilities:
+
+- Store rocket physical properties.
+- Store current rocket state.
+- Update state from calculated forces.
+
+Possible properties:
+
+```text
+position
+velocity
+mass
+dry_mass
+reference_area
+drag_coefficient
+```
+
+Later:
+
+```text
+angle
+angular_velocity
+moment_of_inertia
+center_of_mass
+center_of_pressure
+```
+
+### `motor.py`
+
+Responsibilities:
+
+- Motor burn duration.
+- Thrust as a function of time.
+- Propellant mass.
+- Mass flow.
+
+Possible interface:
+
+```python
+motor.thrust_at(t)
+motor.propellant_mass_at(t)
+motor.is_burning(t)
+```
+
+### `environment.py`
+
+Responsibilities:
+
+- Gravity.
+- Air density.
+- Wind.
+- Atmospheric properties.
+
+Possible interface:
+
+```python
+environment.gravity_at(position)
+environment.air_density_at(altitude)
+environment.wind_at(altitude, time)
+```
+
+### `renderer.py`
+
+Responsibilities:
+
+- Convert world coordinates to screen coordinates.
+- Draw rocket.
+- Draw trajectory.
+- Draw ground.
+- Draw telemetry.
+- Draw force vectors when enabled.
+
+The renderer must not modify physical state.
+
+### `config.py`
+
+Responsibilities:
+
+- Store initial simulation parameters.
+- Keep tuning values out of physics code.
+
+Example configuration:
+
+```python
+ROCKET_MASS_KG = 1.5
+THRUST_N = 35.0
+BURN_TIME_S = 1.0
+LAUNCH_ANGLE_DEG = 85.0
+PHYSICS_DT = 0.01
+```
+
+Eventually, replace or supplement this with JSON/TOML experiment configuration files.
+
+---
+
+## Main Loop
+
+Conceptually:
+
+```text
+initialize
+
+while running:
+    process user input
+
+    accumulate real elapsed time
+
+    while accumulated_time >= physics_dt:
+        simulation.step(physics_dt)
+        accumulated_time -= physics_dt
+
+    renderer.draw(simulation)
+    display frame
+```
+
+This fixed-timestep structure prevents simulation results from changing significantly when graphical frame rate changes.
+
+---
+
+## Data Flow
+
+```text
+User Input
+    ↓
+Configuration
+    ↓
+Simulation
+    ↓
+Rocket + Motor + Environment
+    ↓
+Force Calculation
+    ↓
+Numerical Integration
+    ↓
+Updated Rocket State
+    ↓
+Renderer
+    ↓
+Pygame Display
+```
+
+Trajectory data should also be stored separately for later plotting and analysis.
+
+---
+
+## Design Rules
+
+### Rule 1: SI units internally
+
+Never mix screen pixels with metres.
+
+### Rule 2: Renderer does not own physics
+
+Changing zoom or window size must not change simulation results.
+
+### Rule 3: Fixed physics timestep
+
+Physics should not depend directly on FPS.
+
+### Rule 4: One source of truth for state
+
+Rocket position and velocity should be stored in one location only.
+
+### Rule 5: Keep models replaceable
+
+For example, `ConstantThrustMotor` should later be replaceable by `ThrustCurveMotor` without rewriting the simulation.
+
+### Rule 6: Record experiment parameters
+
+A result is not scientifically useful if the simulator cannot reproduce the run.
+
+---
+
+## Suggested First Classes
+
+```text
+Vector2 / pygame.math.Vector2
+Rocket
+Motor
+Environment
+Simulation
+Renderer
+```
+
+Using `pygame.math.Vector2` is acceptable for vector arithmetic in the first version.
+
+---
+
+## Future Architecture Possibilities
+
+Later, the simulator may benefit from:
+
+- an `Experiment` class,
+- batch simulation mode,
+- CSV export,
+- plotting with Matplotlib,
+- Monte Carlo runs,
+- sensor simulation,
+- autopilot/controller modules,
+- multiple vehicles,
+- reinforcement learning environments,
+- and a headless mode without Pygame.
+
+These should remain future extensions rather than requirements for the first implementation.
diff --git a/docs/MILESTONES.md b/docs/MILESTONES.md
new file mode 100644
index 0000000..7615ec8
--- /dev/null
+++ b/docs/MILESTONES.md
@@ -0,0 +1,245 @@
+# Development Milestones
+
+## Strategy
+
+Build the simulator in small, testable stages. Each milestone should introduce one major source of physical complexity while keeping previous behavior working.
+
+---
+
+## Milestone 0 — Project Skeleton
+
+### Goal
+
+Create a runnable Pygame application with a clean project structure.
+
+### Deliverables
+
+- Pygame window opens.
+- Main loop runs.
+- Simulation and renderer are separate modules.
+- Basic configuration file exists.
+- Test directory exists.
+
+### Completion Check
+
+The project launches without errors and can display a static rocket on a ground line.
+
+---
+
+## Milestone 1 — Powered Point-Mass Flight
+
+### Physics
+
+- Constant gravity.
+- Constant mass.
+- Constant thrust during a fixed burn interval.
+- No drag.
+- Fixed launch angle.
+
+### Features
+
+- Launch/reset controls.
+- Rocket trajectory.
+- Elapsed time.
+- Position and velocity display.
+- Automatic transition from powered flight to coast.
+- Flight ends when rocket returns to ground.
+
+### Validation
+
+Compare no-thrust ballistic motion with analytical projectile equations.
+
+### Completion Check
+
+Simulation results are stable and approximately independent of graphical FPS.
+
+---
+
+## Milestone 2 — Aerodynamic Drag
+
+### Physics
+
+Add:
+
+```text
+F_drag = 0.5 rho C_d A v²
+```
+
+### Features
+
+- Configurable drag coefficient.
+- Configurable reference area.
+- Optional drag force vector display.
+
+### Validation
+
+Confirm that:
+
+- drag always opposes velocity,
+- drag is zero when velocity is zero,
+- drag scales approximately with `v²`,
+- altitude is lower with drag enabled than without drag.
+
+---
+
+## Milestone 3 — Variable Mass and Motor Model
+
+### Physics
+
+- Dry mass.
+- Propellant mass.
+- Propellant depletion.
+- Changing total mass.
+
+### Features
+
+- Remaining propellant display.
+- Motor state: idle / burning / burned out.
+
+### Validation
+
+Confirm total rocket mass never drops below dry mass.
+
+---
+
+## Milestone 4 — Real Thrust Curves
+
+### Goal
+
+Load sampled motor thrust data from a file.
+
+### Features
+
+- CSV motor data.
+- Linear interpolation.
+- Total impulse calculation.
+- Motor curve visualization or debug plot.
+
+### Validation
+
+Numerically integrate thrust curve and compare with expected total impulse.
+
+---
+
+## Milestone 5 — Atmosphere and Mach Number
+
+### Physics
+
+- Density decreases with altitude.
+- Speed of sound estimate.
+- Mach number calculation.
+
+### Features
+
+- Display Mach number.
+- Display maximum Mach reached.
+
+### Validation
+
+Compare atmospheric values with a trusted reference at several altitudes.
+
+---
+
+## Milestone 6 — Wind and Recovery
+
+### Physics
+
+- Horizontal wind.
+- Relative air velocity.
+- Parachute drag.
+
+### Features
+
+- Parachute deployment altitude/time condition.
+- Landing location.
+- Drift distance.
+
+### Validation
+
+Confirm stronger wind produces larger horizontal drift during descent.
+
+---
+
+## Milestone 7 — Rotational Dynamics
+
+### Physics
+
+Introduce:
+
+- rocket orientation,
+- angular velocity,
+- torque,
+- moment of inertia,
+- angle of attack.
+
+### Features
+
+- Rocket sprite rotates physically.
+- Attitude data display.
+
+### Validation
+
+Start with simple torque-only test cases before aerodynamic stability.
+
+---
+
+## Milestone 8 — Aerodynamic Stability
+
+### Physics
+
+- Center of gravity.
+- Center of pressure.
+- Restoring aerodynamic moment.
+- Approximate stability margin.
+
+### Features
+
+- Display CG and CP.
+- Show whether configuration is nominally stable.
+
+### Validation
+
+A statically stable rocket should tend to align with its relative airflow after small disturbances.
+
+---
+
+## Milestone 9 — Experiment Mode
+
+### Features
+
+- Run without real-time graphics.
+- Sweep launch parameters.
+- Export CSV results.
+- Compare apogee, maximum velocity, range, and flight time.
+- Reproduce runs from saved configuration.
+
+### Example Experiment
+
+Vary launch angle from 70° to 90° and measure:
+
+```text
+apogee
+horizontal drift
+maximum speed
+flight duration
+```
+
+---
+
+## Milestone 10 — Advanced Research Extensions
+
+Possible directions:
+
+- Active thrust-vector control.
+- Fin control.
+- Sensor simulation.
+- State estimation.
+- Kalman filtering.
+- Autonomous apogee detection.
+- Optimal control.
+- Monte Carlo uncertainty analysis.
+- Multi-rocket simulations.
+- Swarm behavior.
+- Reinforcement learning controllers.
+
+These are deliberately outside the initial scope.
diff --git a/docs/PHYSICS_MODEL.md b/docs/PHYSICS_MODEL.md
new file mode 100644
index 0000000..ae4ec56
--- /dev/null
+++ b/docs/PHYSICS_MODEL.md
@@ -0,0 +1,317 @@
+# Physics Model
+
+## Purpose
+
+This document defines the physical assumptions, equations, variables, and staged fidelity of the rocket simulator.
+
+The simulator should use SI units internally:
+
+- Position: metres (m)
+- Time: seconds (s)
+- Velocity: metres per second (m/s)
+- Acceleration: metres per second squared (m/s²)
+- Mass: kilograms (kg)
+- Force: newtons (N)
+- Angle: radians internally
+
+Screen pixels should never be used as physics units.
+
+---
+
+## Coordinate System
+
+Use a two-dimensional Cartesian coordinate system:
+
+- +x = horizontal right
+- +y = upward
+- Ground = y = 0
+
+Pygame screen coordinates increase downward, so the renderer must convert simulation coordinates to screen coordinates.
+
+---
+
+## Core State Variables
+
+At minimum, the rocket state should contain:
+
+```text
+time
+position_x
+position_y
+velocity_x
+velocity_y
+mass
+```
+
+Later versions may add:
+
+```text
+angle
+angular_velocity
+propellant_mass
+acceleration_x
+acceleration_y
+mach_number
+```
+
+---
+
+## Milestone 1 Physics
+
+### Gravity
+
+Assume constant gravitational acceleration:
+
+```text
+g = 9.81 m/s²
+```
+
+The gravitational force is:
+
+```text
+F_gravity = m g
+```
+
+acting downward.
+
+In vector form:
+
+```text
+F_g = (0, -m g)
+```
+
+### Thrust
+
+For the first implementation, assume constant thrust during the motor burn.
+
+For thrust magnitude `T` and launch angle `theta`:
+
+```text
+F_thrust_x = T cos(theta)
+F_thrust_y = T sin(theta)
+```
+
+After burnout:
+
+```text
+T = 0
+```
+
+### Net Force
+
+```text
+F_net = F_thrust + F_gravity
+```
+
+### Acceleration
+
+Newton's second law:
+
+```text
+a = F_net / m
+```
+
+Therefore:
+
+```text
+a_x = F_net_x / m
+a_y = F_net_y / m
+```
+
+---
+
+## Numerical Integration
+
+Use a fixed simulation timestep `dt` initially.
+
+Recommended starting value:
+
+```text
+dt = 0.01 s
+```
+
+Use semi-implicit Euler integration:
+
+```text
+v_new = v_old + a * dt
+x_new = x_old + v_new * dt
+```
+
+This is preferable to updating position using the old velocity because it is generally more stable for simple real-time simulations.
+
+The physics timestep should be independent from the graphical frame rate if possible.
+
+---
+
+## Milestone 2: Aerodynamic Drag
+
+Drag magnitude:
+
+```text
+F_drag = 0.5 * rho * C_d * A * v²
+```
+
+where:
+
+- `rho` = air density
+- `C_d` = drag coefficient
+- `A` = reference/frontal area
+- `v` = speed
+
+Drag must point opposite the velocity vector.
+
+For speed:
+
+```text
+v = sqrt(v_x² + v_y²)
+```
+
+If `v > 0`:
+
+```text
+F_drag_x = -F_drag * v_x / v
+F_drag_y = -F_drag * v_y / v
+```
+
+Initial simplification:
+
+```text
+rho = 1.225 kg/m³
+```
+
+at sea level.
+
+---
+
+## Milestone 3: Variable Mass
+
+Model propellant consumption during motor burn.
+
+A simple first model:
+
+```text
+mass(t) = dry_mass + remaining_propellant_mass
+```
+
+For constant mass flow:
+
+```text
+propellant_mass_remaining = initial_propellant_mass - mass_flow_rate * t
+```
+
+Clamp remaining propellant mass to zero.
+
+The reduced mass should automatically increase acceleration for the same thrust.
+
+---
+
+## Milestone 4: Real Motor Thrust Curve
+
+Replace constant thrust with a time-dependent motor curve.
+
+Example data:
+
+```text
+time_s,thrust_N
+0.00,0
+0.05,25
+0.10,40
+0.30,35
+0.60,20
+0.80,0
+```
+
+Interpolate between samples to obtain thrust at simulation time.
+
+Possible future source: published model rocket motor test data.
+
+---
+
+## Milestone 5: Atmospheric Model
+
+Allow air density to decrease with altitude.
+
+A simple approximation can be introduced first. A more realistic standard-atmosphere model can be added later.
+
+Potential variables:
+
+```text
+temperature
+pressure
+air_density
+speed_of_sound
+```
+
+Mach number:
+
+```text
+Mach = speed / speed_of_sound
+```
+
+---
+
+## Milestone 6: Attitude and Stability
+
+Once translational motion is reliable, introduce rocket orientation.
+
+State variables:
+
+```text
+angle theta
+angular_velocity omega
+angular_acceleration alpha
+```
+
+Rotational dynamics:
+
+```text
+torque = I * alpha
+```
+
+or:
+
+```text
+alpha = torque / I
+```
+
+Eventually, aerodynamic force should depend on angle of attack, center of pressure, and center of mass.
+
+This milestone is a major increase in complexity and should not be started until earlier models are validated.
+
+---
+
+## Ground Interaction
+
+The simulation begins with:
+
+```text
+y = 0
+```
+
+After launch, if the rocket returns to:
+
+```text
+y <= 0
+```
+
+and is descending, the flight should end.
+
+For the first version, no bounce or impact dynamics are needed.
+
+---
+
+## Important Assumptions to Track
+
+Every simulation run should make clear which assumptions are active.
+
+Examples:
+
+- Flat Earth over short range.
+- Constant `g`.
+- No Coriolis force.
+- No wind unless enabled.
+- Rocket treated as a point mass until attitude dynamics are added.
+- Constant drag coefficient unless otherwise specified.
+- No transonic aerodynamic correction unless explicitly implemented.
+
+These assumptions should eventually appear in exported experiment metadata.
diff --git a/docs/PROJECT_BRIEF.md b/docs/PROJECT_BRIEF.md
new file mode 100644
index 0000000..9275e8b
--- /dev/null
+++ b/docs/PROJECT_BRIEF.md
@@ -0,0 +1,124 @@
+# Project Brief
+
+## Working Title
+
+**2D Rocket Flight Physics Simulator**
+
+## One-Sentence Description
+
+A Pygame-based experimental simulator that models and visualizes rocket flight while progressively introducing propulsion, aerodynamics, atmosphere, stability, and control.
+
+## Core Question
+
+How accurately can increasingly realistic rocket-flight behavior be reproduced using a simple, modular 2D physics simulator?
+
+## Primary Purpose
+
+The project is intended to serve as:
+
+1. a physics learning environment,
+2. a software-engineering project,
+3. a digital testbed for future rocket experiments,
+4. and potentially the foundation for a more advanced science-fair investigation.
+
+## Initial Scope
+
+Version 1 models a rocket as a point mass in two dimensions with:
+
+- gravity,
+- finite-duration thrust,
+- configurable launch angle,
+- configurable mass,
+- position and velocity integration,
+- trajectory visualization.
+
+The first version explicitly excludes:
+
+- drag,
+- wind,
+- changing mass,
+- rotation,
+- aerodynamic stability,
+- guidance,
+- sensor simulation.
+
+Those effects will be introduced later as independent milestones.
+
+## Key Technical Principle
+
+The project should not be built as a Pygame animation with physics embedded in rendering code.
+
+Instead:
+
+```text
+Physics engine → state → renderer
+```
+
+This allows the same physics engine to later run automated experiments without graphics.
+
+## Initial User Controls
+
+Suggested controls:
+
+```text
+SPACE   launch / pause
+R       reset
+T       toggle trajectory
+V       toggle velocity vector
+F       toggle force vectors
++ / -   zoom
+ESC     quit
+```
+
+Parameters should initially be edited in configuration rather than through a complex GUI.
+
+## Initial Telemetry
+
+Display:
+
+```text
+Time
+Altitude
+Horizontal position
+Horizontal velocity
+Vertical velocity
+Speed
+Motor state
+```
+
+Later:
+
+```text
+Acceleration
+Mass
+Dynamic pressure
+Mach
+Angle of attack
+CG / CP
+```
+
+## Scientific Value
+
+The simulator becomes scientifically useful when it can answer quantitative questions through controlled experiments.
+
+Examples:
+
+- How does drag coefficient affect apogee?
+- What timestep is necessary for reliable simulation?
+- How much performance changes as propellant mass decreases?
+- What launch angle maximizes altitude under wind?
+- How sensitive are predictions to uncertain aerodynamic parameters?
+
+## Long-Term Vision
+
+A mature version could act as a digital flight laboratory containing:
+
+- simulated rocket dynamics,
+- real motor curves,
+- sensor models,
+- simulated telemetry,
+- flight-control algorithms,
+- Monte Carlo uncertainty analysis,
+- and multi-vehicle experiments.
+
+The long-term goal is not merely to draw a rocket flying across the screen, but to create a reusable environment for testing aerospace ideas before hardware experiments.
diff --git a/docs/RESEARCH_LOG.md b/docs/RESEARCH_LOG.md
new file mode 100644
index 0000000..6fdee0b
--- /dev/null
+++ b/docs/RESEARCH_LOG.md
@@ -0,0 +1,118 @@
+# Research and Experiment Log
+
+## Purpose
+
+Use this file to record important design decisions, physics questions, experiments, unexpected results, and ideas for future investigation.
+
+Each entry should make it possible to reconstruct what was tested and why.
+
+---
+
+## Entry Template
+
+### Date
+
+YYYY-MM-DD
+
+### Question
+
+What are we trying to understand?
+
+### Hypothesis
+
+What do we expect to happen, and why?
+
+### Model / Assumptions
+
+List the assumptions active in this simulation.
+
+Example:
+
+- Constant gravity.
+- No wind.
+- Constant drag coefficient.
+- Point-mass rocket.
+- Fixed launch direction.
+
+### Parameters
+
+```text
+Rocket mass:
+Dry mass:
+Propellant mass:
+Thrust:
+Burn duration:
+Launch angle:
+Drag coefficient:
+Reference area:
+Air density:
+Physics timestep:
+```
+
+### Method
+
+Describe exactly what was simulated or changed.
+
+### Results
+
+Record important values:
+
+```text
+Apogee:
+Maximum speed:
+Maximum Mach:
+Flight time:
+Horizontal range:
+Impact velocity:
+```
+
+### Interpretation
+
+What do the results mean physically?
+
+### Problems / Uncertainty
+
+What assumptions or numerical issues might affect the result?
+
+### Next Experiment
+
+What should be tested next?
+
+---
+
+# Initial Research Questions
+
+Possible early questions:
+
+1. How much does timestep affect predicted apogee?
+2. How much does aerodynamic drag reduce altitude relative to a vacuum model?
+3. How sensitive is apogee to rocket mass?
+4. How sensitive is maximum velocity to motor burn duration?
+5. How does launch angle affect altitude and range?
+6. How much does changing air density with altitude matter for a model rocket?
+7. At what speeds does assuming a constant drag coefficient become inadequate?
+8. How accurately can a simple simulation reproduce published model rocket flight data?
+9. How do uncertainty in drag coefficient and mass affect predicted apogee?
+10. Which sensor measurements would be most useful for estimating the rocket's state in flight?
+
+---
+
+# Design Decisions
+
+Use this section to preserve important architecture decisions.
+
+## Decision 001 — SI Units
+
+All physics calculations use SI units internally. Rendering converts metres to pixels.
+
+## Decision 002 — Fixed Physics Timestep
+
+Physics is updated using a fixed timestep rather than directly using the graphical frame time.
+
+## Decision 003 — Separate Physics and Rendering
+
+The simulation engine must be capable of operating independently of Pygame rendering.
+
+## Decision 004 — Add Physics Incrementally
+
+New effects should be implemented only after the current model has been validated against known results.
diff --git a/docs/VALIDATION.md b/docs/VALIDATION.md
new file mode 100644
index 0000000..8c415ac
--- /dev/null
+++ b/docs/VALIDATION.md
@@ -0,0 +1,219 @@
+# Validation and Testing Plan
+
+## Purpose
+
+A physics simulator is only useful if its output can be trusted. This document defines how the simulation should be checked as features are added.
+
+The guiding principle is:
+
+> Validate simple cases against known answers before trusting complex cases.
+
+---
+
+## 1. Unit Tests
+
+Create automated tests for small physics functions.
+
+Examples:
+
+### Gravity
+
+For a 2 kg rocket:
+
+```text
+F_g = 2 × 9.81 = 19.62 N downward
+```
+
+### Thrust Components
+
+At 90° launch angle:
+
+```text
+F_thrust_x ≈ 0
+F_thrust_y ≈ T
+```
+
+At 0° launch angle:
+
+```text
+F_thrust_x ≈ T
+F_thrust_y ≈ 0
+```
+
+### Drag
+
+Verify that drag:
+
+- is zero at zero speed,
+- points opposite velocity,
+- increases by approximately 4× when speed doubles.
+
+---
+
+## 2. Analytical Projectile Test
+
+Disable thrust after assigning an initial velocity and disable drag.
+
+For constant gravity:
+
+```text
+x(t) = x0 + vx0 t
+
+y(t) = y0 + vy0 t - 0.5 g t²
+```
+
+Compare simulation position against this analytical result.
+
+This is one of the most important early tests.
+
+---
+
+## 3. Vertical Launch Test
+
+Launch at exactly 90° with no drag.
+
+Expected behavior:
+
+- Horizontal displacement should remain approximately zero.
+- Vertical velocity should increase during sufficient powered thrust.
+- After burnout, vertical velocity should decrease linearly under gravity.
+- At apogee, vertical velocity should pass through zero.
+
+---
+
+## 4. Timestep Convergence Test
+
+Run the same simulation using:
+
+```text
+dt = 0.02 s
+dt = 0.01 s
+dt = 0.005 s
+```
+
+Compare:
+
+- apogee,
+- flight time,
+- maximum speed,
+- landing position.
+
+Results should converge as timestep decreases.
+
+If halving `dt` dramatically changes the result, the timestep is too large or the numerical method is inadequate.
+
+---
+
+## 5. FPS Independence Test
+
+Run rendering at different frame rates while keeping physics timestep fixed.
+
+For example:
+
+```text
+30 FPS
+60 FPS
+144 FPS
+```
+
+Final trajectory results should remain nearly identical.
+
+---
+
+## 6. Energy Sanity Check
+
+For a drag-free coast phase, mechanical energy should remain approximately constant:
+
+```text
+E = 0.5 m v² + m g h
+```
+
+Small numerical error is expected.
+
+Large systematic gain or loss indicates an integration problem.
+
+---
+
+## 7. Drag Sanity Checks
+
+With drag enabled:
+
+- Maximum altitude should normally decrease.
+- Mechanical energy should decrease during unpowered flight.
+- Higher drag coefficient should reduce apogee and speed.
+- Larger frontal area should increase drag.
+
+---
+
+## 8. Motor Validation
+
+For thrust-curve motors, compute total impulse:
+
+```text
+I = integral(T dt)
+```
+
+Numerically integrate the loaded thrust curve and compare against published or expected motor impulse.
+
+---
+
+## 9. Regression Tests
+
+When a milestone is completed, save several reference scenarios.
+
+Example:
+
+```text
+Scenario: basic_vertical_v1
+Mass: 1.0 kg
+Thrust: 20 N
+Burn: 1.0 s
+Angle: 90 deg
+Drag: disabled
+```
+
+Record expected approximate:
+
+```text
+apogee
+flight time
+max velocity
+```
+
+Future code changes should not unexpectedly change these values.
+
+---
+
+## 10. Real-World Validation
+
+Only after the mathematical model is internally validated should it be compared with real rocket flight data.
+
+Potential measurements:
+
+- launch mass,
+- motor type,
+- measured altitude,
+- accelerometer data,
+- barometric altitude,
+- GPS trajectory,
+- video-derived ascent time.
+
+Real-world discrepancies can then be used to improve assumptions such as drag coefficient or atmospheric conditions.
+
+---
+
+## Validation Log Template
+
+For each test:
+
+```text
+Test name:
+Date:
+Simulator version/commit:
+Parameters:
+Expected result:
+Observed result:
+Difference:
+Pass/fail:
+Notes:
+```
diff --git a/docs/decisions/decision_01_repository_workflow.md b/docs/decisions/decision_01_repository_workflow.md
new file mode 100644
index 0000000..74b7c64
--- /dev/null
+++ b/docs/decisions/decision_01_repository_workflow.md
@@ -0,0 +1,60 @@
+# Decision 01 — Repository Workflow
+
+**Date:** 2026-08-27
+**Status:** accepted
+
+## Decision
+
+The canonical repository is `https://github.com/eugenelin89/rocketsim.git`. The primary branch is `main`. For an approved task that changes repository files, the normal completion workflow is:
+
+```text
+implement
+→ validate
+→ implementation commit
+→ record the implementation SHA and parent diff in the prompt record
+→ prompt-record commit
+→ push completed commits to origin/main
+```
+
+Routine completion pushes do not require separate conversational approval. Force pushes, history rewriting, destructive Git operations, discarding user work, and committing unrelated work remain prohibited. A push may be omitted only for a specific technical or repository-state blocker, which must be reported while preserving the local commits.
+
+The portable platform baseline requires an isolated Python 3.12 environment with its own pip. On the primary development machine, that environment is the Miniconda environment named `rocketsim`, created with both `python=3.12` and `pip`. It is the only project-environment layer; no `venv` is nested inside it. Other developers may use an equivalent isolated Python 3.12 environment, including standard-library `venv`.
+
+`pyproject.toml` remains the sole package and dependency declaration. Installations use `python -m pip`; Pygame is the runtime dependency, pytest is the development dependency, and the project uses a `src/` package layout.
+
+## Context and problem
+
+The starting directory contained project documentation but was not a Git repository and had no executable Python baseline. The project needs a reproducible environment and an explicit history-and-push workflow before flight code begins.
+
+An initial repository-local `.venv` was created with Homebrew Python 3.12.12 before any commit. Homebrew's bundled `ensurepip` wheel was owned by another local user with restrictive permissions, so pip could not be installed normally. Although `get-pip.py` temporarily recovered that generated environment, the workaround was rejected as the canonical setup. Before the initial commit, the environment policy was corrected to use the project owner's established Miniconda workflow without changing machine-wide Homebrew files.
+
+The older milestone documentation also describes a runnable Pygame window as part of Milestone 0. Prompt 01 is newer and more specific: it limits this task to repository and tooling setup and expressly defers the application loop and flight behavior. This decision applies that narrower scope.
+
+## Options considered
+
+- Use the primary machine's dedicated Miniconda `rocketsim` environment for isolation, Python 3.12, and pip while retaining `pyproject.toml` for all project dependencies.
+- Keep the recovered Homebrew-created `.venv`, which would make a machine-specific permissions workaround part of the primary workflow.
+- Require Conda for every developer, which would unnecessarily reduce portability.
+- Nest a `venv` inside Conda, which would add a redundant environment layer and make interpreter provenance less clear.
+- Build the older Milestone 0 application-loop deliverables now, which would exceed Prompt 01's explicit scope.
+
+## Rationale
+
+The selected baseline matches the primary machine's established environment manager while keeping the repository portable and `pyproject.toml` authoritative. Explicit `python -m pip` and `conda run -n rocketsim python ...` commands make interpreter provenance clear. The two-commit history preserves a reviewable implementation commit while keeping its prompt provenance separate.
+
+## Consequences and tradeoffs
+
+- The primary development machine must use the `rocketsim` Conda environment rather than Conda `base`, Homebrew Python, or a nested `venv`.
+- Other developers remain free to use an equivalent isolated Python 3.12 environment.
+- Conda manages only the environment, Python, and pip; project dependencies remain declared in `pyproject.toml`.
+- Prompt records add repository history and storage overhead because they include implementation diffs.
+- The repository is importable and testable, but it is intentionally not yet runnable as a simulator.
+- Future changes that alter this workflow should supersede this record rather than silently editing its history.
+
+## Related prompt records
+
+- `docs/prompts/prompt_01_platform.md`
+
+## Superseding decision
+
+None.
diff --git a/docs/product/PROJECT_UNDERSTANDING.md b/docs/product/PROJECT_UNDERSTANDING.md
new file mode 100644
index 0000000..964bdaf
--- /dev/null
+++ b/docs/product/PROJECT_UNDERSTANDING.md
@@ -0,0 +1,56 @@
+# Project Understanding
+
+## Purpose and current milestone
+
+This repository is the foundation for a scientifically inspectable 2D model-rocket flight simulator. Pygame will provide interaction and visualization, while explicit, testable equations will define the simulation.
+
+Prompt 01 establishes the Milestone 0 repository and Python tooling baseline only. The package is importable, but no application loop, renderer, simulation state, or flight physics exists yet.
+
+## Implemented repository layout
+
+```text
+rocketsim/
+├── docs/
+│   ├── decisions/       durable project decisions
+│   ├── product/         implementation-oriented project status
+│   └── prompts/         implementation prompts and commit records
+├── src/rocket_sim/      importable Python package
+├── tests/               pytest baseline tests
+├── pyproject.toml       project metadata and dependencies
+└── README.md            developer entry point
+```
+
+The repository intentionally has no speculative physics, rendering, motor, environment, or experiment modules. Those boundaries will emerge from concrete implementation work.
+
+## Python and dependency baseline
+
+- Development requires an isolated Python 3.12 environment with its own pip.
+- The primary development machine uses the Miniconda environment named `rocketsim`, created with both `python=3.12` and `pip`.
+- The Conda environment is the single environment layer; it does not contain a nested `venv`.
+- Other developers may use an equivalent isolated Python 3.12 environment, including standard-library `venv`.
+- `pyproject.toml` is the only project and dependency declaration.
+- Pygame is the sole runtime dependency.
+- pytest is the sole development dependency.
+- Installation uses `python -m pip` so pip provenance matches the selected interpreter.
+- The project uses a `src/` package layout and editable development installation.
+
+## Architecture and scientific constraints
+
+- The physics core must remain independent of Pygame wherever practical; Pygame owns display and input concerns.
+- Physics uses SI units and world coordinates: +x is right, +y is up, and gravity will act in -y.
+- Screen-coordinate inversion belongs only at the rendering boundary.
+- Physics simulation time must remain separate from wall-clock and display time.
+- The first physics implementation will use a documented fixed timestep independent of rendering FPS.
+- Physical effects will be added incrementally and validated against analytical or trusted reference results.
+
+## Current validation
+
+The current pytest test imports `rocket_sim` from the editable installation and verifies its baseline package version. There are no physics tests because no physics is implemented.
+
+## Current non-goals
+
+This milestone does not implement a Pygame window, application loop, rocket state, forces, integration, rendering, telemetry, or any flight behavior. Drag, variable mass, thrust curves, atmosphere, recovery, rotation, stability, guidance, and optimization remain later work.
+
+## Immediate next task
+
+Prompt 02 should implement 2D constant-mass point-flight dynamics with constant gravity and finite-duration constant thrust, together with the minimum application/rendering boundary required to observe it and analytical validation of the motion equations.
diff --git a/pyproject.toml b/pyproject.toml
new file mode 100644
index 0000000..4067323
--- /dev/null
+++ b/pyproject.toml
@@ -0,0 +1,24 @@
+[build-system]
+requires = ["setuptools>=75"]
+build-backend = "setuptools.build_meta"
+
+[project]
+name = "pygame-rocket-simulator"
+version = "0.1.0"
+description = "A staged, validated 2D model-rocket flight simulator."
+readme = "README.md"
+requires-python = ">=3.12,<4"
+dependencies = [
+    "pygame>=2.6,<3",
+]
+
+[project.optional-dependencies]
+dev = [
+    "pytest>=8,<9",
+]
+
+[tool.setuptools.packages.find]
+where = ["src"]
+
+[tool.pytest.ini_options]
+testpaths = ["tests"]
diff --git a/src/rocket_sim/__init__.py b/src/rocket_sim/__init__.py
new file mode 100644
index 0000000..ac3a298
--- /dev/null
+++ b/src/rocket_sim/__init__.py
@@ -0,0 +1,3 @@
+"""Pygame rocket simulator package."""
+
+__version__ = "0.1.0"
diff --git a/tests/test_package.py b/tests/test_package.py
new file mode 100644
index 0000000..a494001
--- /dev/null
+++ b/tests/test_package.py
@@ -0,0 +1,4 @@
+def test_package_import() -> None:
+    import rocket_sim
+
+    assert rocket_sim.__version__ == "0.1.0"
~~~~~~
