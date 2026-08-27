# Development Milestones

## Strategy

Build the simulator in small, testable stages. Each milestone should introduce one major source of physical complexity while keeping previous behavior working.

---

## Milestone 0 — Project Skeleton

### Goal

Create a runnable Pygame application with a clean project structure.

### Deliverables

- Pygame window opens.
- Main loop runs.
- Simulation and renderer are separate modules.
- Basic configuration file exists.
- Test directory exists.

### Completion Check

The project launches without errors and can display a static rocket on a ground line.

---

## Milestone 1 — Powered Point-Mass Flight

### Physics

- Constant gravity.
- Constant mass.
- Constant thrust during a fixed burn interval.
- No drag.
- Fixed launch angle.

### Features

- Launch/reset controls.
- Rocket trajectory.
- Elapsed time.
- Position and velocity display.
- Automatic transition from powered flight to coast.
- Flight ends when rocket returns to ground.

### Validation

Compare no-thrust ballistic motion with analytical projectile equations.

### Completion Check

Simulation results are stable and approximately independent of graphical FPS.

---

## Milestone 2 — Aerodynamic Drag

### Physics

Add:

```text
F_drag = 0.5 rho C_d A v²
```

### Features

- Configurable drag coefficient.
- Configurable reference area.
- Optional drag force vector display.

### Validation

Confirm that:

- drag always opposes velocity,
- drag is zero when velocity is zero,
- drag scales approximately with `v²`,
- altitude is lower with drag enabled than without drag.

---

## Milestone 3 — Variable Mass and Motor Model

### Physics

- Dry mass.
- Propellant mass.
- Propellant depletion.
- Changing total mass.

### Features

- Remaining propellant display.
- Motor state: idle / burning / burned out.

### Validation

Confirm total rocket mass never drops below dry mass.

---

## Milestone 4 — Real Thrust Curves

### Goal

Load sampled motor thrust data from a file.

### Features

- CSV motor data.
- Linear interpolation.
- Total impulse calculation.
- Motor curve visualization or debug plot.

### Validation

Numerically integrate thrust curve and compare with expected total impulse.

---

## Milestone 5 — Atmosphere and Mach Number

### Physics

- Density decreases with altitude.
- Speed of sound estimate.
- Mach number calculation.

### Features

- Display Mach number.
- Display maximum Mach reached.

### Validation

Compare atmospheric values with a trusted reference at several altitudes.

---

## Milestone 6 — Wind and Recovery

### Physics

- Horizontal wind.
- Relative air velocity.
- Parachute drag.

### Features

- Parachute deployment altitude/time condition.
- Landing location.
- Drift distance.

### Validation

Confirm stronger wind produces larger horizontal drift during descent.

---

## Milestone 7 — Rotational Dynamics

### Physics

Introduce:

- rocket orientation,
- angular velocity,
- torque,
- moment of inertia,
- angle of attack.

### Features

- Rocket sprite rotates physically.
- Attitude data display.

### Validation

Start with simple torque-only test cases before aerodynamic stability.

---

## Milestone 8 — Aerodynamic Stability

### Physics

- Center of gravity.
- Center of pressure.
- Restoring aerodynamic moment.
- Approximate stability margin.

### Features

- Display CG and CP.
- Show whether configuration is nominally stable.

### Validation

A statically stable rocket should tend to align with its relative airflow after small disturbances.

---

## Milestone 9 — Experiment Mode

### Features

- Run without real-time graphics.
- Sweep launch parameters.
- Export CSV results.
- Compare apogee, maximum velocity, range, and flight time.
- Reproduce runs from saved configuration.

### Example Experiment

Vary launch angle from 70° to 90° and measure:

```text
apogee
horizontal drift
maximum speed
flight duration
```

---

## Milestone 10 — Advanced Research Extensions

Possible directions:

- Active thrust-vector control.
- Fin control.
- Sensor simulation.
- State estimation.
- Kalman filtering.
- Autonomous apogee detection.
- Optimal control.
- Monte Carlo uncertainty analysis.
- Multi-rocket simulations.
- Swarm behavior.
- Reinforcement learning controllers.

These are deliberately outside the initial scope.
