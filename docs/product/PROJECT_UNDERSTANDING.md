# Project Understanding

## Purpose and current milestone

RocketSim is a scientifically validated, interactive rocketry-learning simulator whose educational course evolves with the implemented model. It remains a trustworthy, understandable 2D learning model rather than an engineering-grade launch predictor. Prompt 06 adds Sandbox/Mission mode choice, completed-flight results, objectives, deterministic scoring/stars, target visualization, retry, and in-memory progression above the unchanged validated Prompt 05 simulation.

## Implemented model

The rocket is a constant-mass point in a 2D flat world. Internally, all quantities use SI units, +x points right, +y points upward, and the ground is `y = 0`.

The forces are:

- constant gravity `(0, -m g)`;
- time-varying sampled thrust `T(t)(cos(theta), sin(theta))` during the curve's half-open burn interval; and
- quadratic drag `-0.5 rho Cd A |v_air| v_air`.

Air is stationary, so rocket velocity relative to air is numerically equal to ground-frame rocket velocity. Density, drag coefficient, and reference area are fixed for a complete run. The default educational constants are `rho = 1.225 kg/m^3`, `Cd = 0.75`, and `A = 0.01 m^2`; they are not calibration of a particular rocket. Setting any one of these scalars to zero recovers the validated Prompt 02 no-drag model through the same force path.

One immutable `ThrustCurve` is the propulsion source of truth. Its final sample defines burn duration; its exact polyline area defines total and delivered impulse. The default curve is self-authored synthetic data with `1.05 s` duration, `17.58 N*s` total impulse, `28 N` peak thrust, and `16.742857... N` average thrust. It is not measured or certified motor data. A learner may select mass and fixed thrust direction before a run; both remain constant throughout that run. The UI neither edits nor scales the motor.

## Implemented structure

```text
src/rocket_sim/config.py       immutable Vector2 and validated run constants
src/rocket_sim/setup.py        typed actions and educational config adjustments
src/rocket_sim/propulsion.py   sampled curve, interpolation, and impulse metrics
src/rocket_sim/physics.py      thrust, gravity, drag, force breakdown, and Euler segment
src/rocket_sim/simulation.py   lifecycle, fixed outer clock, knot segments, and history
src/rocket_sim/missions.py     terminal result metrics and explicit mission evaluation
src/rocket_sim/game.py         Pygame-independent view/progression/session state
src/rocket_sim/rendering.py    setup, mission, force, Inspector, and timeline presentation
src/rocket_sim/app.py          Pygame loop and shared keyboard/mouse/game action dispatch
src/rocket_sim/__main__.py     python -m rocket_sim entry point
```

The physics, setup, missions, and game-session modules do not import Pygame. Rendering consumes `Simulation.current_forces`, the same immutable `ForceBreakdown` calculated by the production physics layer. Display scaling, target geometry, hit-testing, scoring, and visibility toggles cannot alter physical values or state. `Simulation.config` is getter-only; whole-config replacement is accepted only in READY and atomically rebuilds the initial state and run bookkeeping.

## Numerical and event semantics

- Every fixed outer step is split at all crossed thrust knots.
- Every internal segment integrates represented thrust impulse exactly, applies constant gravity and drag from segment-start velocity, then updates velocity before position.
- Drag makes true continuous acceleration velocity-dependent, so Prompt 02's constant-acceleration position-error identity applies only when drag is disabled.
- The display loop supplies elapsed wall time to a compensated accumulator; only complete fixed timesteps advance the model.
- A step spanning burnout is divided at the exact half-open burn boundary. The coast substep recomputes drag from the burnout velocity.
- Curve knots are part of the active-drag numerical mesh; exact motor impulse does not imply an exact trajectory.
- Recorded acceleration and displayed forces are instantaneous values recalculated from the resulting state's time and velocity, including exact burnout and interpolated impact states.
- Ground return remains deterministic interpolation of the first descending discrete crossing after liftoff, not an exact collision solve.
- A paused RIGHT-arrow command advances exactly one normal configured fixed step, keeps the simulation paused, and preserves fractional accumulator time unless the step lands.

## Educational presentation

The Pygame application shows a pre-launch setup panel, powered and coast trajectory segments, current phase and burnout status, thrust/gravity/drag/net-force arrows, numerical force components and magnitudes, motor/selected parameters, and the implemented equations. A motor timeline plots production samples, current motor cursor, peak, and burnout. READY explicitly reports forces as inactive alongside zero stored acceleration; it does not invent a pad normal force.

The setup panel exposes mass, fixed thrust direction in degrees, `Cd`, effective reference area, constant air density, and constant gravity. Edits and Restore Defaults are READY-only. The sampled motor and timestep are read-only. The fixed-direction guide uses the configured radians and is explicitly not attitude. Keyboard and mouse use one typed-action dispatcher: SPACE or the primary button launches/pauses/resumes; R or Reset Flight rebuilds READY run state while preserving setup; Restore Defaults creates an exact production default config; RIGHT, F, I, and ESC retain their established behavior.

Sandbox preserves that complete laboratory. Mission Mode adds five explicit missions with a brief, allowed-control allow-list, fixed mission values, live objective state, world-coordinate target, and terminal results. `FlightResult` captures the completed run's immutable configuration and recorded numerical metrics. `NO_LIFTOFF` has no fabricated ground-contact position or impact speed. Scores are 500 points for mandatory completion plus up to 500 transparent performance points; stars require success and use 500/750/900 thresholds. Retry preserves allowed choices, Mission Defaults restores the mission baseline, and sequential progression is memory-only.

## Validation status

The suite preserves Prompts 02–05 and adds terminal result provenance/nonmutation, independently checked recorded metrics, exact objective and scoring boundaries, mission restriction bypass checks, per-mission successful/failing production runs, countdown non-advancement, exact Sandbox/Mission post-ignition equivalence, state-machine/retry/progression checks, target/HUD/result sourcing, complete-view rendering nonmutation, and bounded SDL evidence.

## Current limits

Each selected physical scalar is constant during one run. UI bounds are pedagogical controls, not physical limits. Some valid choices produce NO LIFTOFF in the no-pad/no-rail boundary model, and zero gravity can produce a flight that never returns. There is no wind, altitude-varying atmosphere, lift, compressibility, Mach/Reynolds dependence, variable mass, propellant depletion, measured motor import or editing, pad/rail contact, recovery, collision dynamics, rotation, stability, guidance, control, automatic run comparison, disk persistence, networking, 2.5D/3D, plotting, experiment export, calibration, or uncertainty model. Semi-implicit Euler is explicit with respect to drag and can become unstable for sufficiently large timestep or speed; no artificial clamp conceals that limitation.

The point-mass result is not equivalent to 3D flight dynamics and is not an engineering or safety prediction. A mission's “landing” is the existing interpolated first descending ground contact, not recovery, bounce, structural survival, or a real-world safety assessment.
