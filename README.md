# Pygame Rocket Physics Simulator

RocketSim is a scientifically inspectable 2D model-rocket flight simulator built with Python and Pygame. Its first flight milestone implements a constant-mass point rocket under constant gravity and finite-duration constant thrust, with a fixed physics timestep that is independent of display FPS.

## Current status

Milestone 1 is implemented. The runnable application displays the flight trajectory and live telemetry while a Pygame-independent physics core owns forces, integration, event transitions, and history.

Implemented physics:

- SI units and world coordinates with +x right and +y up
- constant mass and constant gravity
- constant thrust at a fixed world angle for `0 <= t < burn_time`
- fixed `0.01 s` physics timestep and semi-implicit Euler integration
- exact substep split when a fixed step crosses burnout
- deterministic ground-return termination after liftoff

Drag, variable mass, sampled thrust curves, wind, atmosphere, recovery, rotation, stability, guidance, and control are not implemented.

## Setup and validation

Python 3.12 and an isolated environment are required. On the primary development machine:

```bash
conda create -n rocketsim python=3.12 pip
conda run -n rocketsim python -m pip install -e ".[dev]"
conda run -n rocketsim python -m pytest
```

`pyproject.toml` is the canonical package and dependency declaration. Do not install the project into Conda `base`, a system interpreter, or a nested virtual environment.

## Run the simulator

```bash
conda run -n rocketsim python -m rocket_sim
```

Controls:

- `SPACE`: launch, pause, or resume
- `R`: reset the complete deterministic run
- `ESC`: exit

Telemetry shows phase, simulation time, position, velocity, speed, acceleration, mass, and current thrust. The default vertical configuration uses a `1 kg` rocket, `20 N` thrust, a `1 s` burn, and `9.81 m/s²` gravity, so thrust exceeds weight during launch.

## Repository layout

```text
.codex/agents/         persistent read-only specialist reviewer definitions
src/rocket_sim/        configuration, physics, lifecycle, rendering, and app code
tests/                 headless physics, numerical, lifecycle, and rendering tests
docs/product/          current implementation understanding
docs/prompts/          prompt and implementation history
docs/decisions/        durable scientific and workflow decisions
```

See [docs/PHYSICS_MODEL.md](docs/PHYSICS_MODEL.md) for the exact equations and limits, [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for ownership boundaries, and [docs/VALIDATION.md](docs/VALIDATION.md) for the evidence strategy.
