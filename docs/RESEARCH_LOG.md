# Research and Experiment Log

## Purpose

Use this file to record important design decisions, physics questions, experiments, unexpected results, and ideas for future investigation.

Each entry should make it possible to reconstruct what was tested and why.

---

## Entry Template

### Date

YYYY-MM-DD

### Question

What are we trying to understand?

### Hypothesis

What do we expect to happen, and why?

### Model / Assumptions

List the assumptions active in this simulation.

Example:

- Constant gravity.
- No wind.
- Constant drag coefficient.
- Point-mass rocket.
- Fixed launch direction.

### Parameters

```text
Rocket mass:
Dry mass:
Propellant mass:
Thrust:
Burn duration:
Launch angle:
Drag coefficient:
Reference area:
Air density:
Physics timestep:
```

### Method

Describe exactly what was simulated or changed.

### Results

Record important values:

```text
Apogee:
Maximum speed:
Maximum Mach:
Flight time:
Horizontal range:
Impact velocity:
```

### Interpretation

What do the results mean physically?

### Problems / Uncertainty

What assumptions or numerical issues might affect the result?

### Next Experiment

What should be tested next?

---

# Initial Research Questions

Possible early questions:

1. How much does timestep affect predicted apogee?
2. How much does aerodynamic drag reduce altitude relative to a vacuum model?
3. How sensitive is apogee to rocket mass?
4. How sensitive is maximum velocity to motor burn duration?
5. How does launch angle affect altitude and range?
6. How much does changing air density with altitude matter for a model rocket?
7. At what speeds does assuming a constant drag coefficient become inadequate?
8. How accurately can a simple simulation reproduce published model rocket flight data?
9. How do uncertainty in drag coefficient and mass affect predicted apogee?
10. Which sensor measurements would be most useful for estimating the rocket's state in flight?

---

# Design Decisions

Use this section to preserve important architecture decisions.

## Decision 001 — SI Units

All physics calculations use SI units internally. Rendering converts metres to pixels.

## Decision 002 — Fixed Physics Timestep

Physics is updated using a fixed timestep rather than directly using the graphical frame time.

## Decision 003 — Separate Physics and Rendering

The simulation engine must be capable of operating independently of Pygame rendering.

## Decision 004 — Add Physics Incrementally

New effects should be implemented only after the current model has been validated against known results.

---

## 2026-08-28 — Quadratic-drag timestep convergence

### Question

Does numerical error against the vertical constant-property quadratic-drag solution decrease at first order as the fixed timestep is halved?

### Hypothesis

Because the velocity-dependent force is evaluated at the start of each semi-implicit Euler segment, global velocity and position error should decrease approximately in proportion to `dt` for a stable case.

### Model / assumptions

- Constant mass `2 kg`.
- Constant gravity `8 m/s^2`.
- Still air with `rho=2 kg/m^3`, `Cd=1`, and `A=1 m^2`.
- Vertical fall from rest at `100 m`.
- No thrust and no ground contact during the `1 s` comparison.

These values give `k=1 kg/m` and terminal speed `4 m/s`. The continuous references are `vy=-4 tanh(2)` and `y=100-2 ln(cosh(2))` at `t=1 s`.

### Method and results

Production simulations at `dt=0.02`, `0.01`, and `0.005 s` were compared directly with the closed form.

| `dt` (s) | velocity error (m/s) | altitude error (m) |
| ---: | ---: | ---: |
| 0.020 | 0.0148671763 | 0.0578690164 |
| 0.010 | 0.0074621397 | 0.0289350701 |
| 0.005 | 0.0037378878 | 0.0144675983 |

The velocity-error ratios were approximately `1.992` and `1.996`; altitude-error ratios were approximately `2.000` and `2.000`.

### Interpretation and uncertainty

The measured ratios support first-order convergence for this stable nonlinear case. They do not establish stability for arbitrary speed, aerodynamic parameters, or timestep, and they do not validate the constant-property drag approximation against a real rocket. Future physical effects should retain independent analytical or limiting evidence rather than using a fine numerical run as their only oracle.
