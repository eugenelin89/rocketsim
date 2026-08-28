# Software Architecture

## Implemented boundary

The simulator separates scientific state evolution from Pygame presentation:

```text
Pygame events + frame time
            |
            v
app.py -> Simulation.advance_elapsed()
            |
            v
fixed-step accumulator -> simulation.py lifecycle/events
            |
            v
physics.py forces + semi-implicit Euler
            |
            v
immutable RocketState history
            |
            v
rendering.py world transform + drawing + telemetry
```

`config.py`, `physics.py`, and `simulation.py` do not import Pygame. `app.py` owns window creation, input, the display clock, and the outer loop. `rendering.py` owns pixels, fonts, drawing, and the +y-up to +y-down transform.

## Module responsibilities

### `config.py`

- immutable, validated `SimulationConfig`
- neutral immutable `Vector2`
- SI-valued defaults and initial conditions

### `physics.py`

- gravitational and thrust force equations
- half-open burn predicate
- net acceleration
- one constant-acceleration semi-implicit Euler segment

It does not own wall time, phases, events, or drawing.

### `simulation.py`

- immutable `RocketState` samples and flight phases
- launch, pause/resume, reset, and terminal lifecycle
- fixed-timestep wall-time accumulator
- exact burnout split and deterministic ground-crossing handling
- physics step count and trajectory history

Configuration is the source of constant mass. Every recorded state repeats that value so the invariant is observable.

### `rendering.py`

- world metres to screen pixels
- ground, trajectory, rocket, and telemetry drawing
- no mutation of simulation state

### `app.py` and `__main__.py`

- `python -m rocket_sim` entry point
- Pygame initialization and shutdown
- `SPACE`, `R`, and `ESC` controls
- bounded `run(max_frames=...)` path for dummy-display smoke validation

## Clock contract

Elapsed unpaused display time is accumulated with compensated floating-point summation. The simulation consumes complete fixed `physics_dt_s` intervals and retains only a fractional remainder. It never advances a representably subthreshold interval and has no substep cap that drops elapsed time. Pre-launch, paused, and post-landing calls do not add elapsed time; reset clears the remainder, compensation, and step counter.

No absolute comparison tolerance creates simulation time. Burnout is handled by explicit segment endpoints, not an epsilon-expanded burn interval.

## State and event contract

The flight phases are ready, powered, coast, and landed. Pause is an application lifecycle state layered over the physical powered/coast phase. State acceleration describes the instantaneous force model at the state's resulting time, so a state exactly at burnout is coast even if the preceding interval was powered.

Burnout and landing are handled inside the simulation boundary. A terminal state is the instant of impact, so pre-burn impact retains time-consistent thrust and acceleration telemetry. Rendering infers no transitions and performs no force calculations.

## Extension limits

Prompt 02 deliberately does not introduce motor interfaces, atmosphere interfaces, data loaders, experiment frameworks, plugins, databases, ECS, networking, or abstractions for unimplemented milestones. Later effects should be added one validated physical model at a time without changing the current ownership boundary silently.
