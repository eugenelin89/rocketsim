# Project Understanding

## Purpose and current milestone

RocketSim is a scientifically validated, interactive rocketry-learning simulator whose educational course evolves with the implemented model. It remains a trustworthy, understandable 2D learning model rather than an engineering-grade launch predictor. Prompt 04 adds piecewise-linear sampled thrust and motor impulse while establishing the permanent Living Rocketry Course.

## Implemented model

The rocket is a constant-mass point in a 2D flat world. Internally, all quantities use SI units, +x points right, +y points upward, and the ground is `y = 0`.

The forces are:

- constant gravity `(0, -m g)`;
- time-varying sampled thrust `T(t)(cos(theta), sin(theta))` during the curve's half-open burn interval; and
- quadratic drag `-0.5 rho Cd A |v_air| v_air`.

Air is stationary, so rocket velocity relative to air is numerically equal to ground-frame rocket velocity. Density, drag coefficient, and reference area are fixed for a complete run. The default educational constants are `rho = 1.225 kg/m^3`, `Cd = 0.75`, and `A = 0.01 m^2`; they are not calibration of a particular rocket. Setting any one of these scalars to zero recovers the validated Prompt 02 no-drag model through the same force path.

One immutable `ThrustCurve` is the propulsion source of truth. Its final sample defines burn duration; its exact polyline area defines total and delivered impulse. The default curve is self-authored synthetic data with `1.05 s` duration, `17.58 N*s` total impulse, `28 N` peak thrust, and `16.742857... N` average thrust. It is not measured or certified motor data. The rocket mass and thrust direction remain constant.

## Implemented structure

```text
src/rocket_sim/config.py       immutable Vector2 and validated run constants
src/rocket_sim/propulsion.py   sampled curve, interpolation, and impulse metrics
src/rocket_sim/physics.py      thrust, gravity, drag, force breakdown, and Euler segment
src/rocket_sim/simulation.py   lifecycle, fixed outer clock, knot segments, and history
src/rocket_sim/rendering.py    force arrows, Inspector, and motor timeline
src/rocket_sim/app.py          Pygame loop and educational controls
src/rocket_sim/__main__.py     python -m rocket_sim entry point
```

The physics modules do not import Pygame. Rendering consumes `Simulation.current_forces`, the same immutable `ForceBreakdown` calculated by the production physics layer. Display scaling and visibility toggles cannot alter physical values or state.

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

The Pygame application shows powered and coast trajectory segments, current phase and burnout status, thrust/gravity/drag/net-force arrows, numerical force components and magnitudes, motor/aerodynamic parameters, and the implemented equations. A motor timeline plots production samples, current motor cursor, peak, and burnout. READY explicitly reports forces as inactive alongside zero stored acceleration; it does not invent a pad normal force.

Controls are SPACE launch/pause/resume, RIGHT single-step while paused, R reset, F force overlay, I Physics Inspector, and ESC exit.

## Validation status

The suite preserves Prompts 02–03 through constant/zero curves and adds independent sample validation, interpolation, impulse, default metrics, knot segmentation, burn-end, impulse–momentum, active-drag force, independent-RK4 convergence, sampled-thrust reset/FPS, paused stepping, rendering isolation, Inspector/timeline sourcing, and bounded SDL smoke evidence.

## Current limits

Density, `Cd`, and effective reference area are constant and direction-independent. There is no wind, altitude-varying atmosphere, lift, compressibility, Mach/Reynolds dependence, variable mass, propellant depletion, measured motor import, pad/rail contact, recovery, collision dynamics, rotation, stability, guidance, control, plotting, experiment export, calibration, or uncertainty model. Semi-implicit Euler is explicit with respect to drag and can become unstable for sufficiently large timestep or speed; no artificial clamp conceals that limitation.

The point-mass result is not equivalent to 3D flight dynamics and is not an engineering or safety prediction. Prompt 05 has not begun.
