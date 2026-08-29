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
physics.py force breakdown + semi-implicit Euler
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
- SI-valued defaults, initial conditions, and constant aerodynamic scalars

### `physics.py`

- gravitational, thrust, and constant-property quadratic-drag equations
- half-open burn predicate
- immutable thrust/gravity/drag/net `ForceBreakdown`
- net acceleration from the force sum
- one force-frozen semi-implicit Euler segment

It does not own wall time, phases, events, or drawing.

### `simulation.py`

- immutable `RocketState` samples and flight phases
- launch, pause/resume, reset, and terminal lifecycle
- fixed-timestep wall-time accumulator
- paused exact single-step through the normal fixed-step path
- exact burnout split with drag reevaluation
- deterministic ground-crossing handling
- physics step count and trajectory history

Configuration is the source of constant mass. Every recorded state repeats that value so the invariant is observable.

### `rendering.py`

- world metres and force vectors to screen pixels
- powered/coast trajectory colors, rocket, and educational status drawing
- force-vector overlay with one rendering-only newtons-to-pixels scale
- Physics Inspector formatting for state, forces, parameters, and equations
- no mutation of simulation state

### `app.py` and `__main__.py`

- `python -m rocket_sim` entry point
- Pygame initialization and shutdown
- `SPACE`, `RIGHT`, `R`, `F`, `I`, and `ESC` controls
- bounded `run(max_frames=...)` path for dummy-display smoke validation

## Shared force-observability contract

`physics.force_breakdown_n(config, time, velocity)` is the single production source for thrust, gravity, drag, and net force. The simulation uses its net vector for acceleration and exposes the current breakdown for presentation. The renderer receives those vectors and may only scale, label, color, or hide them; it does not import the drag helper or reproduce the aerodynamic equation.

READY is a lifecycle state rather than a solved pad-contact equilibrium. The simulation therefore exposes an all-zero inactive breakdown while READY so the inspector's zero acceleration and force sum remain coherent without an invented support force. Powered, coast, and terminal states expose their appropriate instantaneous force breakdown; terminal presentation distinguishes a post-liftoff impact from a no-liftoff initial state.

## Clock contract

Elapsed unpaused display time is accumulated with compensated floating-point summation. The simulation consumes complete fixed `physics_dt_s` intervals and retains only a fractional remainder. It never advances a representably subthreshold interval and has no substep cap that drops elapsed time. Pre-launch, paused, and post-landing calls do not add elapsed time; reset clears the remainder, compensation, and step counter.

No absolute comparison tolerance creates simulation time. Burnout is handled by explicit segment endpoints, not an epsilon-expanded burn interval.

## State and event contract

The flight phases are ready, powered, coast, and landed. Pause is an application lifecycle state layered over the physical powered/coast phase. State acceleration describes the instantaneous force model at the state's resulting time and velocity, so a state exactly at burnout is coast even if the preceding interval was powered. A step split at burnout calls the force path independently for the powered and coast segments, so the latter uses updated burnout velocity for drag.

Burnout and landing are handled inside the simulation boundary. A post-liftoff terminal landed state is the instant of impact, so pre-burn impact retains time-consistent thrust, drag, and acceleration telemetry. A terminal state with `has_lifted_off=False` instead records an unsupported no-liftoff initial condition and is presented distinctly from impact. Rendering infers no transitions and performs no physical force calculations.

## Extension limits

Prompt 03 deliberately adds no atmosphere or aerodynamic plugin interface: three constant scalars and one vector equation are sufficient. It does not introduce motor interfaces, wind, lift, data loaders, experiment frameworks, plots, plugins, databases, ECS, networking, or abstractions for unimplemented milestones. Later effects should be added one validated physical model at a time without changing the current ownership boundary silently.
