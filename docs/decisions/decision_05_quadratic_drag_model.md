# Decision 05: Constant-property quadratic drag model

- Date: 2026-08-28
- Status: accepted
- Related prompt: `docs/prompts/prompt_03_drag.md`
- Supersedes: none

## Decision

Prompt 03 adds one aerodynamic effect: constant-property quadratic drag on the existing constant-mass 2D point rocket. The surrounding air is stationary, so rocket velocity relative to air is numerically equal to ground-frame rocket velocity. Air density, dimensionless drag coefficient, and one direction-independent effective reference area remain constant for the whole run.

For air-relative velocity `v_air`:

```text
k = 0.5 rho Cd A
F_drag = -k |v_air| v_air
F_net = F_thrust + F_gravity + F_drag
a = F_net / m
```

At zero speed, density, `Cd`, or area, drag is exactly zero. Integration retains fixed-step semi-implicit Euler: evaluate forces from segment-start time and velocity, update velocity, then update position from the new velocity. A step crossing burnout remains split exactly, and drag is recomputed from the burnout velocity for the coast substep. Recorded forces and acceleration are recalculated from each resulting state's time and velocity.

The principal nonlinear reference is vertical fall from rest:

```text
v_terminal = sqrt(2 m g / (rho Cd A))
vy(t) = -v_terminal tanh(g t / v_terminal)
y(t) = y0 - (v_terminal^2 / g) ln(cosh(g t / v_terminal))
```

## Context and problem

Prompt 02 deliberately excluded drag so gravity and thrust could be validated under constant acceleration. The next educational step needs an energy-removing velocity-dependent force that is vector-correct, inspectable, and independently testable without introducing atmosphere variation, wind, orientation, or real-vehicle calibration.

The Physics Inspector also needs the exact component forces. One immutable `ForceBreakdown` therefore exposes thrust, gravity, drag, and net force to integration and presentation without introducing a general force-plugin framework.

## Options considered

- Constant-property quadratic drag in still air, the approved single-effect milestone.
- Linear drag, which is analytically convenient but does not match Prompt 03's required `v^2` law.
- Altitude-varying atmosphere or constant wind, both explicitly deferred because either would add another physical effect.
- A drag-enable boolean, rejected because any zero aerodynamic scalar already supplies the exact Prompt 02 limiting case.
- A higher-order or implicit integrator, rejected because the established semi-implicit Euler method remains understandable and demonstrates measured first-order convergence for the selected stable case.
- Phase-specific ascent/descent drag signs, rejected in favor of one vector equation that works in every quadrant.

## Rationale

The selected model is the smallest scientifically coherent aerodynamic extension. It preserves SI units, constant mass, the half-open thrust interval, exact burnout segmentation, deterministic event handling, and rendering independence. The dot-product identity `F_drag dot v_air = -k |v_air|^3` establishes that drag removes energy for positive parameters. The analytical fall and terminal-speed equilibrium provide independent nonlinear checks.

Defaults `rho=1.225 kg/m^3`, `Cd=0.75`, and `A=0.01 m^2` give the default 1 kg rocket a vertical gravity-only terminal speed of approximately `46.21 m/s`, producing visible but modest drag at `dt=0.01 s`. These are educational constants, not measured vehicle data.

## Consequences and tradeoffs

- Drag acts during powered flight, coast ascent, and descent and naturally reverses with velocity.
- Setting density, `Cd`, or area to zero exactly recovers the Prompt 02 force path.
- Acceleration is no longer constant with active drag, so Prompt 02's closed-form Euler position-error identity is limited to the zero-drag constant-acceleration case.
- Semi-implicit Euler is explicit with respect to drag. Large `k |v| dt / m` can cause unphysical reversal or instability; no artificial clamp masks this limitation.
- Constant density at all altitudes, constant `Cd`, and direction-independent area are simplified assumptions. The model omits wind, lift, compressibility, Mach/Reynolds effects, attitude, and aerodynamic stability.
- READY exposes inactive zero forces to presentation rather than claiming an unmodeled pad-support equilibrium. A post-liftoff landed state exposes forces at the instant of interpolated impact, but no further motion is integrated. An unsupported ground start is labeled as a terminal no-liftoff initial state rather than impact.
- The result is an educational point-mass approximation, not a calibrated real-flight or safety predictor.

## Related prompt records

- `docs/prompts/prompt_03_drag.md`

## Superseding decision

None.
