# Pygame Rocket Physics Simulator

RocketSim is a scientifically inspectable 2D model-rocket flight simulator built with Python and Pygame. Its current milestone models a constant-mass point rocket under gravity, finite-duration constant thrust, and constant-property quadratic aerodynamic drag in still air. A fixed physics timestep remains independent of display FPS.

## Current status

Milestone 2 is implemented. The runnable application includes a Physics Inspector and force-vector overlay while a Pygame-independent physics core remains the sole owner of force calculations, integration, event transitions, and history.

Implemented physics:

- SI units and world coordinates with +x right and +y up
- constant mass and constant gravity
- constant thrust at a fixed world angle for `0 <= t < burn_time`
- constant density, drag coefficient, and reference area
- still-air quadratic drag `F_drag = -0.5 rho Cd A |v_air| v_air`
- fixed `0.01 s` physics timestep and semi-implicit Euler integration
- exact substep split when a fixed step crosses burnout
- deterministic ground-return termination after liftoff

The aerodynamic defaults are educational constants, not calibration of a real vehicle: `rho = 1.225 kg/m^3`, `Cd = 0.75`, and `A = 0.01 m^2`. Variable mass, sampled thrust curves, wind, atmosphere variation, lift, recovery, rotation, stability, guidance, and control are not implemented.

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
- `RIGHT ARROW`: advance exactly one physics timestep while paused
- `R`: reset the complete deterministic run
- `F`: show or hide force vectors
- `I`: show or hide the Physics Inspector
- `ESC`: exit

The inspector shows phase, burnout status, state, acceleration, mass, all force vectors and magnitudes, the aerodynamic constants, and the implemented equations. Thrust, gravity, drag, and net-force arrows use the same rendering-only scale and are sourced from the force breakdown used by the simulator. The default vertical configuration uses a `1 kg` rocket, `20 N` thrust, a `1 s` burn, and `9.81 m/s^2` gravity, so thrust exceeds weight during launch.

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
