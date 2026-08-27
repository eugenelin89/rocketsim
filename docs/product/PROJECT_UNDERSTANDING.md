# Project Understanding

## Purpose and current milestone

This repository is the foundation for a scientifically inspectable 2D model-rocket flight simulator. Pygame will provide interaction and visualization, while explicit, testable equations will define the simulation.

Prompt 01 establishes the Milestone 0 repository and Python tooling baseline only. The package is importable, but no application loop, renderer, simulation state, or flight physics exists yet.

## Implemented repository layout

```text
rocketsim/
├── docs/
│   ├── decisions/       durable project decisions
│   ├── product/         implementation-oriented project status
│   └── prompts/         implementation prompts and commit records
├── src/rocket_sim/      importable Python package
├── tests/               pytest baseline tests
├── pyproject.toml       project metadata and dependencies
└── README.md            developer entry point
```

The repository intentionally has no speculative physics, rendering, motor, environment, or experiment modules. Those boundaries will emerge from concrete implementation work.

## Python and dependency baseline

- Development requires an isolated Python 3.12 environment with its own pip.
- The primary development machine uses the Miniconda environment named `rocketsim`, created with both `python=3.12` and `pip`.
- The Conda environment is the single environment layer; it does not contain a nested `venv`.
- Other developers may use an equivalent isolated Python 3.12 environment, including standard-library `venv`.
- `pyproject.toml` is the only project and dependency declaration.
- Pygame is the sole runtime dependency.
- pytest is the sole development dependency.
- Installation uses `python -m pip` so pip provenance matches the selected interpreter.
- The project uses a `src/` package layout and editable development installation.

## Architecture and scientific constraints

- The physics core must remain independent of Pygame wherever practical; Pygame owns display and input concerns.
- Physics uses SI units and world coordinates: +x is right, +y is up, and gravity will act in -y.
- Screen-coordinate inversion belongs only at the rendering boundary.
- Physics simulation time must remain separate from wall-clock and display time.
- The first physics implementation will use a documented fixed timestep independent of rendering FPS.
- Physical effects will be added incrementally and validated against analytical or trusted reference results.

## Current validation

The current pytest test imports `rocket_sim` from the editable installation and verifies its baseline package version. There are no physics tests because no physics is implemented.

## Current non-goals

This milestone does not implement a Pygame window, application loop, rocket state, forces, integration, rendering, telemetry, or any flight behavior. Drag, variable mass, thrust curves, atmosphere, recovery, rotation, stability, guidance, and optimization remain later work.

## Immediate next task

Prompt 02 should implement 2D constant-mass point-flight dynamics with constant gravity and finite-duration constant thrust, together with the minimum application/rendering boundary required to observe it and analytical validation of the motion equations.
