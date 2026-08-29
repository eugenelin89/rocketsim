# Pygame Rocket Physics Simulator

RocketSim is a scientifically inspectable 2D model-rocket flight simulator and interactive rocketry-learning laboratory built with Python and Pygame. Its current milestone models a constant-mass point rocket under gravity, a sampled time-varying thrust curve, and constant-property quadratic aerodynamic drag in still air. A fixed outer physics timestep remains independent of display FPS.

Start with the [Living Rocketry Course](docs/learning/LEARNING_ROCKETRY_WITH_ROCKETSIM.md) to learn the implemented physics through prediction, observation, and hands-on simulator experiments.

## Current status

Milestone 3 is implemented. The runnable application includes a Physics Inspector, force-vector overlay, and motor thrust timeline while a Pygame-independent physics core remains the sole owner of force calculations, integration, event transitions, and history.

Implemented physics:

- SI units and world coordinates with +x right and +y up
- constant mass and constant gravity
- immutable sampled thrust with piecewise-linear `T(t)` at a fixed world angle
- exact total/delivered motor impulse for the represented curve
- burn duration derived from the final sample and a half-open burn endpoint
- constant density, drag coefficient, and reference area
- still-air quadratic drag `F_drag = -0.5 rho Cd A |v_air| v_air`
- fixed `0.01 s` physics timestep and semi-implicit Euler integration
- exact internal split at every crossed thrust knot and burnout
- deterministic ground-return termination after liftoff

The propulsion default is self-authored synthetic educational data, not measured or certified motor data. It has `1.05 s` duration, `17.58 N*s` total impulse, `28 N` peak thrust, and `16.742857... N` average thrust. The aerodynamic defaults are educational constants, not calibration of a real vehicle: `rho = 1.225 kg/m^3`, `Cd = 0.75`, and `A = 0.01 m^2`.

Variable mass, propellant depletion, motor-data import, launch-pad/rail contact, wind, atmosphere variation, lift, recovery, rotation, stability, guidance, and control are not implemented.

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

The inspector shows flight and motor phase, burnout status, state, acceleration, constant mass, current/peak/average thrust, burn-time progress, delivered/total impulse, all force vectors and magnitudes, aerodynamic constants, and implemented equations. The timeline plots the exact production samples and current motor-time cursor; after burnout its endpoint-clamped cursor is labeled as such. Thrust, gravity, drag, and net-force arrows use the same rendering-only scale and are sourced from the force breakdown used by the simulator.

The default vertical configuration uses a `1 kg` rocket and begins at `12 N`, above its `9.81 N` weight. The original zero-at-ignition educational curve is tested only away from the ground boundary because RocketSim does not model a launch-pad support force.

## Repository layout

```text
.codex/agents/         persistent read-only specialist reviewer definitions
src/rocket_sim/        configuration, physics, lifecycle, rendering, and app code
tests/                 headless physics, numerical, lifecycle, and rendering tests
docs/learning/         learner-facing Living Rocketry Course
docs/product/          current implementation understanding
docs/prompts/          prompt and implementation history
docs/decisions/        durable scientific and workflow decisions
```

See [docs/PHYSICS_MODEL.md](docs/PHYSICS_MODEL.md) for the exact equations and limits, [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for ownership boundaries, and [docs/VALIDATION.md](docs/VALIDATION.md) for the evidence strategy.
