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
fixed-step accumulator -> simulation.py lifecycle/events + knot segmentation
            |
            v
propulsion.py curve geometry -> physics.py force/impulse update
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
- one authoritative immutable `ThrustCurve`
- SI-valued defaults, initial conditions, and constant aerodynamic scalars

### `propulsion.py`

- immutable `ThrustSample` and defensively tuple-owned `ThrustCurve`
- sample validation and half-open piecewise-linear interpolation
- exact total, delivered, and interval impulse from curve geometry
- burn duration, average thrust, and peak thrust metrics
- constant-thrust and zero-thrust limiting constructors
- bundled synthetic educational default curve

It contains no Pygame, motor database, file loader, network access, variable mass, or mutable motor state.

### `physics.py`

- gravitational, thrust, and constant-property quadratic-drag equations
- instantaneous thrust from the production curve and fixed world direction
- exact thrust-impulse vector for an interval
- immutable thrust/gravity/drag/net `ForceBreakdown`
- net acceleration from the force sum
- exact-thrust-impulse/start-state-other-force semi-implicit segment update

It does not own wall time, phases, events, or drawing.

### `simulation.py`

- immutable `RocketState` samples and flight phases
- launch, pause/resume, reset, and terminal lifecycle
- fixed-timestep wall-time accumulator
- paused exact single-step through the normal fixed-step path
- exact internal splitting at every crossed thrust knot and burn end
- exact curve thrust impulse plus start-velocity drag on each internal segment
- deterministic interpolation of the first discrete ground crossing
- physics step count and trajectory history

Configuration is the source of constant mass. Every recorded state repeats that value so the invariant is observable.

### `rendering.py`

- world metres and force vectors to screen pixels
- powered/coast trajectory colors, rocket, and educational status drawing
- force-vector overlay with one rendering-only newtons-to-pixels scale
- Physics Inspector formatting for state, forces, parameters, and equations
- production-curve motor timeline, samples, cursor, burnout marker, and metrics
- no mutation of simulation state

### `app.py` and `__main__.py`

- `python -m rocket_sim` entry point
- Pygame initialization and shutdown
- `SPACE`, `RIGHT`, `R`, `F`, `I`, and `ESC` controls
- bounded `run(max_frames=...)` path for dummy-display smoke validation

## Shared force-observability contract

`physics.force_breakdown_n(config, time, velocity)` is the single production source for instantaneous thrust, gravity, drag, and net force. The simulation exposes that breakdown for presentation. Integration separately obtains exact scalar curve impulse through `propulsion.ThrustCurve` and converts it once to a fixed-direction vector; it combines that impulse with gravity and start-velocity drag without double-counting instantaneous thrust.

The renderer receives the configured production `ThrustCurve` for sample positions and calls its public instantaneous-thrust and impulse-backed simulator values. It may map time/thrust to pixels, clamp a clearly labeled motor cursor at burnout, and format values. It does not construct a second curve, interpolate thrust, integrate trapezoids, or mutate motor/simulation state.

READY is a lifecycle state rather than a solved pad-contact equilibrium. The simulation therefore exposes an all-zero inactive breakdown while READY so the inspector's zero acceleration and force sum remain coherent without an invented support force. Powered, coast, and terminal states expose their appropriate instantaneous force breakdown; terminal presentation distinguishes a post-liftoff impact from a no-liftoff initial state.

## Clock contract

Elapsed unpaused display time is accumulated with compensated floating-point summation. The simulation consumes complete fixed `physics_dt_s` intervals and retains only a fractional remainder. It never advances a representably subthreshold interval and has no substep cap that drops elapsed time. Pre-launch, paused, and post-landing calls do not add elapsed time; reset clears the remainder, compensation, and step counter.

No absolute comparison tolerance creates simulation time. Burnout is handled by explicit segment endpoints, not an epsilon-expanded burn interval.

## State and event contract

The flight phases are ready, powered, coast, and landed. Pause is an application lifecycle state layered over the physical powered/coast phase. Powered is the half-open configured motor interval and does not imply that instantaneous thrust must be positive at every time. State acceleration describes the instantaneous force model at the state's resulting time and velocity; it can differ from the average acceleration that produced the segment's velocity change. A state exactly at burnout is coast even if the preceding interval was powered.

Each fixed outer step is partitioned at every strictly crossed curve knot. Every internal segment integrates the curve impulse exactly, reevaluates drag from its own start velocity, updates velocity, then updates position. Internal boundaries may add trajectory samples, but the wall-time accumulator and `physics_step_count` still consume one configured outer step. Curve knots are consequently part of the numerical mesh when drag is active.

Burnout and landing are handled inside the simulation boundary. A post-liftoff terminal landed state is the instant of impact, so pre-burn impact retains time-consistent thrust, drag, and acceleration telemetry. A terminal state with `has_lifted_off=False` instead records an unsupported no-liftoff initial condition and is presented distinctly from impact. Rendering infers no transitions and performs no physical force calculations.

## Learning documentation boundary

`docs/learning/LEARNING_ROCKETRY_WITH_ROCKETSIM.md` is the learner-facing tutorial and interactive laboratory guide. It derives equations from `docs/PHYSICS_MODEL.md`, validation claims from `docs/VALIDATION.md`, and controls from the implemented application. It is reviewed retroactively when physics or educational behavior changes; it is not an independent source of scientific truth.

## Extension limits

Prompt 04 adds the smallest active propulsion boundary: one immutable sampled curve and no general motor-data ecosystem. It does not introduce variable mass, propellant depletion, motor-file import, motor selection, wind, lift, atmosphere variation, experiment frameworks, plugins, databases, ECS, or networking. Later effects should be added one validated physical model at a time without changing the current ownership boundary silently.
