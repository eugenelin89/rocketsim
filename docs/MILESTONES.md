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

Status: not started. It is outside Prompt 02.

When separately approved, this milestone may add quadratic drag with explicit density, drag coefficient, reference area, and air-relative velocity. It will require direction, zero-speed, `v²` scaling, analytical/limiting-case, and timestep-sensitivity evidence. No drag placeholder exists in the current implementation.

## Later candidate milestones

The following remain unimplemented and require separate approval and validation:

1. variable mass and propellant depletion
2. sampled real-motor thrust curves and total impulse
3. atmospheric density and speed of sound
4. wind and recovery
5. rotational dynamics and aerodynamic stability
6. headless experiment export and reproducibility tooling
7. calibrated real-flight comparison and uncertainty analysis

Advanced guidance, control, optimization, machine learning, and multi-vehicle work are research directions only. They must not be inferred from the current 2D point-mass model.
