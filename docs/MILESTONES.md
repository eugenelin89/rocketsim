# Development Milestones

## Strategy

Add one major physical effect at a time, preserve validated earlier behavior, and keep display concerns outside the physics core.

## Milestone 0 — Repository and application foundation

Status: complete.

- installable Python 3.12 package
- isolated Conda development workflow
- Pygame runtime and pytest development dependencies
- documentation, prompt archive, decisions, and repository policy
- runnable module entry point and separated simulation/rendering modules

The application portion was completed alongside Milestone 1 so it could display real, tested state rather than placeholder physics.

## Milestone 1 — Powered point-mass flight

Status: complete in Prompt 02.

Physics:

- constant gravity
- constant mass
- constant thrust on a finite half-open burn interval
- fixed launch angle in world coordinates
- no drag

Features:

- launch, pause/resume, reset, and exit controls
- trajectory and SI telemetry
- powered-to-coast transition
- post-liftoff ground return and terminal landing
- fixed timestep independent of rendering FPS

Validation:

- independent gravity, powered, and piecewise analytical cases
- Euler ordering and known position-error checks
- non-aligned burnout split
- first-order timestep convergence
- reset determinism and 30/60/144 FPS partition independence
- bounded headless application smoke

## Milestone 2 — Aerodynamic drag

Status: complete in Prompt 03.

Physics:

- still-air quadratic drag
- constant density, drag coefficient, and effective reference area
- exact zero-speed and zero-parameter limiting behavior
- shared thrust/gravity/drag/net force breakdown
- drag applied during powered flight, coast ascent, and descent

Features:

- Physics Inspector with SI state, forces, parameters, and equations
- same-scale thrust, gravity, drag, and net-force arrows
- powered/coast trajectory distinction
- force and Inspector visibility toggles
- exact paused single-step through the normal physics path

Validation:

- independent force magnitude, direction, quadrant, reversal, and `v^2` cases
- vertical quadratic-drag analytical fall and terminal velocity
- first-order timestep convergence at `0.02`, `0.01`, and `0.005 s`
- exact Prompt 02 reduction when density, `Cd`, or area is zero
- active-drag burnout, reset, and FPS-independence regressions
- renderer sourcing and non-mutation evidence

## Milestone 3 — Sampled motor thrust curves and Living Rocketry Course

Status: complete in Prompt 04.

Physics:

- immutable sampled thrust data and piecewise-linear interpolation
- burn duration derived from the final curve sample
- exact total, delivered, and interval motor impulse
- fixed world thrust direction and constant rocket mass
- exact thrust-impulse velocity contribution on every knot-bounded segment
- gravity plus segment-start-velocity quadratic drag retained
- constant-thrust and zero-thrust limiting curves

Features:

- current, peak, and average thrust plus delivered/total impulse in the Physics Inspector
- production-data motor timeline with samples, cursor, peak, and burnout marker
- paused single-step updates across thrust knots while remaining paused
- permanent Living Rocketry Course and retroactive update policy
- persistent propulsion and learning reviewers

Validation:

- independent curve validation, interpolation, and trapezoidal metrics
- one/multiple-knot and nonaligned-burn-end literal oracles
- zero-gravity/zero-drag impulse–momentum agreement
- Prompt 03 constant-thrust, zero-thrust, drag, lifecycle, timing, and rendering regressions
- active-drag convergence against an independent RK4 reference
- sampled-thrust FPS independence and deterministic reset
- Inspector/timeline production sourcing, non-mutation, and SDL smoke evidence

The default is a synthetic educational curve, not measured motor data. Variable mass and propellant depletion remain unimplemented.

## Standing cross-cutting requirement — Learning Course impact review

Every future approved milestone must identify whether it changes physics, equations, numerical interpretation, phases/events, Inspector information, educational visualization, controls, or experiments. Applicable chapters of `docs/learning/LEARNING_ROCKETRY_WITH_ROCKETSIM.md` must be revised and the complete course reviewed before that milestone is complete. This requirement may revise earlier chapters rather than merely append a new one.

## Later candidate milestones

The following remain unimplemented and require separate approval and validation:

1. variable mass and propellant depletion
2. validated real-motor data ingestion
3. atmospheric density and speed of sound
4. wind and recovery
5. rotational dynamics and aerodynamic stability
6. headless experiment export and reproducibility tooling
7. calibrated real-flight comparison and uncertainty analysis

Each candidate milestone includes a Living Course impact review as a completion gate.

Advanced guidance, control, optimization, machine learning, and multi-vehicle work are research directions only. They must not be inferred from the current 2D point-mass model.
