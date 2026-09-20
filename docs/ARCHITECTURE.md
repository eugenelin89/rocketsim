# Software Architecture

## Implemented boundary

The simulator separates scientific state evolution, Pygame-independent game evaluation, and Pygame presentation:

```text
Pygame keyboard/mouse events + frame time
            |
            v
app.py shared typed-action dispatcher
       |                    |
       | READY setup        | flight clock
       v                    v
setup.py -> validated config -> Simulation.advance_elapsed()
            |
            v
fixed-step accumulator -> simulation.py lifecycle/events + knot segmentation
            |
            v
propulsion.py curve geometry -> physics.py force/impulse update
            |
            v
immutable RocketState history
       |                         |
       | completed run           | live observation
       v                         v
missions.py FlightResult -> objective evaluation -> score/stars
       |
       v
game.py session/view/progression
       |
       v
rendering.py world transform + Sandbox/Mission drawing + telemetry
```

`config.py`, `physics.py`, `simulation.py`, `missions.py`, and `game.py` do not import Pygame. `app.py` owns window creation, input, the display clock, and the outer loop. `rendering.py` owns pixels, fonts, drawing, target/HUD presentation, and the +y-up to +y-down transform.

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

### `setup.py`

- typed application actions shared by keyboard and mouse paths
- the six learner-facing parameter specifications, UI ranges, increments, units, and formatting
- degree display conversion for the internally radian-valued fixed thrust direction
- immutable `dataclasses.replace` configuration rebuilding that preserves every unedited field, including exact `ThrustCurve` identity and `physics_dt_s`

It contains no Pygame and does not own simulation lifecycle or a second parameter store. Its ranges constrain only the educational controls; the broader validated `SimulationConfig` API remains available to headless use.

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
- getter-only active configuration and atomic whole-config replacement while READY

Configuration is the source of constant mass. Every recorded state repeats that value so the invariant is observable. An accepted READY replacement rebuilds the initial state, singleton trajectory, accumulator, and lifecycle bookkeeping together. Running, paused, coast, and landed configurations cannot be replaced; Reset Flight preserves the selected configuration while rebuilding run state.

### `missions.py`

- immutable terminal `FlightResult` extracted from exactly one completed `Simulation`
- explicit `NO_LIFTOFF` versus post-liftoff `LANDED` outcome
- captured immutable run configuration plus recorded apogee, speed, acceleration, drag, contact, and time metrics
- five explicit immutable missions, inclusive objective rules, score components, and star thresholds
- no Pygame, lifecycle mutation, alternate physics calculation, scripting engine, or persistence

Landing position and impact speed are absent for `NO_LIFTOFF`; they are never zero-filled. Apogee and extrema are maxima over recorded numerical states. Impact speed is total pre-contact ground-frame speed, not impact deceleration. Mission evaluation consumes only the `FlightResult`, so scoring cannot accidentally use a later READY configuration.

### `game.py`

- mode/mission/brief/flight/results view state
- presentation-only countdown that leaves simulation time and history unchanged before ignition
- mission setup allow-list enforcement through the existing validated adjustment and READY replacement paths
- one-time terminal result extraction/evaluation, in-memory best scores, and sequential unlocks
- retry preserving the selected mission configuration and mission reset restoring the mission base configuration

`GameSession` owns no force, integrator, trajectory, event, motor, or timestep calculation. From ignition onward it supplies elapsed time to an ordinary `Simulation` exactly as Sandbox does.

### `rendering.py`

- world metres and force vectors to screen pixels
- powered/coast trajectory colors, rocket, and educational status drawing
- force-vector overlay with one rendering-only newtons-to-pixels scale
- Physics Inspector formatting for state, forces, parameters, and equations
- production-curve motor timeline, samples, cursor, burnout marker, and metrics
- setup panel drawing, exact mouse hitbox geometry, disabled-state presentation, and fixed-direction preview
- mode selection, mission brief/selection/results views, mission HUD, and target geometry transformed by the shared `world_to_screen`
- no mutation of simulation state

### `app.py` and `__main__.py`

- `python -m rocket_sim` entry point
- Pygame initialization and shutdown
- one typed-action dispatcher for keyboard and mouse behavior
- `SPACE`, `RIGHT`, `R`, `F`, `I`, and `ESC` controls plus mouse setup, primary, reset, and restore-default actions
- bounded `run(max_frames=...)` path for dummy-display smoke validation

## Mission evaluation boundary

The implemented pipeline is:

```text
validated Simulation
        -> immutable FlightResult
        -> Mission.evaluate(...)
        -> objective outcomes + score + stars
        -> GameSession progression
        -> Pygame presentation
```

Mission targets are presentation geometry in world metres. They never feed back into the simulation. Difficulty changes exposed controls, objectives, hints, and scoring only. There is no target steering, gravity/thrust/drag adjustment, position snapping, timestep change, or false terminal result.

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

## Pre-launch laboratory contract

The UI reads all six displayed values directly from `Simulation.config`. The renderer returns typed actions but never performs configuration replacement. The application dispatches an adjustment by creating a new validated configuration and requesting a READY-only atomic replacement from `Simulation`. Restore Defaults requests an exact new `SimulationConfig()`; Reset Flight uses the existing selected config. The motor/impulse and physics timestep are shown from production config but read-only, no timestep control is exposed, and there is no launchability shortcut separate from the production ground-admission path.

The direction preview is rendering-only and uses the exact configured radians. It carries no force magnitude, leaves READY forces inactive, and does not rotate the point marker or represent attitude.

## Extension limits

Prompt 06 adds evaluation and presentation above existing validated parameters, not a new physical effect or run-comparison framework. It does not introduce variable mass, propellant depletion, motor-file import, motor selection/editing, wind, lift, atmosphere variation, recovery/contact dynamics, persistence/export, 2.5D/3D, plots, plugins, databases, ECS, or networking. Later effects should be added one validated physical model at a time without changing the current ownership boundary silently.
