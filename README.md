# Pygame Rocket Physics Simulator

A staged 2D model-rocket flight simulator built with Python and Pygame. The project emphasizes explicit assumptions, reproducible runs, analytical validation, and a clean boundary between physics and visualization.

## Current status

Prompt 01 establishes the Milestone 0 repository and tooling baseline. The `rocket_sim` package is installable and tested, but no Pygame application loop or rocket-flight physics is implemented yet.

The next milestone will add 2D constant-mass flight with gravity and finite-duration constant thrust. Drag, variable mass, wind, atmosphere, recovery, rotation, stability, guidance, and control remain out of scope until later milestones.

## Development setup

Python 3.12 and an isolated environment are required. On the primary Miniconda-based development machine, create and use the dedicated `rocketsim` environment:

```bash
conda create -n rocketsim python=3.12 pip
conda activate rocketsim
python --version
python -m pip --version
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest
```

For automated work on that machine, make the interpreter explicit without relying on shell activation:

```bash
conda run -n rocketsim python -m pytest
```

Conda supplies isolation, Python, and pip; `pyproject.toml` remains the canonical project and dependency declaration. Use `python -m pip` so pip belongs to the selected interpreter. Do not use Conda `base` for project dependencies, and do not create a nested `venv` inside the `rocketsim` environment.

On other machines, a conventional isolated Python 3.12 environment, including standard-library `venv`, is acceptable when it works normally. Install the same project and development dependencies from `pyproject.toml` with `python -m pip install -e ".[dev]"`.

## Repository layout

```text
src/rocket_sim/     importable application package
tests/              pytest test suite
docs/product/       current implementation understanding
docs/prompts/       prompt and implementation history
docs/decisions/     durable project decisions
```

Subsystem directories will be introduced only when a concrete implementation milestone needs them.

## Documentation

- [`Pygame_Rocket_Simulator_Project_Context.md`](Pygame_Rocket_Simulator_Project_Context.md) — canonical product, scientific, and milestone context
- [`docs/product/PROJECT_UNDERSTANDING.md`](docs/product/PROJECT_UNDERSTANDING.md) — current implementation-oriented status
- [`docs/PHYSICS_MODEL.md`](docs/PHYSICS_MODEL.md) — planned model assumptions and equations
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — architecture direction
- [`docs/VALIDATION.md`](docs/VALIDATION.md) — validation strategy
- [`docs/MILESTONES.md`](docs/MILESTONES.md) — staged development plan
- [`docs/RESEARCH_LOG.md`](docs/RESEARCH_LOG.md) — research questions and experiment log

## Definition of success

The simulator should become a trustworthy experimental sandbox rather than merely a plausible animation. Results must remain understandable, testable, and traceable to their equations, units, numerical method, and configuration.
