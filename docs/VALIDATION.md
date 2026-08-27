# Validation and Testing Plan

## Purpose

A physics simulator is only useful if its output can be trusted. This document defines how the simulation should be checked as features are added.

The guiding principle is:

> Validate simple cases against known answers before trusting complex cases.

---

## 1. Unit Tests

Create automated tests for small physics functions.

Examples:

### Gravity

For a 2 kg rocket:

```text
F_g = 2 × 9.81 = 19.62 N downward
```

### Thrust Components

At 90° launch angle:

```text
F_thrust_x ≈ 0
F_thrust_y ≈ T
```

At 0° launch angle:

```text
F_thrust_x ≈ T
F_thrust_y ≈ 0
```

### Drag

Verify that drag:

- is zero at zero speed,
- points opposite velocity,
- increases by approximately 4× when speed doubles.

---

## 2. Analytical Projectile Test

Disable thrust after assigning an initial velocity and disable drag.

For constant gravity:

```text
x(t) = x0 + vx0 t

y(t) = y0 + vy0 t - 0.5 g t²
```

Compare simulation position against this analytical result.

This is one of the most important early tests.

---

## 3. Vertical Launch Test

Launch at exactly 90° with no drag.

Expected behavior:

- Horizontal displacement should remain approximately zero.
- Vertical velocity should increase during sufficient powered thrust.
- After burnout, vertical velocity should decrease linearly under gravity.
- At apogee, vertical velocity should pass through zero.

---

## 4. Timestep Convergence Test

Run the same simulation using:

```text
dt = 0.02 s
dt = 0.01 s
dt = 0.005 s
```

Compare:

- apogee,
- flight time,
- maximum speed,
- landing position.

Results should converge as timestep decreases.

If halving `dt` dramatically changes the result, the timestep is too large or the numerical method is inadequate.

---

## 5. FPS Independence Test

Run rendering at different frame rates while keeping physics timestep fixed.

For example:

```text
30 FPS
60 FPS
144 FPS
```

Final trajectory results should remain nearly identical.

---

## 6. Energy Sanity Check

For a drag-free coast phase, mechanical energy should remain approximately constant:

```text
E = 0.5 m v² + m g h
```

Small numerical error is expected.

Large systematic gain or loss indicates an integration problem.

---

## 7. Drag Sanity Checks

With drag enabled:

- Maximum altitude should normally decrease.
- Mechanical energy should decrease during unpowered flight.
- Higher drag coefficient should reduce apogee and speed.
- Larger frontal area should increase drag.

---

## 8. Motor Validation

For thrust-curve motors, compute total impulse:

```text
I = integral(T dt)
```

Numerically integrate the loaded thrust curve and compare against published or expected motor impulse.

---

## 9. Regression Tests

When a milestone is completed, save several reference scenarios.

Example:

```text
Scenario: basic_vertical_v1
Mass: 1.0 kg
Thrust: 20 N
Burn: 1.0 s
Angle: 90 deg
Drag: disabled
```

Record expected approximate:

```text
apogee
flight time
max velocity
```

Future code changes should not unexpectedly change these values.

---

## 10. Real-World Validation

Only after the mathematical model is internally validated should it be compared with real rocket flight data.

Potential measurements:

- launch mass,
- motor type,
- measured altitude,
- accelerometer data,
- barometric altitude,
- GPS trajectory,
- video-derived ascent time.

Real-world discrepancies can then be used to improve assumptions such as drag coefficient or atmospheric conditions.

---

## Validation Log Template

For each test:

```text
Test name:
Date:
Simulator version/commit:
Parameters:
Expected result:
Observed result:
Difference:
Pass/fail:
Notes:
```
